import logging
import time
from pathlib import Path
from datetime import date
from mysql.connector import Error
from typing import TYPE_CHECKING

from src.application.ports.accounting_repository import AccountingRepository
if TYPE_CHECKING:
    from .mysql_connection_manager import MySQLConnectionManager

logger = logging.getLogger(__name__)
MYSQL_CSV_ENCODING = 'utf8mb4'  # MySQL encoding that supports full Unicode

class MySqlAccountingRepository(AccountingRepository):
    """MySQL implementation of AccountingRepository for bulk loading accounting data."""
    
    def __init__(self, connection_manager: 'MySQLConnectionManager'):
        self._conn_manager = connection_manager
        
        # SQL template for LOAD DATA command with:
        # - Field mapping
        # - Data cleaning
        # - Decimal number handling (Brazilian format)
        self._load_sql_template = """
            LOAD DATA LOCAL INFILE '{csv_path}'
            INTO TABLE accounting
            CHARACTER SET {encoding}
            FIELDS TERMINATED BY ';'
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\n' -- Or '\\r\\n' if needed
            IGNORE 1 ROWS
            (
                @DATA_CSV, reg_ans, cd_conta_contabil, descricao,
                @VL_SALDO_INICIAL, @VL_SALDO_FINAL
            )
            SET
                trimestre_referencia = '{trimestre_ref_sql}',
                reg_ans = reg_ans,
                cd_conta_contabil = LEFT(TRIM(cd_conta_contabil), 50),
                descricao = LEFT(TRIM(descricao), 500),
                vl_saldo_inicial = IF(TRIM(COALESCE(@VL_SALDO_INICIAL,'')) REGEXP '^-?[0-9.,]+$',
                                    CAST(REPLACE(REPLACE(TRIM(@VL_SALDO_INICIAL), '.', ''), ',', '.') AS DECIMAL(18,2)),
                                    NULL),
                vl_saldo_final = IF(TRIM(COALESCE(@VL_SALDO_FINAL,'')) REGEXP '^-?[0-9.,]+$',
                                  CAST(REPLACE(REPLACE(TRIM(@VL_SALDO_FINAL), '.', ''), ',', '.') AS DECIMAL(18,2)),
                                  NULL);
        """

    def clear_all(self) -> None:
        """Truncates the accounting table, temporarily disabling foreign key checks."""
        logger.warning("Attempting to clear 'accounting' table.")
        conn = None
        cursor = None
        fk_check_original_value = 1  # Default MySQL FK check state (enabled)

        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            # Disable FK checks to allow TRUNCATE on tables with FK constraints
            logger.debug("Disabling foreign key checks for accounting TRUNCATE.")
            cursor.execute("SET SESSION foreign_key_checks = 0;")

            cursor.execute("TRUNCATE TABLE accounting;")
            conn.commit()
            logger.info("'accounting' table cleared successfully.")

        except Error as e:
            logger.error(f"Database error while clearing accounting table: {e}")
            if conn: conn.rollback()
            raise RuntimeError("Failed to clear accounting table") from e
        finally:
            # Critical: Always re-enable FK checks and clean up resources
            if cursor:
                try:
                    logger.debug(f"Re-enabling foreign key checks (original value: {fk_check_original_value}).")
                    cursor.execute(f"SET SESSION foreign_key_checks = {fk_check_original_value};")
                    conn.commit()
                except Error as fk_err:
                    logger.error(f"Failed to re-enable foreign key checks: {fk_err}")
                finally:
                    cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Connection returned to pool after clear_all.")

    def load_from_csv(self, csv_path: Path, reference_date: date) -> int:
        """Bulk loads accounting data from CSV using MySQL's LOAD DATA INFILE.
        
        Returns:
            int: Number of affected rows
        Raises:
            RuntimeError: If loading fails
        """
        table_name = f"accounting ({csv_path.name})"
        logger.info(f"Loading {table_name} for reference date {reference_date}")
        start_time = time.time()
        
        # Prepare paths and SQL with proper escaping
        abs_csv_path = csv_path.resolve()
        escaped_csv_path = str(abs_csv_path).replace('\\', '\\\\')
        formatted_date = reference_date.strftime('%Y-%m-%d')

        formatted_sql = self._load_sql_template.format(
            csv_path=escaped_csv_path,
            encoding=MYSQL_CSV_ENCODING,
            trimestre_ref_sql=formatted_date
        )

        conn = None
        cursor = None
        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            logger.info(f"Executing LOAD DATA for '{table_name}'...")
            cursor.execute(formatted_sql)
            affected_rows = cursor.rowcount
            conn.commit()

            logger.info(f"LOAD DATA completed in {time.time() - start_time:.2f}s. Rows: {affected_rows}")
            
            if affected_rows == 0:
                self._log_load_data_warnings(cursor, table_name)

            return affected_rows

        except Error as err:
            logger.error(f"Database error during LOAD DATA: {err}")
            if conn: conn.rollback()
            raise RuntimeError(f"Failed to load {csv_path.name}") from err
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Connection returned to pool.")

    def _log_load_data_warnings(self, cursor, table_name: str):
        """Logs MySQL warnings when LOAD DATA completes but affects 0 rows."""
        try:
            cursor.execute("SHOW WARNINGS")
            warnings = cursor.fetchall()
            if warnings:
                logger.warning(f"LOAD DATA warnings for '{table_name}':")
                for level, code, message in warnings:
                    logger.warning(f"  - {level} (Code {code}): {message}")
            else:
                logger.warning(f"No rows loaded for '{table_name}'. Check file format and encoding.")
        except Error as warn_err:
            logger.error(f"Could not retrieve warnings: {warn_err}")