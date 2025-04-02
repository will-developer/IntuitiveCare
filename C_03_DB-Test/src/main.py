import logging
import sys

try:
    from src import config
except ImportError as e:
     print(f"Error importing configuration or dependencies: {e}", file=sys.stderr)
     print("Ensure all dependencies are installed (pip install -r requirements.txt or poetry install)", file=sys.stderr)
     print("Ensure the .env file has necessary variables set.", file=sys.stderr)
     sys.exit(1)
except ValueError as e:
    print(f"Configuration Error: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from src.infrastructure import (
        OsFileSystem,
        RequestsDownloader,
        Bs4HtmlParser,
        ZipfileExtractor,
        MySQLConnectionManager,
        MySqlOperatorRepository,
        MySqlAccountingRepository,
    )
    from src.application import (
        DownloadAnsDataUseCase,
        LoadAnsDataUseCase,
    )
except ImportError as e:
     logging.exception(f"Failed to import application/infrastructure components: {e}")
     sys.exit(1)

logger = logging.getLogger(__name__)

def run():
    logger.info("=== Application Starting ===")

    logger.info("Initializing infrastructure components...")
    try:
        file_system = OsFileSystem()
        file_downloader = RequestsDownloader()
        html_parser = Bs4HtmlParser()
        zip_extractor = ZipfileExtractor()

        db_connection_manager = MySQLConnectionManager(
            db_config=config.DB_CONFIG,
            pool_size=config.DB_CONFIG.get('pool_size', 2)
        )
        operator_repo = MySqlOperatorRepository(db_connection_manager)
        accounting_repo = MySqlAccountingRepository(db_connection_manager)
        logger.info("Infrastructure components initialized.")

    except Exception as e:
        logger.exception(f"Failed to initialize infrastructure components: {e}")
        logger.error("Application cannot proceed.")
        return

    logger.info("Initializing application use cases...")
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
    logger.info("Application use cases initialized.")

    logger.info("--- Starting Download Process ---")
    download_successful = download_use_case.execute(config.DOWNLOAD_CONFIG)

    if download_successful:
        logger.info("Download process completed successfully (or partially, check logs).")
        logger.info("--- Starting Load Process ---")
        load_successful = load_use_case.execute(config.LOAD_CONFIG)
        if load_successful:
            logger.info("Load process completed successfully.")
        else:
            logger.error("Load process failed. Check logs for details.")
    else:
        logger.error("Download process failed. Skipping load process.")

    logger.info("=== Application Finished ===")

if __name__ == "__main__":
    project_root = config.PROJECT_ROOT
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        logger.debug(f"Added {project_root} to sys.path")

    run()