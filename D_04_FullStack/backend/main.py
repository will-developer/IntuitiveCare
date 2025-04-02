import logging
import traceback
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.config import settings
from src.infrastructure.repositories.csv_operator_repository import CsvOperatorRepository
from src.application.use_cases.search_operators import SearchOperatorsUseCase
from src.interfaces.web.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_application():
    logger.info("Application starting...")

    logger.info(f"Attempting to use CSV path from settings: {settings.CSV_FILE_PATH}")
    try:
        csv_repo = CsvOperatorRepository(csv_file_path=settings.CSV_FILE_PATH)

        logger.info("Attempting to load operator data...")
        csv_repo.load_data()

        if not csv_repo.is_data_loaded():
             logger.critical("*****************************************************")
             logger.critical("******** FATAL: OPERATOR DATA FAILED TO LOAD ********")
             logger.critical("**** API cannot function without data.           ****")
             logger.critical(f"**** Failed path: {settings.CSV_FILE_PATH}        ****")
             logger.critical("**** Please check the CSV_FILE_PATH in .env,     ****")
             logger.critical("**** file existence, and file integrity.         ****")
             logger.critical("*****************************************************")
             sys.exit("Exiting due to data load failure.")
        else:
             logger.info(f"Operator data loaded successfully. Shape: {csv_repo.get_data_shape()}")

        search_uc = SearchOperatorsUseCase(operator_repository=csv_repo)

        flask_app = create_app(
            operator_repository=csv_repo,
            search_operators_use_case=search_uc
        )

        logger.info(f"Starting Flask server on http://{settings.FLASK_HOST}:{settings.FLASK_PORT}")
        logger.info(f"Flask Debug Mode: {settings.FLASK_DEBUG}")

        flask_app.run(
            host=settings.FLASK_HOST,
            port=settings.FLASK_PORT,
            debug=settings.FLASK_DEBUG
        )

    except ValueError as ve:
         logger.error(f"Configuration error during initialization: {ve}", exc_info=True)
         sys.exit(f"Configuration error: {ve}")
    except FileNotFoundError as fnf:
         logger.error(f"Data file not found during initialization: {fnf}", exc_info=True)
         sys.exit(f"Data file error: {fnf}")
    except Exception as e:
         logger.error(f"An unexpected error occurred during application startup: {e}", exc_info=True)
         sys.exit(f"Unexpected startup error: {e}")


if __name__ == '__main__':
    run_application()