import pandas
import tabula
import logging
from typing import List

logger = logging.getLogger(__name__)

def extract_tables_from_pdf(pdf_path: str) -> List[pandas.DataFrame]:
    logger.info(f"Attempting PDF table extraction using tabula-py from: {pdf_path}")
    try:
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',
            lattice=True,
            pandas_options={'dtype': str}
        )

        if tables is None:
            logger.warning(f"No tables extracted from {pdf_path}. Tabula returned None.")
            return []
        if isinstance(tables, pandas.DataFrame):
             logger.info(f"Found 1 table in PDF.")
             return [tables]
        if isinstance(tables, list):
             valid_tables = [df for df in tables if isinstance(df, pandas.DataFrame)]
             if len(valid_tables) != len(tables):
                 logger.warning(f"Filtered out {len(tables) - len(valid_tables)} non-DataFrame entries returned by tabula.")
             logger.info(f"Found {len(valid_tables)} tables in PDF.")
             return valid_tables
        else:
            logger.warning(f"Unexpected type returned by tabula.read_pdf: {type(tables)}. Returning empty list.")
            return []

    except Exception as e:
        logger.error(f"Tabula PDF extraction failed for '{pdf_path}': {e}", exc_info=True)
        raise