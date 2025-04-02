from dataclasses import dataclass
from pathlib import Path
from typing import List

# Configuration for downloading files (immutable)
@dataclass(frozen=True)
class DownloadConfig:
    base_accounting_url: str  # Base URL for accounting data downloads
    operators_csv_url: str    # URL to download operators CSV
    years_to_download: List[str]  # List of years to fetch data for
    data_dir: Path           # Main directory for storing all data
    accounting_dir: Path     # Directory for accounting data
    zips_dir: Path           # Directory for downloaded ZIP files
    csvs_dir: Path           # Directory for extracted CSV files
    operators_dir: Path      # Directory for operator-related files
    operators_csv_path: Path # Path to the operators CSV file

# Configuration for loading data (immutable)
@dataclass(frozen=True)
class LoadConfig:
    operators_csv_path: Path      # Path to the operators CSV file
    accounting_csvs_dir: Path     # Directory containing accounting CSV files