import requests
from pathlib import Path
import os
import logging

#Log Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Create Dir for place data
def create_data_dir():
    local_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    data_dir = local_dir.parent / "data" / "download"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

######
BASE_URL_ACCOUNTING = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_OPERATORS_CSV = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
######

# Define project paths
CURRENT_YEAR = 2025
YEARS_TO_DOWNLOAD = [str(year) for year in range(CURRENT_YEAR - 2, CURRENT_YEAR)]
#Create Main Folder
DATA_DIR = os.path.join("..", "data")
#Accounting Folder and save files
ACCOUNTING_DIR = os.path.join(DATA_DIR, "accounting")
ZIPS_DIR = os.path.join(ACCOUNTING_DIR, "zips")
CSVS_DIR = os.path.join(ACCOUNTING_DIR, "csvs")
#Operators Folder and save files
OPERATORS_DIR = os.path.join(DATA_DIR, "operators") 
OPERATORS_CSV_PATH = os.path.join(OPERATORS_DIR, "operators.csv")

logging.info(f"\nProject paths configured.")  
logging.info(f"\nData directory: {os.path.abspath(DATA_DIR)}")
logging.info(f"\nYears to download: {YEARS_TO_DOWNLOAD}")

def download_file(url, save_path, timeout=60):
    try:
        logging.info(f"Try to download: {url}")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        response = requests.get(url, timeout=timeout) 
        response.raise_for_status()  

        with open(save_path, 'wb') as f:
            f.write(response.content) 

        logging.info(f"Successfully downloaded and saved to: {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")
        return False

if __name__ == "__main__":
    logging.info("\nDownload started.")
    download_file(URL_OPERATORS_CSV, OPERATORS_CSV_PATH)
    logging.info("\nDownload script finished")