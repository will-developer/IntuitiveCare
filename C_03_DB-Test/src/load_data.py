import logging
from pathlib import Path
import mysql.connector
import pandas
import os
from datetime import date
import re
from decimal import Decimal, InvalidOperation
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ans_data',
    'allow_local_infile': True
}

print()
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    ACCOUNTING_DIR = DATA_DIR / "accounting"
    CSVS_DIR = ACCOUNTING_DIR / "csvs"
    OPERATORS_DIR = DATA_DIR / "operators"
    OPERATORS_FILE = OPERATORS_DIR / "operators.csv"
    logging.info(f"Project Root: {PROJECT_ROOT}")
    logging.info(f"Operators CSV Path: {OPERATORS_FILE}")
    logging.info(f"Accounting CSVs Dir: {CSVS_DIR}")
except NameError:
    logging.error("Could not determine script directory automatically.")
    PROJECT_ROOT = Path('.')
    DATA_DIR = PROJECT_ROOT / "data"
    ACCOUNTING_DIR = DATA_DIR / "accounting"
    CSVS_DIR = ACCOUNTING_DIR / "csvs"
    OPERATORS_DIR = DATA_DIR / "operators"
    OPERATORS_FILE = OPERATORS_DIR / "operators.csv"


CSV_ENCODINGS = ['utf-8', 'latin-1', 'cp1252']
CSV_ENCODING_MYSQL = 'utf8mb4'

def get_db_connection(db_config):
    try:
        cnx = mysql.connector.connect(**db_config)
        logging.info("Successfully connected to the database (allow_local_infile=True).\n")
        return cnx
    except mysql.connector.Error as e:
        logging.error(f"Failed to connect to the database: {e}\n")
        if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            logging.error(f"Database '{db_config.get('database')}' does not exist.")
        elif e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Access denied. Check username and password in DB_CONFIG.")
        elif 'allow_local_infile' in str(e):
             logging.error("Error: LOAD DATA LOCAL INFILE probably not enabled on server or client connection.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during DB connection test: {e}\n")
        return None

def execute_load_data(cnx, cursor, table_name, csv_path, load_sql):
    start_time = time.time()
    success = False
    affected_rows = 0
    try:
        logging.info(f"Executing LOAD DATA LOCAL INFILE for '{table_name}' from '{csv_path.name}'...")
        escaped_csv_path = str(csv_path).replace('\\', '\\\\')
        formatted_sql = load_sql.format(csv_path=escaped_csv_path, encoding=CSV_ENCODING_MYSQL)

        cursor.execute(formatted_sql)
        cnx.commit()
        affected_rows = cursor.rowcount
        end_time = time.time()
        logging.info(f"LOAD DATA for '{table_name}' completed in {end_time - start_time:.2f}s. Rows affected: {affected_rows}\n")

        if affected_rows == 0:
             cursor.execute("SHOW WARNINGS")
             warnings = cursor.fetchall()
             if warnings:
                  logging.warning(f"LOAD DATA for '{table_name}' affected 0 rows but generated warnings:")
                  for warn in warnings: logging.warning(f"  - {warn}")
             else:
                  logging.warning(f"LOAD DATA for '{table_name}' affected 0 rows. Check delimiters, encoding, file content, and SQL SET clauses.")

        success = True

    except mysql.connector.Error as err:
        logging.error(f"Error during LOAD DATA INFILE for '{table_name}': {err}\n")
        try:
            cnx.rollback()
        except Exception as rb_err:
            logging.error(f"Error during rollback for '{table_name}': {rb_err}\n")
    except Exception as e:
        logging.error(f"Unexpected error during LOAD DATA INFILE for '{table_name}': {e}\n", exc_info=True)
        try:
            cnx.rollback()
        except Exception as rb_err:
            logging.error(f"Error during rollback for '{table_name}': {rb_err}\n")

    return success, affected_rows


def parse_trimestre_from_filename(filename):
    match = re.search(r'(\d)T(\d{4})|(\d{4})_(\d)T', filename.name, re.IGNORECASE)
    if match:
        if match.group(1) and match.group(2): trimestre, ano = int(match.group(1)), int(match.group(2))
        elif match.group(3) and match.group(4): ano, trimestre = int(match.group(3)), int(match.group(4))
        else: return None
        if 1 <= trimestre <= 4:
            month = trimestre * 3
            day = 31 if month in [3, 12] else 30
            try: return date(ano, month, day)
            except ValueError:
                 if month == 6: return date(ano, month, 30)
                 if month == 9: return date(ano, month, 30)
                 logging.warning(f"Invalid date calculated for {filename.name}: {ano}-{month}-{day}\n")
                 return None
    logging.warning(f"Could not extract year/quarter from filename: {filename.name}\n")
    return None


