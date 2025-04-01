import os
import requests.utils
import logging
import uuid
from typing import List
from ..core.ports.gateways import FileManager

class FileSystemManager(FileManager):
    def ensure_directory(self, path: str) -> bool:
        # Check if directory exists, create if it doesn't
        if not os.path.exists(path):
            try:
                os.makedirs(path)  # Create directory including parent directories
                logging.info(f"Created directory using os.makedirs: {path}")
                return True
            except OSError as e:
                logging.error(f"Failed to create directory {path} using os.makedirs: {e}")
                return False
        else:
            logging.debug(f"Directory already exists: {path}")
            return True

    def remove_files(self, folder: str, filenames: List[str]) -> None:
        # Remove multiple files from a folder
        logging.info(f"Attempting to remove {len(filenames)} files from {folder} using os.remove.")
        removed_count = 0
        for filename in filenames:
            filepath = os.path.join(folder, filename)  # Create full file path
            try:
                if os.path.exists(filepath):  # Check if file exists
                    os.remove(filepath)  # Delete the file
                    logging.debug(f"Removed file: {filepath}")
                    removed_count += 1
                else:
                    logging.warning(f"File not found for removal: {filepath}")
            except OSError as e:
                logging.warning(f"Could not remove file {filepath}: {e}")
        logging.info(f"Removed {removed_count} files using os.remove.")

    def get_filename_from_url(self, url: str, suffix: str) -> str:
        # Extract filename from URL or generate a random one if needed
        try:
            parsed_path = requests.utils.urlparse(url).path  # Get path part of URL
            filename = os.path.basename(parsed_path)  # Extract filename from path
            
            # If no filename or wrong extension, use fallback with UUID
            if not filename or not filename.lower().endswith(suffix.lower()):
                fallback_filename = f"downloaded_file_{uuid.uuid4()}{suffix}"
                logging.warning(f"Could not extract suitable filename from {url} (path: '{parsed_path}'). Using fallback: {fallback_filename}")
                return fallback_filename
            return filename
        except Exception as e:
            logging.error(f"Error parsing filename from URL {url}: {e}")
            return f"downloaded_file_{uuid.uuid4()}{suffix}"  # Fallback with random UUID