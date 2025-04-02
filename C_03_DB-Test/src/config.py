import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List

# Load environment variables from .env file if present
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded environment variables from: {dotenv_path}")
else:
    print(f"Note: .env file not found at {dotenv_path}, using system environment variables.")

# Project directory setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.info(f"Log level set to: {LOG_LEVEL}")

# Directory structure configuration
DATA_DIR = PROJECT_ROOT / "data"
ACCOUNTING_DIR = DATA_DIR / "accounting"
ZIPS_DIR = ACCOUNTING_DIR / "zips"       # For downloaded zip files
CSVS_DIR = ACCOUNTING_DIR / "csvs"       # For extracted CSV files
OPERATORS_DIR = DATA_DIR / "operators"   # For operator data
OPERATORS_CSV_PATH = OPERATORS_DIR / "operators.csv"

logger.info(f"Project structure initialized:\n"
           f"- Root: {PROJECT_ROOT}\n"
           f"- Data: {DATA_DIR}")

# Validate required URLs
BASE_ACCOUNTING_URL = os.getenv('ANS_BASE_ACCOUNTING_URL')
OPERATORS_CSV_URL = os.getenv('ANS_OPERATORS_CSV_URL')
if not BASE_ACCOUNTING_URL or not OPERATORS_CSV_URL:
    logger.error("Missing required URL environment variables")
    raise ValueError("ANS_BASE_ACCOUNTING_URL and ANS_OPERATORS_CSV_URL must be set")

# Configure year range for data download
try:
    current_year = int(os.getenv('CURRENT_YEAR_OVERRIDE')) if os.getenv('CURRENT_YEAR_OVERRIDE') else datetime.now().year
    YEARS_TO_DOWNLOAD: List[str] = [str(year) for year in range(current_year - 2, current_year)]
    
    # Allow manual override of years
    if years_override := os.getenv('YEARS_TO_DOWNLOAD'):
        YEARS_TO_DOWNLOAD = [y.strip() for y in years_override.split(',') if y.strip()]
    
    logger.info(f"Configured years to download: {YEARS_TO_DOWNLOAD}")
except ValueError:
    logger.error("Invalid year format in environment variables")
    raise

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'allow_local_infile': True,  # Required for LOAD DATA LOCAL INFILE
    'pool_name': os.getenv('DB_POOL_NAME', 'ans_pool'),
    'pool_size': int(os.getenv('DB_POOL_SIZE', 2))
}

# Validate required database credentials
missing_db_vars = [k for k in ['user', 'password', 'database'] if not DB_CONFIG.get(k)]
if missing_db_vars:
    logger.error(f"Missing database credentials: {', '.join(missing_db_vars)}")
    raise ValueError("Incomplete database configuration")

MYSQL_CSV_ENCODING = 'utf8mb4'  # Supports full Unicode including emojis
logger.info(f"Database connection configured for: {DB_CONFIG['host']}:{DB_CONFIG['port']}")

# Application configuration objects
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