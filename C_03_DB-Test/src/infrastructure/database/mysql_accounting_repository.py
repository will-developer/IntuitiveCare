# src/infrastructure/database/mysql_accounting_repository.py
import logging
import time
from pathlib import Path
from datetime import date
from mysql.connector import Error, MySQLConnection
from typing import TYPE_CHECKING

from src.application.ports.accounting_repository import AccountingRepository
if TYPE_CHECKING:
    from .mysql_connection_manager import MySQLConnectionManager

logger = logging.getLogger(__name__)
MYSQL_CSV_ENCODING = 'utf8mb4'

class MySqlAccountingRepository(AccountingRepository):
    def __init__(self, connection_manager: 'MySQLConnectionManager'):
        self._conn_manager = connection_manager
        # SQL template remains the same
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
        logger.warning("Attempting to clear 'accounting' table.")
        conn = None
        cursor = None
        fk_check_original_value = 1 # Assume default is 1 (enabled)

        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            # Optional: Get current FK check value
            # cursor.execute("SELECT @@SESSION.foreign_key_checks;")
            # fk_check_original_value = cursor.fetchone()[0]
            # logger.debug(f"Original foreign_key_checks value: {fk_check_original_value}")

            logger.debug("Disabling foreign key checks for accounting TRUNCATE.")
            cursor.execute("SET SESSION foreign_key_checks = 0;") # Use SESSION scope

            cursor.execute("TRUNCATE TABLE accounting;")
            conn.commit()
            logger.info("'accounting' table cleared successfully.")

        except Error as e:
            logger.error(f"Database error while clearing accounting table: {e}")
            if conn: conn.rollback()
            # Let finally block handle FK check re-enabling before raising
            raise RuntimeError("Failed to clear accounting table") from e
        except Exception as e:
            logger.error(f"Unexpected error during accounting table clear: {e}")
            if conn: conn.rollback()
            # Let finally block handle FK check re-enabling before raising
            raise
        finally:
            # Ensure FK checks are re-enabled IN THE SAME SESSION
            if cursor:
                try:
                    logger.debug(f"Re-enabling foreign key checks for accounting session (setting to {fk_check_original_value}).")
                    cursor.execute(f"SET SESSION foreign_key_checks = {fk_check_original_value};")
                    conn.commit() # Commit the SET command
                except Error as fk_err:
                    logger.error(f"Failed to re-enable foreign key checks: {fk_err}")
                    # Log error but proceed with cleanup
                finally:
                     cursor.close() # Close cursor after attempting to re-enable checks
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Returned connection to pool after clear_all accounting.")

    def load_from_csv(self, csv_path: Path, reference_date: date) -> int:
        # --- load_from_csv method remains unchanged ---
        table_name = f"accounting ({csv_path.name})" # For logging
        logger.info(f"Loading {table_name} for reference date {reference_date.strftime('%Y-%m-%d')}")
        start_time = time.time()
        affected_rows = 0
        conn = None
        cursor = None

        abs_csv_path = csv_path.resolve()
        escaped_csv_path = str(abs_csv_path).replace('\\', '\\\\')
        formatted_date = reference_date.strftime('%Y-%m-%d')

        formatted_sql = self._load_sql_template.format(
            csv_path=escaped_csv_path,
            encoding=MYSQL_CSV_ENCODING, # Use the defined encoding
            trimestre_ref_sql=formatted_date
        )

        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            logger.info(f"Executing LOAD DATA for '{table_name}'...")
            cursor.execute(formatted_sql)
            affected_rows = cursor.rowcount
            conn.commit()

            end_time = time.time()
            logger.info(f"LOAD DATA for '{table_name}' completed in {end_time - start_time:.2f}s. Rows affected: {affected_rows}")

            if affected_rows == 0:
                 self._log_load_data_warnings(cursor, table_name) # Call local helper

            return affected_rows

        except Error as err:
            logger.error(f"Database error during LOAD DATA for '{table_name}': {err}")
            if conn: conn.rollback()
            raise RuntimeError(f"Failed to load accounting data from {csv_path.name}") from err
        except Exception as e:
            logger.error(f"Unexpected error during LOAD DATA for '{table_name}': {e}", exc_info=True)
            if conn: conn.rollback()
            raise RuntimeError(f"Unexpected failure loading accounting data from {csv_path.name}") from e
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Returned connection to pool after load_from_csv.")

    def _log_load_data_warnings(self, cursor, table_name: str):
         # --- _log_load_data_warnings method remains unchanged ---
        try:
            cursor.execute("SHOW WARNINGS")
            warnings = cursor.fetchall()
            if warnings:
                logger.warning(f"LOAD DATA for '{table_name}' generated warnings:")
                for level, code, message in warnings:
                    logger.warning(f"  - Level: {level}, Code: {code}, Message: {message}")
            else:
                logger.warning(f"LOAD DATA for '{table_name}' affected 0 rows and produced no warnings. "
                               f"Check file content, delimiters, line endings, encoding ('{MYSQL_CSV_ENCODING}'), and IGNORE clause.")
        except Error as warn_err:
            logger.error(f"Could not retrieve warnings for '{table_name}': {warn_err}")