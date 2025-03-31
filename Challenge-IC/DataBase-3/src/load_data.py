import logging
import mysql.connector

#Log Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root', 
    'database': 'ans_data'
}

def test_db_connection(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        print()
        logging.info("Successfully connected to the database.\n")
        connection.close()
        return True
    except mysql.connector.Error as e:
        logging.error(f"Failed to connect to the database: {e}\n")
        return False

if __name__ == "__main__":
    test_db_connection(DB_CONFIG)