if __name__ == "__main__":
    logging.info("--- STARTING DATA LOADING PROCESS (LOAD DATA INFILE) ---\n")
    connection = None
    cursor = None

    try:
        config_main = DB_CONFIG.copy()
        config_main['autocommit'] = True
        connection = get_db_connection(config_main)
        if not connection or not connection.is_connected():
             raise Exception("Failed to establish main database connection for cleanup.")

        cursor = connection.cursor()

        logging.warning("Disabling foreign key checks for cleanup...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        logging.warning("Truncating 'accounting' table...")
        cursor.execute("TRUNCATE TABLE accounting;")
        logging.info("'accounting' table truncated.")
        logging.warning("Truncating 'operators' table...")
        cursor.execute("TRUNCATE TABLE operators;")
        logging.info("'operators' table truncated.")
        logging.info("Re-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        logging.info("Pre-load cleanup finished.")

        cursor.close()
        connection.close()
        logging.info("Cleanup connection closed.")
        connection = None
        cursor = None

        connection = get_db_connection(DB_CONFIG)
        if not connection or not connection.is_connected():
             raise Exception("Failed to establish database connection for loading.")
        cursor = connection.cursor()

        sql_load_operadoras = """
            LOAD DATA LOCAL INFILE '{csv_path}'
            INTO TABLE operators
            CHARACTER SET {encoding}
            FIELDS TERMINATED BY ';'
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\n'
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
                Regiao_de_Comercializacao = LEFT(IF(@Regiao_de_Comercializacao LIKE '%.0', LEFT(@Regiao_de_Comercializacao, LENGTH(@Regiao_de_Comercializacao)-2), @Regiao_de_Comercializacao), 100),
                Data_Registro_ANS = IF( TRIM(COALESCE(@Data_Registro_ANS, '')) = '' OR TRIM(COALESCE(@Data_Registro_ANS, '')) = '0000-00-00',
                                        NULL,
                                        STR_TO_DATE(TRIM(@Data_Registro_ANS), '%Y-%m-%d')
                                      );
        """
        success_op, count_op = execute_load_data(connection, cursor, "operators", OPERATORS_FILE, sql_load_operadoras)

        if success_op and count_op > 0:
            csv_files = list(CSVS_DIR.glob('*.csv'))
            if not csv_files:
                logging.warning(f"No accounting CSV files found in {CSVS_DIR}")
            else:
                logging.info(f"Starting load for {len(csv_files)} accounting statement files...")
                total_demonstracoes_count = 0
                for file_path in csv_files:
                    trimestre_ref = parse_trimestre_from_filename(file_path)
                    if trimestre_ref is None:
                        logging.error(f"Skipping {file_path.name}: could not determine quarter.")
                        continue

                    sql_load_demonstracoes = """
                        LOAD DATA LOCAL INFILE '{csv_path}'
                        INTO TABLE accounting
                        CHARACTER SET {encoding}
                        FIELDS TERMINATED BY ';'
                        OPTIONALLY ENCLOSED BY '"'
                        LINES TERMINATED BY '\\n'
                        IGNORE 1 ROWS
                        (
                            @DATA_CSV, reg_ans, cd_conta_contabil, descricao,
                            @VL_SALDO_INICIAL, @VL_SALDO_FINAL
                        )
                        SET
                            trimestre_referencia = '{trimestre_ref_sql}',
                            vl_saldo_inicial = IF(TRIM(COALESCE(@VL_SALDO_INICIAL,'')) REGEXP '^-?[0-9,.]+$',
                                                CAST(REPLACE(REPLACE(TRIM(@VL_SALDO_INICIAL), '.', ''), ',', '.') AS DECIMAL(18,2)),
                                                NULL),
                            vl_saldo_final = IF(TRIM(COALESCE(@VL_SALDO_FINAL,'')) REGEXP '^-?[0-9,.]+$',
                                              CAST(REPLACE(REPLACE(TRIM(@VL_SALDO_FINAL), '.', ''), ',', '.') AS DECIMAL(18,2)),
                                              NULL),
                            cd_conta_contabil = LEFT(TRIM(cd_conta_contabil), 50),
                            descricao = LEFT(TRIM(descricao), 500);
                    """
                    formatted_sql_demonstracoes = sql_load_demonstracoes.format(
                        csv_path=str(file_path).replace('\\', '\\\\'),
                        encoding=CSV_ENCODING_MYSQL,
                        trimestre_ref_sql=trimestre_ref.strftime('%Y-%m-%d')
                    )
                    success_dem, count_dem = execute_load_data(connection, cursor, f"accounting ({file_path.name})", file_path, formatted_sql_demonstracoes)
                    if success_dem:
                        total_demonstracoes_count += count_dem

                logging.info(f"Accounting statements load finished. Total rows affected across files: {total_demonstracoes_count}\n")
        elif not success_op:
            logging.error("Skipping accounting statements load due to operator load failure.\n")
        else:
             logging.error("Skipping accounting statements load because no operators were loaded.\n")

    except mysql.connector.Error as db_err:
         logging.error(f"A database error occurred in the main block: {db_err}\n", exc_info=False)
    except Exception as main_e:
         logging.error(f"An error occurred in the main loading block: {main_e}\n", exc_info=True)
    finally:
        if cursor:
             try: cursor.close()
             except: pass
        if connection and connection.is_connected():
             try: connection.close()
             except: pass
             logging.info("Main database connection closed.\n")

    logging.info("--- DATA LOADING PROCESS FINISHED ---\n")