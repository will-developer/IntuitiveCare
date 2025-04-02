import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger.info(f"Attempting to load .env file from: {dotenv_path}")
loaded = load_dotenv(dotenv_path=dotenv_path, verbose=True)
if not loaded:
    logger.warning(f".env file not found or failed to load from {dotenv_path}. Using environment variables or defaults.")

class Settings:
    raw_csv_path = os.getenv("CSV_FILE_PATH", "default_path_if_not_set.csv")
    backend_dir = os.path.dirname(dotenv_path)
    CSV_FILE_PATH: str = os.path.abspath(os.path.join(backend_dir, raw_csv_path))

    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() in ['true', '1', 't']

settings = Settings()

logger.info(f"Resolved CSV path to: {settings.CSV_FILE_PATH}")
if not os.path.exists(settings.CSV_FILE_PATH):
     logger.warning(f"Configured CSV file path does not exist: {settings.CSV_FILE_PATH}")
else:
     logger.info(f"Confirmed CSV file exists at: {settings.CSV_FILE_PATH}")