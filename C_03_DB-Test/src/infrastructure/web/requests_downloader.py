import logging
import requests
from pathlib import Path

from src.application.ports.file_downloader import FileDownloader

logger = logging.getLogger(__name__)

class RequestsDownloader(FileDownloader):
    def download(self, url: str, save_path: Path, timeout: int = 60) -> bool:
        try:
            logger.info(f"Attempting to download: {url}")
            save_path.parent.mkdir(parents=True, exist_ok=True)

            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Successfully downloaded and saved to: {save_path}")
            return True
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error downloading {url} after {timeout} seconds.")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error downloading {url}: {e.response.status_code} {e.response.reason}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading {url}: {e}")
            return False
        except OSError as e:
            logger.error(f"Error saving file to {save_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during download of {url}: {e}")
            return False