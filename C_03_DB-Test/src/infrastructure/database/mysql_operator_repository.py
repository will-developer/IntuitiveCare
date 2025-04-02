# src/infrastructure/database/mysql_operator_repository.py
import logging
import time
from pathlib import Path
from mysql.connector import Error

from src.application.ports.operator_repository import OperatorRepository
from .mysql_connection_manager import MySQLConnectionManager
from .db_config import MYSQL_CSV_ENCODING

logger = logging.getLogger(__name__)

class MySqlOperatorRepository(OperatorRepository):
    def __init__(self, connection_manager: MySQLConnectionManager):
        self._conn_manager = connection_manager
        self._load_sql = """
            LOAD DATA LOCAL INFILE '{csv_path}'
            INTO TABLE operators
            CHARACTER SET {encoding}
            FIELDS TERMINATED BY ';'
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\n' -- Or '\\r\\n' if needed
            IGNORE 1 ROWS
            (
                @Registro_ANS, CNPJ, Razao_Social, Nome_Fantasia, Modalidade,
                Logradouro, Numero, Complemento, Bairro, Cidade, UF, CEP,
                @DDD, @Telefone, @Fax, Endereco_eletronico, Representante,
                Cargo_Representante, @Regiao_de_Comercializacao, @Data_Registro_ANS
            )
            SET
                Registro_ANS = @Registro_ANS,
                -- Clean potential '.0' suffixes and limit length
                DDD = LEFT(IF(@DDD LIKE '%.0', LEFT(@DDD, LENGTH(@DDD)-2), @DDD), 3),
                Telefone = LEFT(IF(@Telefone LIKE '%.0', LEFT(@Telefone, LENGTH(@Telefone)-2), @Telefone), 50),
                Fax = LEFT(IF(@Fax LIKE '%.0', LEFT(@Fax, LENGTH(@Fax)-2), @Fax), 50),
                CEP = LEFT(IF(@CEP LIKE '%.0', LEFT(@CEP, LENGTH(@CEP)-2), @CEP), 9),
                Regiao_de_Comercializacao = LEFT(IF(@Regiao_de_Comercializacao LIKE '%.0', LEFT(@Regiao_de_Comercializacao, LENGTH(@Regiao_de_Comercializacao)-2), @Regiao_de_Comercializacao), 100),
                -- Handle empty or invalid dates, converting valid ones
                Data_Registro_ANS = IF( TRIM(COALESCE(@Data_Registro_ANS, '')) = '' OR
                                        TRIM(COALESCE(@Data_Registro_ANS, '')) = '0000-00-00' OR
                                        TRIM(COALESCE(@Data_Registro_ANS, '')) = 'NULL', -- Handle explicit 'NULL' string if present
                                        NULL,
                                        STR_TO_DATE(TRIM(@Data_Registro_ANS), '%Y-%m-%d')
                                      );
        """

    def clear_all(self) -> None:
        logger.warning("Attempting to clear 'operators' table.")
        conn = None
        cursor = None
        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE operators;")
            conn.commit()
            logger.info("'operators' table cleared successfully.")
        except Error as e:
            logger.error(f"Database error while clearing operators table: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during operators table clear: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Returned connection to pool after clear_all.")

    def load_from_csv(self, csv_path: Path) -> int:
        logger.info(f"Loading operators from CSV: {csv_path.name}")
        start_time = time.time()
        affected_rows = 0
        conn = None
        cursor = None

        abs_csv_path = csv_path.resolve()
        escaped_csv_path = str(abs_csv_path).replace('\\', '\\\\')

        formatted_sql = self._load_sql.format(
            csv_path=escaped_csv_path,
            encoding=MYSQL_CSV_ENCODING
        )

        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            logger.info(f"Executing LOAD DATA for 'operators' from '{csv_path.name}'...")

            cursor.execute(formatted_sql)
            affected_rows = cursor.rowcount
            conn.commit()

            end_time = time.time()
            logger.info(f"LOAD DATA for 'operators' completed in {end_time - start_time:.2f}s. Rows affected: {affected_rows}")

            if affected_rows == 0:
                self._log_load_data_warnings(cursor, "operators")

            return affected_rows

        except Error as err:
            logger.error(f"Database error during LOAD DATA for 'operators': {err}")
            if conn:
                conn.rollback()
            if "Cannot get geometry object from data you send to the GEOMETRY field" in str(err):
                 logger.error("Potential issue with spatial data types if used.")
            if "Incorrect date value" in str(err):
                 logger.error("Potential issue with date conversion. Check source data and SQL SET clause.")
            raise RuntimeError(f"Failed to load operators from {csv_path.name}") from err
        except Exception as e:
            logger.error(f"Unexpected error during LOAD DATA for 'operators': {e}", exc_info=True)
            if conn:
                conn.rollback()
            raise RuntimeError(f"Unexpected failure loading operators from {csv_path.name}") from e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Returned connection to pool after load_from_csv.")

    def _log_load_data_warnings(self, cursor, table_name: str):
        """Helper to fetch and log warnings after LOAD DATA."""
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