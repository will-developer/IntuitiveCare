import logging
import sys

from .application import pipeline

LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

try:
    logging.basicConfig(
        level=LOG_LEVEL.upper(),
        format=LOG_FORMAT,
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    logger.debug("Logging configured successfully from main.py settings.")
except ValueError as e:
    print(f"FATAL: Invalid logging level '{LOG_LEVEL}'. Error: {e}", file=sys.stderr)
    sys.exit(2)
except Exception as e:
    print(f"FATAL: Failed to configure logging: {e}", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    logger.info("Application entry point reached. Starting pipeline...")
    try:
        pipeline.run_pipeline()
        logger.info("Application finished successfully.")
        sys.exit(0)
    except SystemExit as e:
        logger.info(f"Application exiting with status code {e.code}.")
        raise
    except Exception as e:
        logger.critical(f"Unhandled critical exception at main entry point: {e}", exc_info=True)
        sys.exit(3)