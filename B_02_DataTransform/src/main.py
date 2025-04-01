import zipfile
import os
import tempfile
import pandas
import logging
import sys
from typing import List, Dict, Optional

from . import config
from .application import processing

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def find_and_extract_target_file(
    zip_path: str,
    target_filename_part: str,
    extract_to_dir: str
) -> str:
    logger.info(f"Attempting to open zip file: {zip_path}")
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Input ZIP file not found at: {zip_path}")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        target_file_in_zip = next(
            (f for f in zip_ref.namelist() if target_filename_part in f),
            None
        )

        if not target_file_in_zip:
            raise ValueError(
                f"'{target_filename_part}' not found in ZIP archive: {zip_path}"
            )

        zip_ref.extract(target_file_in_zip, extract_to_dir)
        logger.info(f"Successfully extracted '{target_file_in_zip}' to '{extract_to_dir}'")

        extracted_file_path = os.path.join(extract_to_dir, target_file_in_zip)
        desired_file_path = os.path.join(extract_to_dir, os.path.basename(target_file_in_zip))

        if extracted_file_path != desired_file_path:
            logger.debug(f"Moving extracted file from '{extracted_file_path}' to '{desired_file_path}'")
            os.rename(extracted_file_path, desired_file_path)
            try:
                os.rmdir(os.path.dirname(extracted_file_path))
                logger.debug(f"Removed empty directory: {os.path.dirname(extracted_file_path)}")
            except OSError:
                 logger.debug(f"Could not remove directory {os.path.dirname(extracted_file_path)}, likely not empty.")
                 pass
        else:
             logger.debug(f"Extracted file already at desired location: '{desired_file_path}'")

        return desired_file_path

def save_dataframe_to_zipped_csv(
    df: Optional[pandas.DataFrame],
    output_dir: str,
    csv_filename_in_zip: str,
    zip_filename: str
):
    if df is None:
        logger.warning("DataFrame is None, skipping save.")
        return
    if df.empty:
         logger.warning("DataFrame is empty, skipping save.")
         return
    if not isinstance(df, pandas.DataFrame):
         logger.error(f"Invalid object passed to save_dataframe_to_zipped_csv: type {type(df)}. Skipping save.")
         return

    os.makedirs(output_dir, exist_ok=True)
    logger.debug(f"Ensured output directory exists: {output_dir}")

    final_zip_path = os.path.join(output_dir, zip_filename)
    temp_csv_path = os.path.join(output_dir, f"~temp_{csv_filename_in_zip}")

    try:
        df.to_csv(temp_csv_path, index=False, encoding='utf-8')
        logger.info(f"DataFrame temporarily saved to CSV: {temp_csv_path}")

        with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_csv_path, arcname=csv_filename_in_zip)
            logger.info(f"Added '{csv_filename_in_zip}' to ZIP archive: {final_zip_path}")

        logger.info(f"Successfully created final output: {final_zip_path}")

    except Exception as e:
        logger.error(f"Failed to save DataFrame to zipped CSV: {e}", exc_info=True)
        if os.path.exists(final_zip_path):
             try:
                 os.remove(final_zip_path)
                 logger.info(f"Removed potentially incomplete zip file due to error: {final_zip_path}")
             except OSError as rm_err:
                 logger.warning(f"Could not remove incomplete zip file '{final_zip_path}': {rm_err}")
        raise
    finally:
        if os.path.exists(temp_csv_path):
            try:
                os.remove(temp_csv_path)
                logger.debug(f"Removed temporary CSV file: {temp_csv_path}")
            except OSError as rm_err:
                 logger.warning(f"Could not remove temporary csv file '{temp_csv_path}': {rm_err}")


def run_pipeline():
    logger.info("Starting data transformation pipeline.")
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Created temporary directory: {temp_dir}")
        try:
            extracted_pdf_path = find_and_extract_target_file(
                zip_path=config.INPUT_ZIP_PATH,
                target_filename_part=config.TARGET_FILENAME_PART,
                extract_to_dir=temp_dir
            )

            raw_tables = processing.extract_tables_from_pdf(extracted_pdf_path)

            processed_data = processing.process_extracted_tables(
                tables=raw_tables,
                column_rename_map=config.COLUMN_RENAME_MAP
            )

            save_dataframe_to_zipped_csv(
                df=processed_data,
                output_dir=config.OUTPUT_DIR,
                csv_filename_in_zip=config.OUTPUT_CSV_FILENAME,
                zip_filename=config.FINAL_ZIP_FILENAME
            )

            logger.info("Data transformation pipeline finished successfully.")

        except FileNotFoundError as e:
             logger.error(f"Pipeline aborted: Required file not found. {e}")
             sys.exit(1)
        except ValueError as e:
             logger.error(f"Pipeline aborted: Data or configuration error. {e}")
             sys.exit(1)
        except zipfile.BadZipFile as e:
             logger.error(f"Pipeline aborted: Input ZIP file is corrupted or invalid. {e}")
             sys.exit(1)
        except Exception as e:
            logger.error(f"An unexpected error occurred during the pipeline: {e}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    run_pipeline()