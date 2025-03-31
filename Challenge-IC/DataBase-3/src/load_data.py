import logging
from pathlib import Path
import mysql.connector
import pandas
import os

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
        return

    try:
        config_with_autocommit = db_config.copy()
        config_with_autocommit['autocommit'] = False
        connection = mysql.connector.connect(**config_with_autocommit)
        if not connection or not connection.is_connected():
             logging.error("Failed to establish connection for loading operators.")
             return

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
             logging.error("No columns from CSV matched the database map. Check CSV column names and csv_to_db_map.\n")
             return

        placeholders = ', '.join(['%s'] * len(db_cols))
        sql = f"INSERT INTO operators ({', '.join(db_cols)}) VALUES ({placeholders})"
        logging.debug(f"Insert SQL: {sql}")

        total_rows = len(df)
        logging.info(f"Attempting to insert {total_rows} rows into 'operators'...\n")

        for i, row_tuple in enumerate(df[cols_in_csv_order].itertuples(index=False, name=None)):
            processed_rows += 1
            values = list(row_tuple)

            processed_values = [None if pandas.isna(v) else v for v in values]

            try:
                cursor.execute(sql, tuple(processed_values))
                insert_count += 1
            except mysql.connector.Error as insert_err:
                logging.error(f"Row {i+1}: DB Error inserting data: {insert_err}. Data: {processed_values}\n")
                error_count += 1
            except Exception as e:
                logging.error(f"Row {i+1}: Unexpected error processing/inserting data: {e}. Data: {processed_values}\n")
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

    except Exception as e:
        logging.error(f"An error occurred during the 'operators' loading process: {e}\n", exc_info=True)
        if connection and connection.is_connected():
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logging.info("Local connection for 'load_operators' closed.\n")


if __name__ == "__main__":
    logging.info("--- STARTING DATA LOADING PROCESS ---\n")
    connection_ok = test_db_connection(DB_CONFIG)

    if connection_ok:
        try:
            operators_df = read_csv(OPERATORS_FILE, separator=';', decimal_sep='.')

            if operators_df is not None:
                logging.info(f"DataFrame loaded successfully. Shape: {operators_df.shape}\n")
                load_operators(DB_CONFIG, operators_df)
            else:
                logging.error("Skipping operator loading due to CSV read failure.\n")

            logging.info("Accounting statements loading not yet implemented.\n")

        except Exception as main_e:
             logging.error(f"An error occurred in the main loading block: {main_e}\n", exc_info=True)

    else:
        logging.error("Initial database connection test failed. Aborting data loading.\n")

    logging.info("--- DATA LOADING PROCESS FINISHED ---\n")