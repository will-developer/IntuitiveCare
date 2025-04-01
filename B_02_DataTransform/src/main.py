import logging
import sys
from . import config
from .application import pipeline

try:
    logging.basicConfig(
        level=config.LOG_LEVEL.upper(),
        format=config.LOG_FORMAT,
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    logger.debug("Logging configured successfully.")
except Exception as e:
    print(f"FATAL: Failed to configure logging: {e}", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    logger.info("Application entry point reached. Starting pipeline...")
    try:
        pipeline.run_pipeline()
        logger.info("Application finished.")
        sys.exit(0)
    except SystemExit as e:
        logger.info(f"Application exiting with status code {e.code}.")
        raise
    except Exception as e:
        logger.critical(f"Unhandled exception at main entry point: {e}", exc_info=True)
        sys.exit(3)