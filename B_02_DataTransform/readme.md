# B_02_DataTransform: PDF Table Extraction

This project implements a Python pipeline to extract table data from a specific PDF file contained within a ZIP archive, process the data, and save the results into a zipped CSV file.

The pipeline follows principles of Clean Architecture to ensure separation of concerns, testability, and maintainability.

## Features

- Extracts a target PDF file (containing "Anexo_I" in its name) from an input ZIP archive (`Anexos.zip`).
- Uses `tabula-py` to extract all tables from the PDF pages.
- Cleans the extracted tables by removing empty rows and columns.
- Combines all valid tables into a single Pandas DataFrame.
- Renames specific columns ('OD', 'AMB') to more descriptive names.
- Saves the final processed DataFrame to a CSV file (`csvFile.csv`).
- Compresses the output CSV file into a ZIP archive (`Test_William.zip`).
- Structured using layers (application, adapters) for better organization.
- Includes unit tests (`pytest`) for core logic and adapters.

## Setup

### Prerequisites

- **Python:** Version 3.9 or higher recommended.
- **Java:** `tabula-py` requires a Java Runtime Environment (JRE) or Java Development Kit (JDK) to be installed and accessible in your system's PATH. You can download it from [Oracle Java](https://www.oracle.com/java/technologies/downloads/) or use alternatives like OpenJDK.

### Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd B_02_DataTransform
    ```

## Usage

1.  **Input Data:** Ensure the input ZIP file (`Anexos.zip`) is placed inside the `zip_anexo_1/` directory within the project root (`B_02_DataTransform/zip_anexo_1/Anexos.zip`). You can change this location by modifying `INPUT_ZIP_RELATIVE_PATH` in `src/config.py`.

2.  **Run the Pipeline:** Execute the main script as a module from the project root directory (`B_02_DataTransform/`):

    ```bash
    python -m src.main
    ```

3.  **Output:** The processed data will be saved as a zipped CSV file in the `csvFile/` directory within the project root (`B_02_DataTransform/csvFile/csv.zip`). The output directory and filenames can be configured in `src/config.py`.

## Running Tests

To run the unit tests, navigate to the project root directory (`B_02_DataTransform/`) and run `pytest`:

```bash
pytest
```

Or for more detailed output:

```bash
pytest -v
```

## Configuration

Key parameters can be adjusted in the `src/config.py` file:

- `INPUT_ZIP_RELATIVE_PATH`: Path to the input ZIP file relative to the project root.
- `TARGET_FILENAME_PART`: Substring used to identify the target PDF within the input ZIP.
- `OUTPUT_DIR_RELATIVE_PATH`: Path to the output directory relative to the project root.
- `OUTPUT_CSV_FILENAME`: Name of the CSV file inside the output ZIP.
- `FINAL_ZIP_FILENAME`: Name of the final output ZIP archive.
- `COLUMN_RENAME_MAP`: Dictionary defining how specific columns should be renamed after processing.
