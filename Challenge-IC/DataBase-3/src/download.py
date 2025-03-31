import logging
import requests
from pathlib import Path
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

#Function to get zip
def get_accounting_zip(year_url):
    print('\n\n#################################\n\n')
    zip_links = []
    try:
        logging.info(f"Fetching ZIP links from: {year_url}\n")
        response = requests.get(year_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find a tags
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.zip'):
                full_url = urljoin(year_url, href)
                zip_links.append(full_url)
                logging.debug(f"Found ZIP link: {full_url}\n")

        if not zip_links:
            logging.warning(f"No .zip files found at {year_url}\n")
        else:
             logging.info(f"Found {len(zip_links)} ZIP file links for {year_url.strip('/').split('/')[-1]}.\n")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch or parse {year_url}: {e}\n")
    except Exception as e:
        logging.error(f"Unexpected error finding ZIP links at {year_url}: {e}\n")

    return zip_links

def download_accounting():
    logging.info("\n--- Starting Accounting Statements Download ---\n")
    all_zip_urls = []
    for year in YEARS_TO_DOWNLOAD:
        year_directory_url = urljoin(BASE_URL_ACCOUNTING, f"{year}/")
        year_zip_urls = get_accounting_zip(year_directory_url)
        all_zip_urls.extend(year_zip_urls)

    if not all_zip_urls:
        logging.warning("Nothing Found in zip function\n")
        return False

    logging.info(f"------------TEST: Found a total of {len(all_zip_urls)} ZIP\n")
    return True 

if __name__ == "__main__":
    logging.info("Download started.\n")
    create_data_directories()
    download_operators_csv()
    download_accounting()
    logging.info("\n\nDownload script finished\n")