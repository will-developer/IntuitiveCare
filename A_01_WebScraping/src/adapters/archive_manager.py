import zipfile
import logging
import os
from typing import List
from ..core.ports.gateways import ArchiveManager

class ZipArchiveManager(ArchiveManager):
    def create_archive(self, source_folder: str, archive_filepath: str, filenames: List[str]) -> bool:
        # Log that we're starting to create a zip archive
        logging.info(f"Creating zip archive: {archive_filepath} using zipfile module")
        try:
            # Create a new zip file with compression
            with zipfile.ZipFile(archive_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add each file from the source folder to the zip archive
                for filename in filenames:
                    source_filepath = os.path.join(source_folder, filename)
                    # Check if file exists before adding to zip
                    if os.path.exists(source_filepath):
                        zipf.write(source_filepath, os.path.basename(source_filepath))
                        logging.debug(f"Added {filename} to zip archive.")
                    else:
                        logging.warning(f"File not found, skipping zip: {source_filepath}")

            # Log success message after creating zip
            logging.info(f"Successfully created zip archive {archive_filepath} with {len(filenames)} files.")
            return True

        # Handle different types of errors that might occur during zip creation
        except zipfile.BadZipFile as e:
             logging.error(f"Failed to create zip file {archive_filepath}: Bad zip file - {e}")
             return False
        except OSError as e:
             logging.error(f"OS error creating/writing zip file {archive_filepath}: {e}")
             return False
        except Exception as e:
             logging.error(f"Unexpected error during zipping for {archive_filepath}: {e}")
             return False