import logging

# Import configuration settings from config module
from .config import (
    BASE_URL, DOWNLOAD_DIR, ZIP_FILEPATH, LINK_SELECTOR,
    LINK_TEXT_KEYWORDS, LINK_SUFFIX, REQUEST_TIMEOUT
)

# Import the main use case class
from .core.use_cases.download_use_case import DownloadUseCase

# Import all the adapter implementations
from .adapters.http_gateway import RequestsHttpGateway
from .adapters.html_parser import BeautifulSoupHtmlParser
from .adapters.file_downloader import RequestsFileDownloader
from .adapters.archive_manager import ZipArchiveManager
from .adapters.file_manager import FileSystemManager

# Configure basic logging settings (format and level)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run():
    """Configures and runs the application."""
    logging.info("Setting up application dependencies...")

    # Initialize all concrete implementations of the gateways/adapters
    http_gateway = RequestsHttpGateway()  # For making HTTP requests
    html_parser = BeautifulSoupHtmlParser()  # For parsing HTML content
    file_downloader = RequestsFileDownloader()  # For downloading files
    archive_manager = ZipArchiveManager()  # For creating zip archives
    file_manager = FileSystemManager()  # For file system operations

    # Create the main use case instance with all dependencies
    download_use_case = DownloadUseCase(
        http_gateway=http_gateway,
        html_parser=html_parser,
        file_downloader=file_downloader,
        archive_manager=archive_manager,
        file_manager=file_manager,
    )

    # Execute the main use case with configuration parameters
    logging.info("Executing the main use case...")
    try:
        download_use_case.execute(
            url=BASE_URL,  # The starting URL to scrape
            download_dir=DOWNLOAD_DIR,  # Where to save downloaded files
            zip_filepath=ZIP_FILEPATH,  # Where to create the final zip
            selector=LINK_SELECTOR,  # CSS selector to find links
            keywords=LINK_TEXT_KEYWORDS,  # Keywords to filter links
            suffix=LINK_SUFFIX,  # File extension to look for (e.g. '.pdf')
            timeout=REQUEST_TIMEOUT  # Network timeout in seconds
        )
        logging.info("Use case execution completed.")
    except Exception as e:
        # Catch and log any unexpected errors during execution
        logging.exception(f"An unexpected error occurred during the main execution flow: {e}")

# Standard Python idiom to run the application when executed directly
if __name__ == "__main__":
    run()