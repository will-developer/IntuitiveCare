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
    def __init__(
        self,
        operator_repo: OperatorRepository,
        accounting_repo: AccountingRepository,
        file_system: FileSystem,
    ):
        self._operator_repo = operator_repo
        self._accounting_repo = accounting_repo
        self._fs = file_system

    def execute(self, config: LoadConfig) -> bool:
        logger.info("--- Starting Data Loading Use Case ---")
        try:
            self._clear_database_tables()

            operators_loaded_count = self._load_operators(config)
            if operators_loaded_count <= 0:
                 logger.error("Operator loading failed or loaded 0 records. Aborting accounting load.")
                 return False

            accounting_loaded_count = self._load_accounting_statements(config)

            logger.info(f"Total accounting statements loaded: {accounting_loaded_count}")
            logger.info("--- Finished Data Loading Use Case ---")
            return True

        except Exception as e:
            logger.exception(f"An unexpected error occurred during the data loading process: {e}")
            return False

    def _clear_database_tables(self) -> None:
        logger.warning("Clearing existing data from 'accounting' and 'operators' tables...")
        try:
            self._accounting_repo.clear_all()
            logger.info("'accounting' table cleared.")
            self._operator_repo.clear_all()
            logger.info("'operators' table cleared.")
            logger.info("Pre-load cleanup finished.")
        except Exception as e:
            logger.error(f"Error during table cleanup: {e}")
            raise

    def _load_operators(self, config: LoadConfig) -> int:
        logger.info(f"Loading operators from: {config.operators_csv_path}")
        if not self._fs.path_exists(config.operators_csv_path):
            logger.error(f"Operators CSV file not found: {config.operators_csv_path}")
            return -1

        try:
            count = self._operator_repo.load_from_csv(config.operators_csv_path)
            logger.info(f"Operators loaded: {count} rows affected.")
            return count
        except Exception as e:
            logger.error(f"Failed to load operators: {e}")
            return -1

    def _load_accounting_statements(self, config: LoadConfig) -> int:
        logger.info(f"Looking for accounting CSV files in: {config.accounting_csvs_dir}")
        csv_files = self._fs.list_files(config.accounting_csvs_dir, '*.csv')

        if not csv_files:
            logger.warning(f"No accounting CSV files found in {config.accounting_csvs_dir}. Nothing to load.")
            return 0

        logger.info(f"Found {len(csv_files)} accounting CSV files. Starting load...")
        total_loaded_count = 0
        for file_path in csv_files:
            filename = self._fs.get_filename(file_path)
            logger.debug(f"Processing accounting file: {filename}")

            reference_date = self._parse_reference_date_from_filename(filename)
            if reference_date is None:
                logger.error(f"Skipping {filename}: Could not determine reference date (quarter/year).")
                continue

            try:
                logger.info(f"Loading {filename} for reference date {reference_date.strftime('%Y-%m-%d')}...")
                count = self._accounting_repo.load_from_csv(file_path, reference_date)
                logger.info(f"Loaded {count} rows from {filename}.")
                total_loaded_count += count
            except Exception as e:
                logger.error(f"Failed to load accounting data from {filename}: {e}")

        return total_loaded_count

    def _parse_reference_date_from_filename(self, filename: str) -> Optional[date]:
        match = re.search(r'(\d)T(\d{4})|(\d{4})_(\d)T', filename, re.IGNORECASE)
        if match:
            if match.group(1) and match.group(2):
                quarter, year = int(match.group(1)), int(match.group(2))
            elif match.group(3) and match.group(4):
                year, quarter = int(match.group(3)), int(match.group(4))
            else:
                return None

            if not (1 <= quarter <= 4):
                logger.warning(f"Invalid quarter '{quarter}' found in filename: {filename}")
                return None

            month = quarter * 3
            day = 31 if month in [3, 12] else 30
            try:
                return date(year, month, day)
            except ValueError:
                logger.error(f"Calculated invalid date: {year}-{month}-{day} from filename: {filename}")
                return None
        else:
            logger.warning(f"Could not extract year/quarter from filename: {filename}")
            return None