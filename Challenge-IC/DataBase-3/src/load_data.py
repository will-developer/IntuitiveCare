import logging
from pathlib import Path
import mysql.connector

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

# Encoding a usar
CSV_ENCODING_MYSQL = "utf8mb4"

def test_db_connection(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        logging.info("Successfully connected to the database.\n")
        connection.close()
        return True
    except mysql.connector.Error as e:
        logging.error(f"Failed to connect to the database: {e}\n")
        return False

if __name__ == "__main__":
    test_db_connection(DB_CONFIG)