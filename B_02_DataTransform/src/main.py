import logging
import sys

from .application import pipeline  # Import the main processing pipeline

# Logging configuration constants
LOG_LEVEL = "INFO"  # Default logging level (INFO, DEBUG, WARNING, etc.)
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'  # Log message format

try:
    # Configure the root logger with:
    # - Specified log level (converted to uppercase)
    # - Defined format
    # - Output to stdout
    logging.basicConfig(
        level=LOG_LEVEL.upper(),
        format=LOG_FORMAT,
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)  # Get logger for this module
    logger.debug("Logging configured successfully from main.py settings.")
except ValueError as e:
    # Handle invalid log level error (prints to stderr and exits)
    print(f"FATAL: Invalid logging level '{LOG_LEVEL}'. Error: {e}", file=sys.stderr)
    sys.exit(2)  # Exit with error code 2 for configuration errors
except Exception as e:
    # Handle any other logging configuration errors
    print(f"FATAL: Failed to configure logging: {e}", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    # Main application entry point
    logger.info("Application entry point reached. Starting pipeline...")
    try:
        # Execute the main processing pipeline
        pipeline.run_pipeline()
        logger.info("Application finished successfully.")
        sys.exit(0)  # Exit with code 0 for success
    except SystemExit as e:
        # Handle intentional system exits (re-raise after logging)
        logger.info(f"Application exiting with status code {e.code}.")
        raise
    except Exception as e:
        # Handle any uncaught exceptions at the top level
        logger.critical(f"Unhandled critical exception at main entry point: {e}", exc_info=True)
        sys.exit(3)  # Exit with code 3 for unhandled exceptions