import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)

INPUT_ZIP_RELATIVE_PATH = os.path.join('..', 'WebScraping', 'pdfs', 'Anexos.zip')
INPUT_ZIP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, INPUT_ZIP_RELATIVE_PATH))

TARGET_FILENAME_PART = 'Anexo_I'

OUTPUT_DIR_RELATIVE_PATH = 'csvFile'
OUTPUT_DIR = os.path.join(PROJECT_ROOT, OUTPUT_DIR_RELATIVE_PATH)
OUTPUT_CSV_FILENAME = 'csvFile.csv'
FINAL_ZIP_FILENAME = 'csv.zip'

COLUMN_RENAME_MAP = {
    'OD': 'Dental Insurance',
    'AMB': 'Ambulatorial Insurance',
}