# Data Downloader and Loader (C_03_DB-Test)

## Overview

This project downloads public registration data (CSV) and quarterly accounting statements (ZIP files containing CSVs) from the Brazilian National Health Agency (ANS) open data portal. It then processes and loads this data into a MySQL database.

## Features

- Downloads the latest operators CSV.
- Downloads accounting statement ZIP files for configurable years.
- Extracts CSVs from downloaded ZIP files.
- Cleans database tables (`operators`, `accounting`) before loading.
- Loads operator data into the `operators` table using `LOAD DATA LOCAL INFILE`.
- Loads accounting statement data into the `accounting` table using `LOAD DATA LOCAL INFILE`, handling data type conversions and deriving reference dates from filenames.
- Structured using Clean Architecture layers (Domain, Application, Infrastructure).
- Configuration managed via `.env` file.
- Includes Unit and Integration tests using `pytest`.
- Written in English following Python best practices.

## Setup

### Prerequisites

- Python (3.9+ recommended)
- Git
- MySQL Server (ensure `local_infile` is enabled)

  - Check server status: `SHOW GLOBAL VARIABLES LIKE 'local_infile';`
  - If OFF, enable it in your MySQL configuration file (`my.cnf` or `my.ini`) under the `[mysqld]` and `[mysql]` sections:

    ```ini
    [mysqld]
    local_infile=1

    [mysql]
    local_infile=1
    ```

  - Restart the MySQL server after changing the configuration.

### Installation Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/will-developer/IntuitiveCare
    ```

<br>
---- (If you have already done it, skip steps 2 and 3:) ----

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows with bash
    # source venv\Scripts\activate
    ```

3.  **Install dependencies:**

    - **Using pip:**
      ```bash
      pip install -r requirements.txt
      ```

4.  **Database Setup:**

    - Connect to your MySQL server.
    - Create the database specified in your configuration (default: `db-test`).

    - Create a database user (or use an existing one).
    - Grant the necessary privileges to the user on the database. The user needs `SELECT`, `INSERT`, `TRUNCATE`, and crucially `FILE` (for `LOAD DATA LOCAL INFILE`). Replace `'your_user'` and `'your_password'` with your actual credentials.
      ```sql
      -- Example: Create user and grant privileges
      CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';
      GRANT SELECT, INSERT, TRUNCATE, FILE ON ans_data.* TO 'your_user'@'localhost';
      FLUSH PRIVILEGES;
      ```
    - Create the necessary tables. You'll need the SQL schema for the `operators` and `accounting` tables, including the foreign key constraint from `accounting` to `operators`. (You might want to add a `schema.sql` file to the project and run `analysis.queries.sql after run the main script and install the schema`).

5.  **Configure Environment Variables:**
    - Copy the example environment file:
      ```bash
      cd C_03_DB-Test
      cp .env.example .env
      ```
    - **Edit the `.env` file** with your specific settings:
      - **Crucially:** Update `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` with your actual database connection details.
      - Adjust `YEARS_TO_DOWNLOAD` or `CURRENT_YEAR_OVERRIDE` if needed.
      - Set the desired `LOG_LEVEL` (e.g., `INFO`, `DEBUG`).
    - **IMPORTANT:** The `.env` file contains sensitive information like database passwords. It is already included in `.gitignore` and **should never be committed to version control.**

## Usage

To run the complete download and load process, execute the main script from the project root directory:

```bash
cd C_03_DB-Test
python -m src.main
```

The script will:

- Read configuration from the .env file.

- Create necessary local data directories (./data/).

- Download the operators CSV.

- Download and extract accounting CSVs for the configured years.

- Connect to the database.

- Clear the accounting and operators tables.

- Load data from the downloaded CSVs into the respective tables.

- Log progress and potential errors to the console.
