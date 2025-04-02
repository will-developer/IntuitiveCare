import logging
import time
from pathlib import Path
from mysql.connector import Error
from typing import TYPE_CHECKING

from src.application.ports.operator_repository import OperatorRepository
if TYPE_CHECKING:
    from .mysql_connection_manager import MySQLConnectionManager

logger = logging.getLogger(__name__)
MYSQL_CSV_ENCODING = 'utf8mb4'  # Supports full Unicode including emojis

class MySqlOperatorRepository(OperatorRepository):
    """MySQL implementation for bulk loading operator/healthcare provider data."""
    
    def __init__(self, connection_manager: 'MySQLConnectionManager'):
        self._conn_manager = connection_manager
        
        # SQL template for LOAD DATA command with:
        # - Special handling for Brazilian ANS registry data
        # - Data cleaning for numeric fields (removing .0 suffixes)
        # - Proper date parsing for registration dates
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
                DDD = LEFT(IF(@DDD LIKE '%.0', LEFT(@DDD, LENGTH(@DDD)-2), @DDD), 3),
                Telefone = LEFT(IF(@Telefone LIKE '%.0', LEFT(@Telefone, LENGTH(@Telefone)-2), @Telefone), 50),
                Fax = LEFT(IF(@Fax LIKE '%.0', LEFT(@Fax, LENGTH(@Fax)-2), @Fax), 50),
                CEP = LEFT(IF(@CEP LIKE '%.0', LEFT(@CEP, LENGTH(@CEP)-2), @CEP), 9),
                Regiao_de_Comercializacao = LEFT(IF(@Regiao_de_Comercializacao LIKE '%.0', 
                    LEFT(@Regiao_de_Comercializacao, LENGTH(@Regiao_de_Comercializacao)-2), 
                    @Regiao_de_Comercializacao), 100),
                Data_Registro_ANS = IF( TRIM(COALESCE(@Data_Registro_ANS, '')) = '' OR
                                    TRIM(COALESCE(@Data_Registro_ANS, '')) = '0000-00-00' OR
                                    TRIM(COALESCE(@Data_Registro_ANS, '')) = 'NULL',
                                    NULL,
                                    STR_TO_DATE(TRIM(@Data_Registro_ANS), '%Y-%m-%d')
                                  );
        """

    def clear_all(self) -> None:
        """Truncates the operators table, temporarily disabling foreign key checks."""
        logger.warning("Clearing 'operators' table (all data will be lost)")
        conn = None
        cursor = None
        fk_check_original_value = 1  # Default MySQL FK check state

        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            # Disable FK checks to allow TRUNCATE even with referential constraints
            logger.debug("Temporarily disabling foreign key checks")
            cursor.execute("SET SESSION foreign_key_checks = 0;")

            cursor.execute("TRUNCATE TABLE operators;")
            conn.commit()
            logger.info("Successfully cleared operators table")

        except Error as e:
            logger.error(f"Database error clearing operators: {e}")
            if conn: conn.rollback()
            raise RuntimeError("Failed to clear operators table") from e
        finally:
            # Critical: Always restore FK checks and clean up resources
            if cursor:
                try:
                    logger.debug(f"Restoring foreign key checks to {fk_check_original_value}")
                    cursor.execute(f"SET SESSION foreign_key_checks = {fk_check_original_value};")
                    conn.commit()
                except Error as fk_err:
                    logger.error(f"Failed to restore FK checks: {fk_err}")
                finally:
                    cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Connection returned to pool")

    def load_from_csv(self, csv_path: Path) -> int:
        """Bulk loads operator data from CSV using MySQL's optimized LOAD DATA.
        """
        logger.info(f"Loading operators from: {csv_path.name}")
        start_time = time.time()
        
        # Prepare path with proper escaping for MySQL
        abs_csv_path = csv_path.resolve()
        escaped_csv_path = str(abs_csv_path).replace('\\', '\\\\')

        formatted_sql = self._load_sql.format(
            csv_path=escaped_csv_path,
            encoding=MYSQL_CSV_ENCODING
        )

        conn = None
        cursor = None
        try:
            conn = self._conn_manager.get_connection()
            cursor = conn.cursor()

            logger.info(f"Executing LOAD DATA for {csv_path.name}")
            cursor.execute(formatted_sql)
            affected_rows = cursor.rowcount
            conn.commit()

            logger.info(f"Loaded {affected_rows} rows in {time.time()-start_time:.2f}s")
            
            if affected_rows == 0:
                self._log_load_data_warnings(cursor, "operators")

            return affected_rows

        except Error as err:
            logger.error(f"Database error loading operators: {err}")
            if conn: conn.rollback()
            raise RuntimeError(f"Failed to load {csv_path.name}") from err
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Connection returned to pool")

    def _log_load_data_warnings(self, cursor, table_name: str):
        """Logs MySQL warnings when LOAD DATA completes with issues."""
        try:
            cursor.execute("SHOW WARNINGS")
            warnings = cursor.fetchall()
            if warnings:
                logger.warning(f"MySQL warnings during load:")
                for level, code, message in warnings:
                    logger.warning(f"[{level} {code}] {message}")
            else:
                logger.warning(f"No rows loaded - check file format and encoding")
        except Error as warn_err:
            logger.error(f"Couldn't retrieve warnings: {warn_err}")