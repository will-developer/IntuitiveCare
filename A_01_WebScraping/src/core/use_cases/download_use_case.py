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
        self._http_gateway = http_gateway
        self._html_parser = html_parser
        self._file_downloader = file_downloader
        self._archive_manager = archive_manager
        self._file_manager = file_manager

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
        
        logging.info(f"Starting use case: Download Anexos from {url}")

        html_content = self._http_gateway.get_content(url, timeout)
        if not html_content:
            logging.error("Aborting use case: Failed to fetch page content.")
            return

        pdf_links = self._html_parser.find_links(
            html_content, url, selector, keywords, suffix
        )
        if not pdf_links:
            logging.warning("Aborting use case: No matching PDF links found.")
            return
        logging.info(f"Found {len(pdf_links)} links to process.")

        if not self._file_manager.ensure_directory(download_dir):
            logging.error("Aborting use case: Failed to ensure download directory exists.")
            return

        downloaded_filenames = []
        failed_downloads = 0
        logging.info(f"Starting download of {len(pdf_links)} files...")

        for link in pdf_links:
            filename = self._file_manager.get_filename_from_url(link, suffix)
            if self._file_downloader.download(link, download_dir, filename, timeout):
                downloaded_filenames.append(filename)
            else:
                failed_downloads += 1

        logging.info(f"Download summary: {len(downloaded_filenames)} succeeded, {failed_downloads} failed.")

        if downloaded_filenames:
            if self._archive_manager.create_archive(download_dir, zip_filepath, downloaded_filenames):
                self._file_manager.remove_files(download_dir, downloaded_filenames)
            else:
                logging.error("Zip archive creation failed. Original files were not removed.")
        elif failed_downloads > 0:
            logging.warning("Skipping zip creation as some downloads failed.")
        else:
            logging.info("No files were successfully downloaded, skipping zip creation.")

        logging.info("Use case execution finished.")