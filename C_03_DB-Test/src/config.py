import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional

dotenv_path = Path(__file__).resolve().parent.parent / '.env' # 
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded environment variables from: {dotenv_path}")
else:
    print(f".env file not found at {dotenv_path}, using system environment variables.")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.info(f"Log level set to: {LOG_LEVEL}")

DATA_DIR = PROJECT_ROOT / "data"
ACCOUNTING_DIR = DATA_DIR / "accounting"
ZIPS_DIR = ACCOUNTING_DIR / "zips"
CSVS_DIR = ACCOUNTING_DIR / "csvs"
OPERATORS_DIR = DATA_DIR / "operators"
OPERATORS_CSV_PATH = OPERATORS_DIR / "operators.csv"

logger.info(f"Project Root: {PROJECT_ROOT}")
logger.info(f"Data Directory: {DATA_DIR}")

BASE_ACCOUNTING_URL = os.getenv('ANS_BASE_ACCOUNTING_URL')
OPERATORS_CSV_URL = os.getenv('ANS_OPERATORS_CSV_URL')

if not BASE_ACCOUNTING_URL or not OPERATORS_CSV_URL:
    logger.error("Missing required environment variables: ANS_BASE_ACCOUNTING_URL or ANS_OPERATORS_CSV_URL")
    raise ValueError("Essential URL environment variables are not set.")

try:
    current_year_override = os.getenv('CURRENT_YEAR_OVERRIDE')
    current_year = int(current_year_override) if current_year_override else datetime.now().year
    YEARS_TO_DOWNLOAD: List[str] = [str(year) for year in range(current_year - 2, current_year)]
    years_override = os.getenv('YEARS_TO_DOWNLOAD')
    if years_override:
        YEARS_TO_DOWNLOAD = [y.strip() for y in years_override.split(',') if y.strip()]
    logger.info(f"Years to download: {YEARS_TO_DOWNLOAD} (based on year {current_year})")
except ValueError:
    logger.error("Invalid format for CURRENT_YEAR_OVERRIDE or YEARS_TO_DOWNLOAD environment variables.")
    raise

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'allow_local_infile': True,
    'pool_name': os.getenv('DB_POOL_NAME', 'ans_pool'),
    'pool_size': int(os.getenv('DB_POOL_SIZE', 2))
}

missing_db_vars = [k for k, v in DB_CONFIG.items() if v is None and k in ['user', 'password', 'database']]
if missing_db_vars:
    logger.error(f"Missing required database environment variables: {', '.join(missing_db_vars)}")
    raise ValueError("Essential database configuration is missing.")

MYSQL_CSV_ENCODING = 'utf8mb4'

logger.info(f"Database configured for: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

from src.application.dto import DownloadConfig, LoadConfig 

DOWNLOAD_CONFIG = DownloadConfig(
    base_accounting_url=BASE_ACCOUNTING_URL,
    operators_csv_url=OPERATORS_CSV_URL,
    years_to_download=YEARS_TO_DOWNLOAD,
    data_dir=DATA_DIR,
    accounting_dir=ACCOUNTING_DIR,
    zips_dir=ZIPS_DIR,
    csvs_dir=CSVS_DIR,
    operators_dir=OPERATORS_DIR,
    operators_csv_path=OPERATORS_CSV_PATH,
)

LOAD_CONFIG = LoadConfig(
    operators_csv_path=OPERATORS_CSV_PATH,
    accounting_csvs_dir=CSVS_DIR,
)