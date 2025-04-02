import pandas
import tabula
import logging
from typing import List
from ..application.ports import IPdfReader

logger = logging.getLogger(__name__)

class TabulaPdfReader(IPdfReader):
    def extract_tables_from_pdf(self, pdf_path: str) -> List[pandas.DataFrame]:
        # Log the start of PDF extraction process
        logger.info(f"Attempting PDF table extraction using tabula-py from: {pdf_path}")
        
        try:
            # Use tabula to read all tables from PDF with these settings:
            # - pages='all': Process all pages
            # - lattice=True: Use lattice mode for cleaner table detection
            # - pandas_options={'dtype': str}: Keep all data as strings to preserve formatting
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                lattice=True,
                pandas_options={'dtype': str}
            )

            # Handle different return scenarios from tabula:
            if tables is None:
                # Case 1: No tables found in PDF
                logger.warning(f"No tables extracted from {pdf_path}. Tabula returned None.")
                return []
            if isinstance(tables, pandas.DataFrame):
                # Case 2: Single table found (returns DataFrame directly)
                logger.info(f"Found 1 table in PDF.")
                return [tables]
            if isinstance(tables, list):
                # Case 3: Multiple tables found (returns list of DataFrames)
                # Filter to ensure we only return valid DataFrames
                valid_tables = [df for df in tables if isinstance(df, pandas.DataFrame)]
                if len(valid_tables) != len(tables):
                    logger.warning(f"Filtered out {len(tables) - len(valid_tables)} non-DataFrame entries returned by tabula.")
                logger.info(f"Found {len(valid_tables)} tables in PDF.")
                return valid_tables
            else:
                # Case 4: Unexpected return type from tabula
                logger.warning(f"Unexpected type returned by tabula.read_pdf: {type(tables)}. Returning empty list.")
                return []

        except Exception as e:
            # Log any errors during PDF processing
            logger.error(f"Tabula PDF extraction failed for '{pdf_path}': {e}", exc_info=True)
            raise