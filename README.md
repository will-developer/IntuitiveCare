## Overview

This repository contains a collection of projects designed to interact with data from the Brazilian National Supplementary Health Agency (ANS - Agência Nacional de Saúde Suplementar). The components cover various stages of a data pipeline:

1.  **Web Scraping:** Downloading specific PDF annexes from the ANS website.
2.  **Data Extraction:** Processing downloaded PDFs to extract tabular data.
3.  **Data Loading:** Fetching public operator and accounting data (CSVs) and loading it into a MySQL database.
4.  **Data Searching:** Providing a web-based interface (Flask + Vue.js) to search through operator data.

Each component is organized into its own subfolder with detailed instructions.

## Repository Structure

This repository is organized into the following main components:

- **`A_01_WebScraping/`**: Contains a Python script to scrape and download specific PDF annexes ("Anexo I", "Anexo II") related to 'Atualização do Rol de Procedimentos' from the ANS website, archiving them into a zip file.

  - For more details, see [`A_01_WebScraping/README.md`](./A_01_WebScraping/README.md).

- **`B_02_DataTransform/`**: Implements a Python pipeline using `tabula-py` to extract, clean, and process table data from a specific PDF file (typically "Anexo I" obtained from the output of `A_01_WebScraping`) and saves the result as a zipped CSV.

  - For more details, see [`B_02_DataTransform/README.md`](./B_02_DataTransform/README.md).

- **`C_03_DB-Test/`**: Downloads public ANS operator registration data (CSV) and quarterly accounting statements (ZIPs containing CSVs), then cleans and loads this data into a MySQL database.

  - For more details, see [`C_03_DB-Test/README.md`](./C_03_DB-Test/README.md).

- **`D_04_FullStack/`**: A full-stack application featuring a Python Flask backend API and a Vue.js frontend. It allows users to perform textual searches and filter ANS operator data (likely sourced from `C_03_DB-Test` or a similar CSV dataset).
  - For more details, see [`D_04_FullStack/README.md`](./D_04_FullStack/README.md).

## Technology Stack Highlights

- **Backend & Data Processing:** Python 3.x
- **Web Scraping:** `requests`, `beautifulsoup4`
- **PDF Table Extraction:** `tabula-py` (requires Java Runtime)
- **Data Handling:** `pandas`
- **Web Framework (API):** `Flask` (in `D_04_FullStack`)
- **Frontend Framework:** `Vue.js` (in `D_04_FullStack`)
- **Database:** MySQL (used by `C_03_DB-Test`)
- **Testing:** `pytest`, `requests-mock`

## Getting Started

### Prerequisites

- Git
- Python (3.9+ recommended for most components)
- Access to a MySQL Server (required for `C_03_DB-Test`)
- Java Runtime Environment (JRE) or JDK (required for `B_02_DataTransform`)
- Node.js and npm (required for the frontend in `D_04_FullStack`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/will-developer/IntuitiveCare
    ```
2.  **Create and activate a virtual environment:**

    ```bash
    # On Windows with bash
    # source venv\Scripts\activate
    ```

3.  **Install dependencies:**

    - **Using pip:**
      ```bash
      pip install -r requirements.txt
      ```

4.  **Navigate to the desired subfolder** (example: `cd A_01_WebScraping`).
5.  **Follow the specific setup and installation instructions** detailed in the `README.md` file within that subfolder.

## Usage

Each component serves a distinct purpose and has its own execution method. Please refer to the `README.md` file within each subfolder for detailed usage instructions:

- [`A_01_WebScraping/README.md`](./A_01_WebScraping/README.md)
- [`B_02_DataTransform/README.md`](./B_02_DataTransform/README.md)
- [`C_03_DB-Test/README.md`](./C_03_DB-Test/README.md)
- [`D_04_FullStack/README.md`](./D_04_FullStack/README.md)
