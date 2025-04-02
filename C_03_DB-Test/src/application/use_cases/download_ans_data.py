import logging
from typing import List
from urllib.parse import urljoin
import requests

from src.application.ports import (
    FileSystem,
    FileDownloader,
    HtmlParser,
    ZipExtractor,
)
from src.application.dto import DownloadConfig

logger = logging.getLogger(__name__)

class DownloadAnsDataUseCase:
    """Orchestrates the downloading and extraction of accounting data and operator information"""
    
    def __init__(
        self,
        file_system: FileSystem,
        file_downloader: FileDownloader,
        html_parser: HtmlParser,
        zip_extractor: ZipExtractor,
    ):
        """Initialize with required dependencies"""
        self._fs = file_system          # Handles file system operations
        self._downloader = file_downloader  # Downloads files from URLs
        self._parser = html_parser      # Parses HTML to find download links
        self._extractor = zip_extractor  # Extracts ZIP archives

    def execute(self, config: DownloadConfig) -> bool:
        """Main execution method that runs the complete workflow"""
        logger.info("--- Starting Data Download Use Case ---")
        try:
            # 1. Prepare directories
            self._create_directories(config)

            # 2. Download operators CSV (non-critical)
            op_success = self._download_operators_csv(config)
            if not op_success:
                logger.warning("Operators CSV download failed. Continuing with accounting data...")

            # 3. Download and extract accounting data (critical)
            acc_success = self._download_and_extract_accounting_data(config)

            logger.info("--- Finished Data Download Use Case ---")
            return acc_success  # Main success indicator

        except Exception as e:
            logger.exception(f"Unexpected error during download process: {e}")
            return False

    def _create_directories(self, config: DownloadConfig) -> None:
        """Creates all required directories if they don't exist"""
        logger.info("Creating necessary data directories...")
        dirs_to_create = [
            config.data_dir,         # Root data directory
            config.accounting_dir,   # For accounting statements
            config.zips_dir,         # For downloaded ZIP files
            config.csvs_dir,         # For extracted CSV files
            config.operators_dir,    # For operator data
        ]
        for dir_path in dirs_to_create:
            self._fs.create_directories(dir_path)
        logger.info("Data directories created (or already exist).")

    def _download_operators_csv(self, config: DownloadConfig) -> bool:
        """Downloads the operators CSV file"""
        logger.info("--- Starting Operators CSV Download ---")
        success = self._downloader.download(
            config.operators_csv_url,  # Source URL
            config.operators_csv_path   # Destination path
        )
        if success:
            logger.info("Operators CSV downloaded successfully.")
        else:
            logger.error("Operators CSV download failed.")
        logger.info("--- Finished Operators CSV Download ---")
        return success

    def _get_accounting_zip_urls(self, config: DownloadConfig) -> List[str]:
        """Finds all accounting ZIP file URLs for specified years"""
        all_zip_urls = []
        logger.info("Fetching accounting ZIP file URLs...")
        
        for year in config.years_to_download:
            # Build URL for each year's directory
            year_directory_url = urljoin(config.base_accounting_url, f"{year}/")
            logger.debug(f"Checking URL for year {year}: {year_directory_url}")
            
            try:
                # Fetch HTML content
                response = requests.get(year_directory_url, timeout=30)
                response.raise_for_status()
                
                # Find ZIP file links in HTML
                year_zip_urls = self._parser.find_links_ending_with(
                    year_directory_url,  # Base URL for relative links
                    response.text,       # HTML content
                    ".zip"              # Target file extension
                )
                all_zip_urls.extend(year_zip_urls)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch or parse {year_directory_url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error finding ZIP links at {year_directory_url}: {e}")

        if not all_zip_urls:
            logger.warning("No accounting ZIP URLs found for the specified years.")
        else:
            logger.info(f"Found {len(all_zip_urls)} total accounting ZIP URLs.")
        return all_zip_urls

    def _download_and_extract_accounting_data(self, config: DownloadConfig) -> bool:
        """Downloads and extracts all accounting ZIP files"""
        logger.info("--- Starting Accounting Statements Download & Extraction ---")
        
        # 1. Find all ZIP file URLs
        zip_urls = self._get_accounting_zip_urls(config)
        if not zip_urls:
            return False

        # 2. Process each ZIP file
        success_downloads = 0
        failed_downloads = 0
        success_extractions = 0
        failed_extractions = 0

        logger.info(f"Attempting to download {len(zip_urls)} ZIP files...")
        for zip_url in zip_urls:
            try:
                # Extract filename from URL
                filename = zip_url.split('/')[-1]
                if not filename.lower().endswith('.zip'):
                    logger.warning(f"Skipping URL with unexpected format: {zip_url}")
                    continue

                # Download the ZIP file
                zip_save_path = config.zips_dir / filename
                if self._downloader.download(zip_url, zip_save_path):
                    success_downloads += 1
                    
                    # Extract the downloaded ZIP
                    if self._extractor.extract(zip_save_path, config.csvs_dir):
                        success_extractions += 1
                    else:
                        failed_extractions += 1
                else:
                    failed_downloads += 1
                    
            except Exception as e:
                logger.error(f"Error processing accounting URL {zip_url}: {e}")
                failed_downloads += 1

        # 3. Report results
        logger.info(f"Download Summary: {success_downloads} succeeded, {failed_downloads} failed.")
        logger.info(f"Extraction Summary: {success_extractions} succeeded, {failed_extractions} failed.")
        logger.info("--- Finished Accounting Statements Download & Extraction ---")

        # Consider successful if at least one extraction worked
        return success_extractions > 0