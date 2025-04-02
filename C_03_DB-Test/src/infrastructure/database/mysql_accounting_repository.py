import logging
import time
from pathlib import Path
from datetime import date
from mysql.connector import Error

from src.application.ports.accounting_repository import AccountingRepository
from .mysql_connection_manager import MySQLConnectionManager
from .db_config import MYSQL_CSV_ENCODING

logger = logging.getLogger(__name__)

class MySqlAccountingRepository(AccountingRepository):
    def __init__(self, connection_manager: MySQLConnectionManager):
        self._conn_manager = connection_manager
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
                trimestre_referencia = '{trimestre_ref_sql}', -- Populated dynamically
                reg_ans = reg_ans, -- Assuming direct mapping is fine
                cd_conta_contabil = LEFT(TRIM(cd_conta_contabil), 50), -- Clean and truncate
                descricao = LEFT(TRIM(descricao), 500), -- Clean and truncate
                -- Convert decimal: remove thousand separators (.), replace decimal comma (,) with dot (.)
                vl_saldo_inicial = IF(TRIM(COALESCE(@VL_SALDO_INICIAL,'')) REGEXP '^-?[0-9.,]+$', -- Basic check for valid chars
                                    CAST(REPLACE(REPLACE(TRIM(@VL_SALDO_INICIAL), '.', ''), ',', '.') AS DECIMAL(18,2)),
                                    NULL),
                vl_saldo_final = IF(TRIM(COALESCE(@VL_SALDO_FINAL,'')) REGEXP '^-?[0-9.,]+$', -- Basic check for valid chars
                                  CAST(REPLACE(REPLACE(TRIM(@VL_SALDO_FINAL), '.', ''), ',', '.') AS DECIMAL(18,2)),
                                  NULL);
        """

    def clear_all(self) -> None:
        logger.warning("Attempting to clear 'accounting' table.")
        conn = None
        cursor = None
        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE accounting;")
            conn.commit()
            logger.info("'accounting' table cleared successfully.")
        except Error as e:
            logger.error(f"Database error while clearing accounting table: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during accounting table clear: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Returned connection to pool after clear_all.")

    def load_from_csv(self, csv_path: Path, reference_date: date) -> int:
        table_name = f"accounting ({csv_path.name})"
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
            encoding=MYSQL_CSV_ENCODING,
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
                 MySqlOperatorRepository(self._conn_manager)._log_load_data_warnings(cursor, table_name)


            return affected_rows

        except Error as err:
            logger.error(f"Database error during LOAD DATA for '{table_name}': {err}")
            if conn:
                conn.rollback()
            if "Incorrect decimal value" in str(err):
                 logger.error("Potential issue with decimal conversion. Check source data format (commas/dots) and SQL SET clause.")
            raise RuntimeError(f"Failed to load accounting data from {csv_path.name}") from err
        except Exception as e:
            logger.error(f"Unexpected error during LOAD DATA for '{table_name}': {e}", exc_info=True)
            if conn:
                conn.rollback()
            raise RuntimeError(f"Unexpected failure loading accounting data from {csv_path.name}") from e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Returned connection to pool after load_from_csv.")