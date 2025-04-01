# src/main.py
import logging

from .config import (
    BASE_URL, DOWNLOAD_DIR, ZIP_FILEPATH, LINK_SELECTOR,
    LINK_TEXT_KEYWORDS, LINK_SUFFIX, REQUEST_TIMEOUT
)

from .core.use_cases.download_use_case import DownloadUseCase

from .adapters.http_gateway import RequestsHttpGateway
from .adapters.html_parser import BeautifulSoupHtmlParser
from .adapters.file_downloader import RequestsFileDownloader
from .adapters.archive_manager import ZipArchiveManager
from .adapters.file_manager import FileSystemManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run():
    """Configures and runs the application."""
    logging.info("Setting up application dependencies...")

    http_gateway = RequestsHttpGateway()
    html_parser = BeautifulSoupHtmlParser()
    file_downloader = RequestsFileDownloader()
    archive_manager = ZipArchiveManager()
    file_manager = FileSystemManager()

    download_use_case = DownloadUseCase(
        http_gateway=http_gateway,
        html_parser=html_parser,
        file_downloader=file_downloader,
        archive_manager=archive_manager,
        file_manager=file_manager,
    )

    logging.info("Executing the main use case...")
    try:
        download_use_case.execute(
            url=BASE_URL,
            download_dir=DOWNLOAD_DIR,
            zip_filepath=ZIP_FILEPATH,
            selector=LINK_SELECTOR,
            keywords=LINK_TEXT_KEYWORDS,
            suffix=LINK_SUFFIX,
            timeout=REQUEST_TIMEOUT
        )
        logging.info("Use case execution completed.")
    except Exception as e:
        logging.exception(f"An unexpected error occurred during the main execution flow: {e}")

if __name__ == "__main__":
    run()