import logging
from pathlib import Path
import mysql.connector
import pandas
import os
from datetime import date
import re

#Log Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root', 
    'database': 'ans_data'
}

# Define project paths
print()
DIR = Path(__file__).resolve().parent
#Create Main Folder
DATA_DIR = DIR.parent / "data"
ACCOUNTING_DIR = DATA_DIR / "accounting"
OPERATORS_DIR = DATA_DIR / "operators"
OPERATORS_FILE = OPERATORS_DIR / "operators.csv" 

# Encoding a usar
CSV_ENCODINGS = ['utf-8', 'latin-1', 'cp1252']

def test_db_connection(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        logging.info("Successfully connected to the database.\n")
        connection.close()
        return True
    except mysql.connector.Error as e:
        logging.error(f"Failed to connect to the database: {e}\n")
        if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            logging.error(f"Database '{db_config.get('database')}' does not exist.")
        elif e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Access denied. Check username and password in DB_CONFIG.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during DB connection test: {e}\n")
        return False

 #Reader CSV Functions
def read_csv(path, separator=';', decimal_sep=','):
    if not path.is_file():
        logging.error(f"CSV file not found at path: {path}\n")
        return None
    try:
        for encoding in CSV_ENCODINGS:
            try:
                data_frame = pandas.read_csv(path, sep=separator, encoding=encoding, decimal=decimal_sep, low_memory=False)
                logging.info(f"CSV '{path.name}' read successfully with encoding '{encoding}'.\n")
                data_frame.columns = data_frame.columns.str.strip()
                return data_frame
            except UnicodeDecodeError:
                logging.warning(f"Failed to read '{path.name}' with encoding '{encoding}'. Trying next...\n")
            except Exception as e:
                 logging.error(f"Error reading CSV {path.name} with encoding {encoding}: {e}\n")

        logging.error(f"Could not read CSV '{path.name}' with any encoding in {CSV_ENCODINGS}.\n")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading CSV {path}: {e}\n")
        return None

 #Data Loading Functions
def load_operators(db_config, df):
    logging.info("--- Starting 'operators' table load (row-by-row) ---")
    connection = None
    cursor = None
    insert_count = 0
    error_count = 0
    processed_rows = 0

    if df is None or df.empty:
        logging.error("Operator DataFrame is None or empty. Aborting operator load.")
        return False

    try:
        config_with_autocommit = db_config.copy()
        config_with_autocommit['autocommit'] = False
        connection = mysql.connector.connect(**config_with_autocommit)
        if not connection or not connection.is_connected():
             logging.error("Failed to establish connection for loading operators.")
             return False

        cursor = connection.cursor()

        logging.warning("Truncating 'operators' table before loading...")
        cursor.execute("TRUNCATE TABLE operators;")
        logging.info("'operators' table truncated.")

        csv_to_db_map = {
            'Registro_ANS': 'Registro_ANS', 'CNPJ': 'CNPJ', 'Razao_Social': 'Razao_Social',
            'Nome_Fantasia': 'Nome_Fantasia', 'Modalidade': 'Modalidade', 'Logradouro': 'Logradouro',
            'Numero': 'Numero', 'Complemento': 'Complemento', 'Bairro': 'Bairro',
            'Cidade': 'Cidade', 'UF': 'UF', 'CEP': 'CEP', 'DDD': 'DDD',
            'Telefone': 'Telefone', 'Fax': 'Fax', 'Endereco_eletronico': 'Endereco_eletronico',
            'Representante': 'Representante', 'Cargo_Representante': 'Cargo_Representante',
            'Regiao_de_Comercializacao': 'Regiao_de_Comercializacao', 'Data_Registro_ANS': 'Data_Registro_ANS'
        }

        db_cols = []
        cols_in_csv_order = []
        for col_csv in df.columns:
            col_csv_stripped = col_csv.strip()
            if col_csv_stripped in csv_to_db_map:
                db_cols.append(csv_to_db_map[col_csv_stripped])
                cols_in_csv_order.append(col_csv)

        if not db_cols:
             logging.error("No columns from CSV matched the database map for operators.\n")
             return False

        placeholders = ', '.join(['%s'] * len(db_cols))
        sql = f"INSERT INTO operators ({', '.join(db_cols)}) VALUES ({placeholders})"
        logging.debug(f"Insert SQL for operators: {sql}")

        total_rows = len(df)
        logging.info(f"Attempting to insert {total_rows} rows into 'operators'...\n")

        for i, row_tuple in enumerate(df[cols_in_csv_order].itertuples(index=False, name=None)):
            processed_rows += 1
            raw_values = list(row_tuple)
            processed_values = []

            try:
                for idx, value in enumerate(raw_values):
                    db_col_name = db_cols[idx]
                    processed = None

                    if pandas.isna(value):
                        processed = None
                    elif db_col_name == 'Data_Registro_ANS':
                        try:
                            pd_date = pandas.to_datetime(value, errors='coerce')
                            processed = pd_date.strftime('%Y-%m-%d') if pandas.notna(pd_date) else None
                        except Exception:
                             processed = None
                    elif db_col_name in ['DDD', 'Telefone', 'Fax', 'CEP', 'CNPJ', 'Regiao_de_Comercializacao']:
                        s_value = str(value).strip()
                        if s_value.endswith('.0'):
                            s_value = s_value[:-2]
                        if db_col_name == 'DDD': processed = s_value[:3]
                        elif db_col_name == 'CEP': processed = s_value[:9]
                        elif db_col_name == 'CNPJ': processed = s_value[:18]
                        elif db_col_name == 'Telefone' or db_col_name == 'Fax': processed = s_value[:50]
                        elif db_col_name == 'Regiao_de_Comercializacao': processed = s_value[:100]
                        else: processed = s_value
                    elif db_col_name == 'Registro_ANS':
                         try: processed = int(value)
                         except (ValueError, TypeError): processed = None
                    else:
                        s_value = str(value).strip()
                        if db_col_name in ['Razao_Social', 'Nome_Fantasia', 'Logradouro', 'Endereco_eletronico', 'Representante']: processed = s_value[:255]
                        elif db_col_name in ['Modalidade', 'Complemento', 'Bairro', 'Cidade', 'Cargo_Representante']: processed = s_value[:100]
                        elif db_col_name == 'Numero': processed = s_value[:50]
                        elif db_col_name == 'UF': processed = s_value[:2]
                        else: processed = s_value

                    processed_values.append(processed)

                cursor.execute(sql, tuple(processed_values))
                insert_count += 1

            except mysql.connector.Error as insert_err:
                logging.error(f"Row {i+1} (Operator): DB Error inserting data: {insert_err}. Processed Data: {processed_values}\n")
                error_count += 1
            except Exception as e:
                logging.error(f"Row {i+1} (Operator): Unexpected error processing/inserting data: {e}. Processed Data: {processed_values}\n")
                error_count += 1

            if processed_rows % 100 == 0 or processed_rows == total_rows:
                logging.info(f"Processed {processed_rows}/{total_rows} operator rows...\n")

        if error_count == 0:
            connection.commit()
            logging.info(f"Transaction committed for 'operators'. Inserted: {insert_count}\n")
        else:
            logging.warning(f"Rolling back 'operators' transaction due to {error_count} errors.\n")
            connection.rollback()

        logging.info(f"'operators' load finished. Attempted: {total_rows}, Inserted: {insert_count}, Errors: {error_count}\n")
        return error_count == 0

    except mysql.connector.Error as e:
        logging.error(f"A database error occurred during the 'operators' loading process: {e}\n", exc_info=False)
        if connection and connection.is_connected(): connection.rollback()
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during the 'operators' loading process: {e}\n", exc_info=True)
        if connection and connection.is_connected(): connection.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logging.info("Local connection for 'load_operators' closed.\n")


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

def load_accounting_statements(db_config, csvs_dir_path):
    logging.info("--- Starting 'accounting' table load (row-by-row) ---")
    total_inserted_all_files = 0
    total_errors_all_files = 0
    processed_files = 0

    if not csvs_dir_path.is_dir():
        logging.error(f"Accounting CSV directory not found: {csvs_dir_path}")
        return

    csv_files = list(csvs_dir_path.glob('*.csv'))
    if not csv_files:
        logging.warning(f"No CSV files found in {csvs_dir_path}")
        return

    logging.info(f"Found {len(csv_files)} accounting CSV files to process.")

    connection_truncate = None
    cursor_truncate = None
    try:
        config_truncate = db_config.copy()
        config_truncate['autocommit'] = True
        connection_truncate = mysql.connector.connect(**config_truncate)
        cursor_truncate = connection_truncate.cursor()
        logging.warning("Truncating 'accounting' table before loading files...")
        cursor_truncate.execute("TRUNCATE TABLE accounting;")
        logging.info("'accounting' table truncated.")
    except mysql.connector.Error as e:
        logging.error(f"Failed to truncate 'accounting' table: {e}. Aborting accounting load.")
        return
    finally:
        if cursor_truncate: cursor_truncate.close()
        if connection_truncate and connection_truncate.is_connected(): connection_truncate.close()

    for file_path in csv_files:
        processed_files += 1
        logging.info(f"Processing file {processed_files}/{len(csv_files)}: {file_path.name}")
        df = read_csv(file_path, separator=';', decimal_sep=',')
        if df is None or df.empty:
            logging.warning(f"Skipping file {file_path.name} due to read error or empty content.")
            total_errors_all_files += 1
            continue
        trimestre_ref = parse_trimestre_from_filename(file_path)
        if trimestre_ref is None:
            logging.error(f"Skipping file {file_path.name}: Could not determine quarter reference date.")
            total_errors_all_files += 1
            continue

        connection = None
        cursor = None
        insert_count_file = 0
        error_count_file = 0
        processed_rows_file = 0
        try:
            config_with_autocommit = db_config.copy()
            config_with_autocommit['autocommit'] = False
            connection = mysql.connector.connect(**config_with_autocommit)
            if not connection or not connection.is_connected():
                 logging.error(f"Failed to establish connection for loading {file_path.name}.")
                 total_errors_all_files += 1
                 continue
            cursor = connection.cursor()
            csv_to_db_map = {
                'REG_ANS': 'reg_ans', 'CD_CONTA_CONTABIL': 'cd_conta_contabil',
                'DESCRICAO': 'descricao', 'VL_SALDO_INICIAL': 'vl_saldo_inicial',
                'VL_SALDO_FINAL': 'vl_saldo_final'
            }
            db_cols = ['trimestre_referencia']
            cols_in_csv_order = []
            for col_csv in df.columns:
                 col_csv_stripped = col_csv.strip()
                 if col_csv_stripped in ['REG_ANS', 'CD_CONTA_CONTABIL', 'DESCRICAO', 'VL_SALDO_INICIAL', 'VL_SALDO_FINAL']:
                      db_cols.append(csv_to_db_map[col_csv_stripped])
                      cols_in_csv_order.append(col_csv)
            if len(db_cols) <= 1:
                 logging.error(f"No matching columns found in {file_path.name} based on map. Skipping file.")
                 total_errors_all_files += 1
                 continue
            placeholders = ', '.join(['%s'] * len(db_cols))
            sql = f"INSERT INTO accounting ({', '.join(db_cols)}) VALUES ({placeholders})"
            logging.debug(f"Insert SQL for accounting: {sql}")
            total_rows = len(df)
            logging.info(f"Attempting to insert {total_rows} rows from {file_path.name}...")
            for i, row_tuple in enumerate(df[cols_in_csv_order].itertuples(index=False, name=None)):
                processed_rows_file += 1
                values = [trimestre_ref.strftime('%Y-%m-%d')] + list(row_tuple)
                processed_values = [None if pandas.isna(v) else v for v in values]
                try:
                    cursor.execute(sql, tuple(processed_values))
                    insert_count_file += 1
                except mysql.connector.Error as insert_err:
                    if insert_err.errno == 1452: logging.warning(f"Row {i+1} ({file_path.name}): FK Error: {insert_err}. Operator likely missing. Data: {processed_values}\n")
                    else: logging.error(f"Row {i+1} ({file_path.name}): DB Error inserting data: {insert_err}. Data: {processed_values}\n")
                    error_count_file += 1
                except Exception as e:
                    logging.error(f"Row {i+1} ({file_path.name}): Unexpected error processing/inserting data: {e}. Data: {processed_values}\n")
                    error_count_file += 1
                if processed_rows_file % 5000 == 0 or processed_rows_file == total_rows:
                    logging.info(f"Processed {processed_rows_file}/{total_rows} rows from {file_path.name}...\n")
            if error_count_file == 0:
                connection.commit()
                logging.info(f"Transaction committed for {file_path.name}. Inserted: {insert_count_file}\n")
            else:
                logging.warning(f"Rolling back transaction for {file_path.name} due to {error_count_file} errors.\n")
                connection.rollback()
            logging.info(f"File {file_path.name} finished. Attempted: {total_rows}, Inserted: {insert_count_file}, Errors: {error_count_file}\n")
            total_inserted_all_files += insert_count_file
            total_errors_all_files += error_count_file
        except Exception as e:
            logging.error(f"An error occurred during the loading process for file {file_path.name}: {e}\n", exc_info=True)
            total_errors_all_files += 1
            if connection and connection.is_connected(): connection.rollback()
        finally:
            if cursor: cursor.close()
            if connection and connection.is_connected():
                connection.close()
                logging.debug(f"Local connection for {file_path.name} closed.\n")
    logging.info(f"--- 'accounting' table load finished. Processed {processed_files} files. Total Inserted: {total_inserted_all_files}, Total Errors: {total_errors_all_files} ---")


if __name__ == "__main__":
    logging.info("--- STARTING DATA LOADING PROCESS ---\n")
    connection_ok = test_db_connection(DB_CONFIG)

    if connection_ok:
        operators_loaded_successfully = False
        try:
            operators_df = read_csv(OPERATORS_FILE, separator=';', decimal_sep='.')

            if operators_df is not None:
                logging.info(f"Operator DataFrame loaded successfully. Shape: {operators_df.shape}\n")
                operators_loaded_successfully = load_operators(DB_CONFIG, operators_df)
            else:
                logging.error("Skipping operator loading due to CSV read failure.\n")

            if operators_loaded_successfully:
                 load_accounting_statements(DB_CONFIG, CSVS_DIR)
            else:
                 logging.warning("Skipping accounting statements loading because operator loading failed or had errors.\n")

        except Exception as main_e:
             logging.error(f"An error occurred in the main loading block: {main_e}\n", exc_info=True)

    else:
        logging.error("Initial database connection test failed. Aborting data loading.\n")

    logging.info("--- DATA LOADING PROCESS FINISHED ---\n")