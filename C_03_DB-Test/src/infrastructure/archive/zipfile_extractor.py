import logging
import zipfile
from pathlib import Path

from src.application.ports.zip_extractor import ZipExtractor

logger = logging.getLogger(__name__)

class ZipfileExtractor(ZipExtractor):
    def extract(self, zip_path: Path, extract_dir: Path) -> bool:
        if not zip_path.exists() or not zip_path.is_file():
            logger.error(f"Zip file not found or is not a file: {zip_path}")
            return False

        try:
            extract_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Extracting '{zip_path.name}' to '{extract_dir}'")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            logger.info(f"Successfully extracted: {zip_path}")
            return True
        except zipfile.BadZipFile:
            logger.error(f"Error extracting {zip_path}: File is not a zip file or it is corrupted.")
            return False
        except FileNotFoundError:
            logger.error(f"Error extracting {zip_path}: File not found during extraction process.")
            return False
        except OSError as e:
            logger.error(f"OS error during extraction of {zip_path} to {extract_dir}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error extracting {zip_path}: {e}")
            return False