import logging
import requests
from pathlib import Path
import os

#Log Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

######
BASE_URL_ACCOUNTING = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_OPERATORS_CSV = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
######

# Define project paths
CURRENT_YEAR = 2025
YEARS_TO_DOWNLOAD = [str(year) for year in range(CURRENT_YEAR - 2, CURRENT_YEAR)]

DIR = Path(__file__).resolve().parent
#Create Main Folder
DATA_DIR = DIR.parent / "data"
#Accounting Folder and save files
ACCOUNTING_DIR = DATA_DIR / "accounting"
ZIPS_DIR = ACCOUNTING_DIR / "zips"
CSVS_DIR = ACCOUNTING_DIR / "csvs"
#Operators Folder and save files
OPERATORS_DIR = DATA_DIR / "operators"
OPERATORS_CSV_PATH = OPERATORS_DIR / "operators.csv"

logging.info(f"Project paths configured.\n")  
logging.info(f"Data directory: {DATA_DIR.resolve()}\n")
logging.info(f"Years to download: {YEARS_TO_DOWNLOAD}\n")

#Function to create all files
def create_data_directories():
    dirs_create = [DATA_DIR, ACCOUNTING_DIR, ZIPS_DIR, CSVS_DIR, OPERATORS_DIR]
    for dir_path in dirs_create:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            logging.error(f"Failed to create DIR: {dir_path}: {e}\n")
    logging.info("Created data directories.\n")

#Function to download files
def download_file(url, save_path, timeout=60):
    try:
        logging.info(f"Try to download: {url}\n")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        response = requests.get(url, timeout=timeout) 
        response.raise_for_status()  

        with open(save_path, 'wb') as f:
            f.write(response.content) 

        logging.info(f"Successfully downloaded and saved to: {save_path}\n")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}\n")
        return False
    
#Download CSV Operators    
def download_operators_csv():
    logging.info("--- Starting Operators CSV Download ---\n")
    success = download_file(URL_OPERATORS_CSV, OPERATORS_CSV_PATH)
    if success:
        logging.info("Operators CSV downloaded successfully.\n")
    else:
        logging.warning("Operators CSV download failed.\n")
    logging.info("--- Finished Operators CSV Download ---\n")
    return success

if __name__ == "__main__":
    logging.info("Download started.\n")
    create_data_directories()
    download_operators_csv()
    logging.info("Download script finished\n")