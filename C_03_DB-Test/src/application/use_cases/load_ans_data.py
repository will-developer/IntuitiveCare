import logging
import re
from datetime import date
from typing import Optional

from src.application.ports import (
    FileSystem,
    OperatorRepository,
    AccountingRepository,
)
from src.application.dto import LoadConfig

logger = logging.getLogger(__name__)

class LoadAnsDataUseCase:
    """Orchestrates loading of operator and accounting data into repositories"""
    
    def __init__(
        self,
        operator_repo: OperatorRepository,  # For operator data storage
        accounting_repo: AccountingRepository,  # For accounting data storage
        file_system: FileSystem,  # For file operations
    ):
        """Initialize with required data repositories and file system"""
        self._operator_repo = operator_repo
        self._accounting_repo = accounting_repo
        self._fs = file_system

    def execute(self, config: LoadConfig) -> bool:
        """Main execution method that runs the complete loading workflow"""
        logger.info("--- Starting Data Loading Use Case ---")
        try:
            # 1. Clear existing data
            self._clear_database_tables()

            # 2. Load operators (required)
            operators_loaded_count = self._load_operators(config)
            if operators_loaded_count <= 0:
                 logger.error("Operator loading failed - aborting accounting load")
                 return False

            # 3. Load accounting statements
            accounting_loaded_count = self._load_accounting_statements(config)

            logger.info(f"Total accounting statements loaded: {accounting_loaded_count}")
            logger.info("--- Finished Data Loading Use Case ---")
            return True

        except Exception as e:
            logger.exception(f"Unexpected error during data loading: {e}")
            return False

    def _clear_database_tables(self) -> None:
        """Clears all existing data from both repositories"""
        logger.warning("Clearing existing data from database tables...")
        try:
            self._accounting_repo.clear_all()
            logger.info("Cleared accounting data")
            self._operator_repo.clear_all()
            logger.info("Cleared operator data")
        except Exception as e:
            logger.error(f"Table cleanup failed: {e}")
            raise

    def _load_operators(self, config: LoadConfig) -> int:
        """Loads operator data from CSV file"""
        logger.info(f"Loading operators from: {config.operators_csv_path}")
        
        # Verify file exists
        if not self._fs.path_exists(config.operators_csv_path):
            logger.error(f"Operators CSV not found at: {config.operators_csv_path}")
            return -1

        try:
            # Load and return record count
            count = self._operator_repo.load_from_csv(config.operators_csv_path)
            logger.info(f"Loaded {count} operator records")
            return count
        except Exception as e:
            logger.error(f"Operator load failed: {e}")
            return -1

    def _load_accounting_statements(self, config: LoadConfig) -> int:
        """Loads accounting data from all CSV files in directory"""
        logger.info(f"Loading accounting data from: {config.accounting_csvs_dir}")
        
        # Find all CSV files
        csv_files = self._fs.list_files(config.accounting_csvs_dir, '*.csv')
        if not csv_files:
            logger.warning("No accounting CSV files found")
            return 0

        logger.info(f"Found {len(csv_files)} accounting files")
        total_loaded = 0
        
        for file_path in csv_files:
            filename = self._fs.get_filename(file_path)
            logger.debug(f"Processing: {filename}")

            # Extract quarter/year from filename
            reference_date = self._parse_reference_date_from_filename(filename)
            if not reference_date:
                logger.error(f"Skipping {filename}: invalid date format")
                continue

            try:
                # Load with reference date
                count = self._accounting_repo.load_from_csv(file_path, reference_date)
                logger.info(f"Loaded {count} records from {filename}")
                total_loaded += count
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")

        return total_loaded

    def _parse_reference_date_from_filename(self, filename: str) -> Optional[date]:
        """Extracts quarter/year from filename and returns as date (last day of quarter)"""
        # Match patterns like "1T2023" or "2023_1T"
        match = re.search(r'(\d)T(\d{4})|(\d{4})_(\d)T', filename, re.IGNORECASE)
        if not match:
            logger.warning(f"Invalid filename format: {filename}")
            return None

        # Extract quarter and year from either pattern
        if match.group(1) and match.group(2):
            quarter, year = int(match.group(1)), int(match.group(2))
        else:
            year, quarter = int(match.group(3)), int(match.group(4))

        # Validate quarter
        if not 1 <= quarter <= 4:
            logger.warning(f"Invalid quarter {quarter} in {filename}")
            return None

        # Calculate last day of quarter
        month = quarter * 3
        day = 31 if month in [3, 12] else 30
        
        try:
            return date(year, month, day)
        except ValueError:
            logger.error(f"Invalid date {year}-{month}-{day} from {filename}")
            return None