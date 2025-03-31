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
CSV_ENCODING_MYSQL = ['utf-8', 'latin-1', 'cp1252']

def test_db_connection(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        logging.info("Successfully connected to the database.\n")
        connection.close()
        return True
    except mysql.connector.Error as e:
        logging.error(f"Failed to connect to the database: {e}\n")
        return False
    
def read_csv(path, separator=';', decimal_sep=','):
    try:
        for encoding in CSV_ENCODING_MYSQL:
            try:
                data_frame = pandas.read_csv(path, sep=separator, encoding=encoding, decimal=decimal_sep, low_memory=False)

                logging.info(f"CSV '{os.path.basename(path)}' read successfully with encoding '{encoding}'.\n")

                data_frame.columns = data_frame.columns.str.strip()  # Strip column names
                return data_frame
            
            except UnicodeDecodeError:
                logging.warning(f"Failed to read '{os.path.basename(path)}' with encoding '{encoding}'. Trying next...\n")
              
        logging.error(f"Could not read CSV '{os.path.basename(path)}' with any encoding in {CSV_ENCODING_MYSQL}.\n")
        return None 
    
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading CSV {path}: {e}\n")
        return None

if __name__ == "__main__":
    connection  = test_db_connection(DB_CONFIG)

    data_frame = read_csv(OPERATORS_FILE)
    if connection and data_frame is not None:
        logging.info(f"DataFrame loaded successfully. Shape: {data_frame.shape}\n")
    else:
        logging.error("Failed to load DataFrame.\n")