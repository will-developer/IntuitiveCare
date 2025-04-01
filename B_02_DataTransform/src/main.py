import tempfile
import logging
import sys
import zipfile

from . import config
from .application import processing
from .adapters import file_system_adapter

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Starting data transformation pipeline.")
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Created temporary directory: {temp_dir}")
        try:
            extracted_pdf_path = file_system_adapter.find_and_extract_target_file(
                zip_path=config.INPUT_ZIP_PATH,
                target_filename_part=config.TARGET_FILENAME_PART,
                extract_to_dir=temp_dir
            )

            raw_tables = processing.extract_tables_from_pdf(extracted_pdf_path)

            processed_data = processing.process_extracted_tables(
                tables=raw_tables,
                column_rename_map=config.COLUMN_RENAME_MAP
            )

            file_system_adapter.save_dataframe_to_zipped_csv(
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
        except IOError as e:
             logger.error(f"Pipeline aborted: File system I/O error. {e}")
             sys.exit(1)
        except Exception as e:
            logger.error(f"An unexpected error occurred during the pipeline: {e}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    run_pipeline()