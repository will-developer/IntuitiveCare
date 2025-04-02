import logging
import requests
from pathlib import Path

from src.application.ports.file_downloader import FileDownloader

logger = logging.getLogger(__name__)

class RequestsDownloader(FileDownloader):
    """File downloader implementation using the requests library."""

    def download(self, url: str, save_path: Path, timeout: int = 60) -> bool:
        """Downloads a file from URL and saves it locally."""
        try:
            logger.info(f"Starting download: {url}")
            
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Stream download to handle large files efficiently
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()  # Raise HTTP errors

            # Write file in chunks to prevent memory issues
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):  # 8KB chunks
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)

            logger.info(f"Download completed: {save_path}")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"Download timed out after {timeout}s: {url}")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"Server returned {e.response.status_code} for {url}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading {url}: {e}")
            return False
        except OSError as e:
            logger.error(f"Filesystem error saving to {save_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}", exc_info=True)
            return False