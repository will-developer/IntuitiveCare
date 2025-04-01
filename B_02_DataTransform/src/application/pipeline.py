import tempfile
import logging
import sys
import zipfile

from .. import config
from . import processing
from .ports import IFileSystemAdapter, IPdfReader
from ..adapters.file_system_adapter import LocalFileSystemAdapter
from ..adapters.pdf_reader_adapter import TabulaPdfReader

logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Starting data transformation pipeline orchestration.")

    file_system: IFileSystemAdapter = LocalFileSystemAdapter()
    pdf_reader: IPdfReader = TabulaPdfReader()

    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Created temporary directory: {temp_dir}")
        try:
            logger.info("Step 1: Extracting PDF from source ZIP.")
            extracted_pdf_path = file_system.find_and_extract_target_file(
                zip_path=config.INPUT_ZIP_PATH,
                target_filename_part=config.TARGET_FILENAME_PART,
                extract_to_dir=temp_dir
            )
            logger.info(f"PDF extracted to: {extracted_pdf_path}")

            logger.info("Step 2: Extracting tables from PDF.")
            raw_tables = pdf_reader.extract_tables_from_pdf(extracted_pdf_path)
            logger.info(f"Extracted {len(raw_tables)} raw tables.")

            logger.info("Step 3: Processing extracted tables.")
            processed_data = processing.process_extracted_tables(
                tables=raw_tables,
                column_rename_map=config.COLUMN_RENAME_MAP
            )
            if processed_data is None:
                 logger.warning("Processing resulted in no data. Skipping save step.")
            else:
                 logger.info("Processing complete.")
                 logger.info("Step 4: Saving processed data to zipped CSV.")
                 file_system.save_dataframe_to_zipped_csv(
                     df=processed_data,
                     output_dir=config.OUTPUT_DIR,
                     csv_filename_in_zip=config.OUTPUT_CSV_FILENAME,
                     zip_filename=config.FINAL_ZIP_FILENAME
                 )
                 logger.info("Save operation complete.")

            logger.info("Data transformation pipeline finished successfully.")

        except FileNotFoundError as e:
             logger.error(f"Pipeline failed: Required file not found. Error: {e}")
             sys.exit(1)
        except ValueError as e:
             logger.error(f"Pipeline failed: Data validation or configuration error. Error: {e}")
             sys.exit(1)
        except zipfile.BadZipFile as e:
             logger.error(f"Pipeline failed: Input ZIP file is corrupted or invalid. Error: {e}")
             sys.exit(1)
        except IOError as e:
             logger.error(f"Pipeline failed: File system I/O error. Error: {e}")
             sys.exit(1)
        except ImportError as e:
             logger.error(f"Pipeline failed: Missing dependency. Error: {e}")
             sys.exit(1)
        except Exception as e:
            logger.error(f"Pipeline failed due to an unexpected error: {e}", exc_info=True)
            sys.exit(1)