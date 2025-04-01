import requests
import logging
import os
from ..core.ports.gateways import FileDownloader

class RequestsFileDownloader(FileDownloader):
    def download(self, url: str, destination_folder: str, filename: str, timeout: int) -> bool:
        # Combine folder path and filename to create full destination path
        filepath = os.path.join(destination_folder, filename)
        # Log the download attempt
        logging.info(f"Attempting download via Requests: {filename} from {url}")
        
        try:
            # Make HTTP GET request with streaming and timeout
            response = requests.get(url, timeout=timeout, stream=True)
            # Check for HTTP errors
            response.raise_for_status()

            # Open file in write-binary mode and save chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192): 
                    f.write(chunk)

            # Log successful download
            logging.info(f"Successfully downloaded via Requests: {filename}")
            return True

        # Handle different types of errors that might occur during download
        except requests.exceptions.RequestException as e:
            logging.error(f"Requests download failed for {filename}: {e}")
            return False
        except IOError as e:
            logging.error(f"Failed to save file {filename}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error downloading {filename}: {e}")
            return False