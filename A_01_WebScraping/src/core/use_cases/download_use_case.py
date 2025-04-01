import logging
from typing import List
from ..ports.gateways import (
    HttpGateway, HtmlParser, FileDownloader, ArchiveManager, FileManager
)

class DownloadUseCase:
    def __init__(
        self,
        http_gateway: HttpGateway,
        html_parser: HtmlParser,
        file_downloader: FileDownloader,
        archive_manager: ArchiveManager,
        file_manager: FileManager,
    ):
        # Initialize all required dependencies (gateways)
        self._http_gateway = http_gateway  # For HTTP requests
        self._html_parser = html_parser    # For parsing HTML
        self._file_downloader = file_downloader  # For downloading files
        self._archive_manager = archive_manager  # For creating zip archives
        self._file_manager = file_manager  # For file system operations

    def execute(
        self,
        url: str,
        download_dir: str,
        zip_filepath: str,
        selector: str,
        keywords: List[str],
        suffix: str,
        timeout: int
    ) -> None:
        
        # Start the download process
        logging.info(f"Starting use case: Download Anexos from {url}")

        # Step 1: Get HTML content from URL
        html_content = self._http_gateway.get_content(url, timeout)
        if not html_content:
            logging.error("Aborting use case: Failed to fetch page content.")
            return

        # Step 2: Find PDF links in the HTML content
        pdf_links = self._html_parser.find_links(
            html_content, url, selector, keywords, suffix
        )
        if not pdf_links:
            logging.warning("Aborting use case: No matching PDF links found.")
            return
        logging.info(f"Found {len(pdf_links)} links to process.")

        # Step 3: Ensure download directory exists
        if not self._file_manager.ensure_directory(download_dir):
            logging.error("Aborting use case: Failed to ensure download directory exists.")
            return

        # Step 4: Download all PDF files
        downloaded_filenames = []
        failed_downloads = 0
        logging.info(f"Starting download of {len(pdf_links)} files...")

        for link in pdf_links:
            filename = self._file_manager.get_filename_from_url(link, suffix)
            if self._file_downloader.download(link, download_dir, filename, timeout):
                downloaded_filenames.append(filename)  # Track successful downloads
            else:
                failed_downloads += 1  # Track failed downloads

        logging.info(f"Download summary: {len(downloaded_filenames)} succeeded, {failed_downloads} failed.")

        # Step 5: Process downloaded files
        if downloaded_filenames:
            # Create zip archive if downloads succeeded
            if self._archive_manager.create_archive(download_dir, zip_filepath, downloaded_filenames):
                # Remove original files after successful zip creation
                self._file_manager.remove_files(download_dir, downloaded_filenames)
            else:
                logging.error("Zip archive creation failed. Original files were not removed.")
        elif failed_downloads > 0:
            logging.warning("Skipping zip creation as some downloads failed.")
        else:
            logging.info("No files were successfully downloaded, skipping zip creation.")

        logging.info("Use case execution finished.")