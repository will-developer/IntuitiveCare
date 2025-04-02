from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass(frozen=True)
class DownloadConfig:
    base_accounting_url: str
    operators_csv_url: str
    years_to_download: List[str]
    data_dir: Path
    accounting_dir: Path
    zips_dir: Path
    csvs_dir: Path
    operators_dir: Path
    operators_csv_path: Path

@dataclass(frozen=True)
class LoadConfig:
    operators_csv_path: Path
    accounting_csvs_dir: Path
