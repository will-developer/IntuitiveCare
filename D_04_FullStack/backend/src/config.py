import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    CSV_FILE_PATH: str = os.getenv("CSV_FILE_PATH", "default_path_if_not_set.csv")
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() in ['true', '1', 't']

settings = Settings()

if not settings.CSV_FILE_PATH or not os.path.isabs(os.path.join(os.path.dirname(__file__), '../../', settings.CSV_FILE_PATH)):
     potential_abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', settings.CSV_FILE_PATH))
     print(f"Attempting to use CSV path: {potential_abs_path}")
     if not os.path.exists(potential_abs_path):
          print(f"Warning: CSV_FILE_PATH '{settings.CSV_FILE_PATH}' (resolved to '{potential_abs_path}') not found or not set correctly in .env")
     else:
          settings.CSV_FILE_PATH = potential_abs_path
else:
     print(f"Using configured CSV path: {settings.CSV_FILE_PATH}")