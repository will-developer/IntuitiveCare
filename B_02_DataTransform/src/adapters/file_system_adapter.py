import os
import zipfile
import logging
import pandas
from typing import Optional
from ..application.ports import IFileSystemAdapter

logger = logging.getLogger(__name__)

class LocalFileSystemAdapter(IFileSystemAdapter):
    def find_and_extract_target_file(
        self,
        zip_path: str,
        target_filename_part: str,
        extract_to_dir: str
    ) -> str:
        # Log attempt to open zip file
        logger.info(f"Attempting to open local zip file: {zip_path}")
        
        # Check if zip file exists
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Input ZIP file not found at: {zip_path}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Search for file containing target name in zip
                target_file_in_zip = next(
                    (f for f in zip_ref.namelist() if target_filename_part in f),
                    None
                )

                # Raise error if target file not found
                if not target_file_in_zip:
                    raise ValueError(
                        f"'{target_filename_part}' not found in ZIP archive: {zip_path}"
                    )

                # Extract the found file
                zip_ref.extract(target_file_in_zip, extract_to_dir)
                logger.info(f"Successfully extracted '{target_file_in_zip}' to '{extract_to_dir}'")

                # Handle path formatting and cleanup
                extracted_file_path = os.path.join(extract_to_dir, target_file_in_zip)
                desired_file_path = os.path.join(extract_to_dir, os.path.basename(target_file_in_zip))

                # Move file if needed and clean up empty directories
                if extracted_file_path != desired_file_path:
                    logger.debug(f"Moving extracted file from '{extracted_file_path}' to '{desired_file_path}'")
                    os.rename(extracted_file_path, desired_file_path)
                    try:
                        os.rmdir(os.path.dirname(extracted_file_path))
                        logger.debug(f"Removed empty directory: {os.path.dirname(extracted_file_path)}")
                    except OSError:
                         logger.debug(f"Could not remove directory {os.path.dirname(extracted_file_path)}")
                         pass
                else:
                     logger.debug(f"Extracted file already at desired location: '{desired_file_path}'")

                return desired_file_path

        # Handle various error cases
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to open or read ZIP file '{zip_path}': {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during zip extraction from '{zip_path}': {e}", exc_info=True)
            raise

    def save_dataframe_to_zipped_csv(
        self,
        df: Optional[pandas.DataFrame],
        output_dir: str,
        csv_filename_in_zip: str,
        zip_filename: str
    ) -> None:
        # Validate input DataFrame
        if df is None:
            logger.warning("DataFrame is None, skipping save.")
            return
        if df.empty:
             logger.warning("DataFrame is empty, skipping save.")
             return
        if not isinstance(df, pandas.DataFrame):
             logger.error(f"Invalid object type provided: expected DataFrame, got {type(df)}. Skipping save.")
             return

        # Create output directory if needed
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Ensured output directory exists: {output_dir}")
        except OSError as e:
            logger.error(f"Failed to create output directory '{output_dir}': {e}")
            raise IOError(f"Failed to create output directory '{output_dir}': {e}") from e

        # Set up file paths
        final_zip_path = os.path.join(output_dir, zip_filename)
        temp_csv_path = os.path.join(output_dir, f"~temp_{csv_filename_in_zip}.csv")

        try:
            # Save DataFrame to temporary CSV
            df.to_csv(temp_csv_path, index=False, encoding='utf-8')
            logger.info(f"DataFrame temporarily saved to CSV: {temp_csv_path}")

            # Create zip file and add CSV
            with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_csv_path, arcname=csv_filename_in_zip)
                logger.info(f"Added '{csv_filename_in_zip}' to ZIP archive: {final_zip_path}")

            logger.info(f"Successfully created final output: {final_zip_path}")

        except Exception as e:
            # Clean up on error
            logger.error(f"Failed to save DataFrame to zipped CSV: {e}", exc_info=True)
            if os.path.exists(final_zip_path):
                 try:
                     os.remove(final_zip_path)
                     logger.info(f"Removed potentially incomplete zip file due to error: {final_zip_path}")
                 except OSError as rm_err:
                     logger.warning(f"Could not remove incomplete zip file '{final_zip_path}': {rm_err}")
            raise
        finally:
            # Always clean up temporary CSV
            if os.path.exists(temp_csv_path):
                try:
                    os.remove(temp_csv_path)
                    logger.debug(f"Removed temporary CSV file: {temp_csv_path}")
                except OSError as rm_err:
                     logger.warning(f"Could not remove temporary csv file '{temp_csv_path}': {rm_err}")