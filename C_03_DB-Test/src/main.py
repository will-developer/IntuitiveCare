import logging
import sys

# Configuration Import - Critical for application startup
try:
    from src import config  # Main configuration module
except ImportError as e:
    print(f"Configuration import failed: {e}", file=sys.stderr)
    print("Possible solutions:", file=sys.stderr)
    print("1. Install dependencies: pip install -r requirements.txt", file=sys.stderr)
    print("2. Check .env file exists with required variables", file=sys.stderr)
    sys.exit(1)
except ValueError as e:
    print(f"Invalid configuration: {e}", file=sys.stderr)
    sys.exit(1)

# Application Component Imports
try:
    # Infrastructure Layer
    from src.infrastructure import (
        OsFileSystem,
        RequestsDownloader,
        Bs4HtmlParser,
        ZipfileExtractor,
        MySQLConnectionManager,
        MySqlOperatorRepository,
        MySqlAccountingRepository,
    )
    # Application Layer
    from src.application import (
        DownloadAnsDataUseCase,
        LoadAnsDataUseCase,
    )
except ImportError as e:
    logging.exception("Critical component import failed")
    sys.exit(1)

logger = logging.getLogger(__name__)

def run():
    """Main application execution flow."""
    logger.info("=== ANS Data Processing Starting ===")
    
    # ----------------------------
    # Infrastructure Initialization
    # ----------------------------
    logger.info("Building infrastructure components...")
    try:
        # Core file operations
        file_system = OsFileSystem()
        file_downloader = RequestsDownloader()
        html_parser = Bs4HtmlParser()
        zip_extractor = ZipfileExtractor()
        
        # Database components
        db_connection_manager = MySQLConnectionManager(
            db_config=config.DB_CONFIG,
            pool_size=config.DB_CONFIG['pool_size']  # Uses configured pool size
        )
        operator_repo = MySqlOperatorRepository(db_connection_manager)
        accounting_repo = MySqlAccountingRepository(db_connection_manager)
        
        logger.info("Infrastructure ready")
    except Exception as e:
        logger.exception("Infrastructure setup failed")
        return

    # --------------------------
    # Application Layer Setup
    # --------------------------
    logger.info("Initializing use cases...")
    download_use_case = DownloadAnsDataUseCase(
        file_system=file_system,
        file_downloader=file_downloader,
        html_parser=html_parser,
        zip_extractor=zip_extractor,
    )
    load_use_case = LoadAnsDataUseCase(
        operator_repo=operator_repo,
        accounting_repo=accounting_repo,
        file_system=file_system,
    )
    logger.info("Use cases initialized")

    # --------------------------
    # Execution Flow
    # --------------------------
    # Phase 1: Data Download
    logger.info("--- Starting Data Download ---")
    download_successful = download_use_case.execute(config.DOWNLOAD_CONFIG)
    
    # Phase 2: Data Loading (only if download succeeded)
    if download_successful:
        logger.info("--- Starting Data Loading ---")
        load_successful = load_use_case.execute(config.LOAD_CONFIG)
        logger.info(f"Load process {'succeeded' if load_successful else 'failed'}")
    else:
        logger.error("Download failed - skipping load phase")

    logger.info("=== Processing Completed ===")

if __name__ == "__main__":
    # Ensure project root is in Python path
    if str(config.PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(config.PROJECT_ROOT))
        logger.debug(f"Added project root to path: {config.PROJECT_ROOT}")

    run()