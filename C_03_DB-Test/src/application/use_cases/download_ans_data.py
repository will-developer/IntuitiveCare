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
    def __init__(
        self,
        file_system: FileSystem,
        file_downloader: FileDownloader,
        html_parser: HtmlParser,
        zip_extractor: ZipExtractor,
    ):
        self._fs = file_system
        self._downloader = file_downloader
        self._parser = html_parser
        self._extractor = zip_extractor

    def execute(self, config: DownloadConfig) -> bool:
        logger.info("--- Starting Data Download Use Case ---")
        try:
            self._create_directories(config)

            op_success = self._download_operators_csv(config)
            if not op_success:
                logger.warning("Operators CSV download failed. Continuing with accounting data...")

            acc_success = self._download_and_extract_accounting_data(config)

            logger.info("--- Finished Data Download Use Case ---")
            return acc_success

        except Exception as e:
            logger.exception(f"An unexpected error occurred during the download process: {e}")
            return False

    def _create_directories(self, config: DownloadConfig) -> None:
        logger.info("Creating necessary data directories...")
        dirs_to_create = [
            config.data_dir,
            config.accounting_dir,
            config.zips_dir,
            config.csvs_dir,
            config.operators_dir,
        ]
        for dir_path in dirs_to_create:
            self._fs.create_directories(dir_path)
        logger.info("Data directories created (or already exist).")

    def _download_operators_csv(self, config: DownloadConfig) -> bool:
        logger.info("--- Starting Operators CSV Download ---")
        success = self._downloader.download(
            config.operators_csv_url, config.operators_csv_path
        )
        if success:
            logger.info("Operators CSV downloaded successfully.")
        else:
            logger.error("Operators CSV download failed.")
        logger.info("--- Finished Operators CSV Download ---")
        return success

    def _get_accounting_zip_urls(self, config: DownloadConfig) -> List[str]:
        all_zip_urls = []
        logger.info("Fetching accounting ZIP file URLs...")
        for year in config.years_to_download:
            year_directory_url = urljoin(config.base_accounting_url, f"{year}/")
            logger.debug(f"Checking URL for year {year}: {year_directory_url}")
            try:
                response = requests.get(year_directory_url, timeout=30)
                response.raise_for_status()
                year_zip_urls = self._parser.find_links_ending_with(
                    year_directory_url, response.text, ".zip"
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
        logger.info("--- Starting Accounting Statements Download & Extraction ---")
        zip_urls = self._get_accounting_zip_urls(config)
        if not zip_urls:
            return False

        success_downloads = 0
        failed_downloads = 0
        success_extractions = 0
        failed_extractions = 0

        logger.info(f"Attempting to download {len(zip_urls)} ZIP files...")
        for zip_url in zip_urls:
            try:
                filename = zip_url.split('/')[-1]
                if not filename.lower().endswith('.zip'):
                    logger.warning(f"Skipping URL with unexpected format: {zip_url}")
                    continue

                zip_save_path = config.zips_dir / filename

                if self._downloader.download(zip_url, zip_save_path):
                    success_downloads += 1
                    if self._extractor.extract(zip_save_path, config.csvs_dir):
                        success_extractions += 1
                    else:
                        failed_extractions += 1
                else:
                    failed_downloads += 1
            except Exception as e:
                logger.error(f"Error processing accounting URL {zip_url}: {e}")
                failed_downloads += 1

        logger.info(f"Download Summary: {success_downloads} succeeded, {failed_downloads} failed.")
        logger.info(f"Extraction Summary: {success_extractions} succeeded, {failed_extractions} failed.")
        logger.info("--- Finished Accounting Statements Download & Extraction ---")

        return success_extractions > 0