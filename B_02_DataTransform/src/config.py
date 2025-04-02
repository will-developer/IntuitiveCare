import os

# Get the absolute path to the source directory containing this config file
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# Get the project root directory (one level up from source directory)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# Input ZIP file configuration
INPUT_ZIP_RELATIVE_PATH = os.path.join('zip_anexo_1', 'Anexos.zip')  # Relative path to ZIP
INPUT_ZIP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, INPUT_ZIP_RELATIVE_PATH))  # Full absolute path

# Target file to extract from ZIP (looks for files containing this string)
TARGET_FILENAME_PART = 'Anexo_I'

# Output directory configuration
OUTPUT_DIR_RELATIVE_PATH = 'csvFile'  # Relative output directory name
OUTPUT_DIR = os.path.join(PROJECT_ROOT, OUTPUT_DIR_RELATIVE_PATH)  # Full output path
OUTPUT_CSV_FILENAME = 'csvFile.csv'  # Name for CSV file inside ZIP
FINAL_ZIP_FILENAME = 'Teste_William.zip'  # Name for final output ZIP file

# Mapping for renaming columns in the processed data
COLUMN_RENAME_MAP = {
    'OD': 'Seg. Odontológica',  # Rename 'OD' column to 'Seg. Odontológica'
    'AMB': 'Seg. Ambulatorial',  # Rename 'AMB' column to 'Seg. Ambulatorial'
}