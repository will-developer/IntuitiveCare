# WebScrapper

This project is a Python web scraper designed to download specific PDF annexes ("Anexo I" and "Anexo II") related to the 'Atualização do Rol de Procedimentos' from the Brazilian National Supplementary Health Agency (ANS) website. It then archives these downloaded PDFs into a single zip file.

## Features

- Fetches content from a specific ANS webpage.
- Parses HTML to find links to PDF files containing "Anexo I" or "Anexo II" in their link text.
- Downloads the identified PDF files.
- Creates a compressed zip archive (`Anexos.zip`) containing the downloaded files.
- Removes the individual PDF files after successful archiving.
- Structured using Clean Architecture principles for maintainability and testability.
- Includes unit and integration tests using `pytest`.

## Target Site

The primary target URL for scraping is:
`https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos`

## Technology Stack

- Python 3.x
- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML content.
- `pytest`: For running unit and integration tests.
- `requests-mock`: For mocking HTTP requests during testing.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    cd A_01_WebScraping
    ```

## Running the Scraper

Ensure your virtual environment is activated. Run the scraper from the project's **root directory** (`A_01_WebScraping/`) using the following command:

```bash
python -m src.main
```

The script will log its progress to the console.

Running Tests
Ensure your virtual environment is activated. Run the tests from the project's root directory using:

```bash
pytest
```

This command will discover and run all tests located in the tests/ directory.

## Configuration

- Key settings can be modified in the src/config.py file:
- BASE_URL: The target webpage URL.
- DOWNLOAD_DIR: The folder where files are temporarily downloaded and the final zip is stored.
- ZIP_FILENAME: The name of the output zip file.
- LINK_SELECTOR: The CSS selector used to find potential links.
- LINK_TEXT_KEYWORDS: Keywords required in the link text.
- LINK_SUFFIX: The required file extension (e.g., .pdf).
- REQUEST_TIMEOUT: Timeout in seconds for HTTP requests.

## Output

- The script will:
- Create a pdfs/ directory in the project root (if it doesn't exist).
- Download the relevant PDF files into this directory.
- Create a Anexos.zip file inside the pdfs/ directory containing all successfully downloaded PDFs.
- Remove the individual PDF files from the pdfs/ directory after the zip file is successfully created.
- The final result will be the pdfs/Anexos.zip file.

---
