import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("src.main")

def start_application():
    logger.info("Application entry point: src.main")
    try:
        from src.interfaces.web.app import run_dev_server

        logger.info("Attempting to start development server via run_dev_server...")
        run_dev_server()
    except ImportError as e:
        logger.error(f"Failed to import application components: {e}", exc_info=True)
        logger.error("--- Troubleshooting ---")
        logger.error(f"Current Working Directory: {os.getcwd()}")
        logger.error(f"Python Executable: {sys.executable}")
        logger.error(f"Sys Path: {sys.path}")
        logger.error("Ensure you are running 'python -m src.main' from the 'backend' directory.")
        logger.error("Ensure the 'src' directory exists in 'backend' and contains '__init__.py'.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during application startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    start_application()