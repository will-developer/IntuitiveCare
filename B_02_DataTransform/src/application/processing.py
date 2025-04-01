# src/application/processing.py
import pandas
import tabula
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def extract_tables_from_pdf(pdf_path: str) -> List[pandas.DataFrame]:
    logger.info(f"Extracting tables from PDF: {pdf_path}")
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
        logger.error(f"Failed to extract tables from PDF '{pdf_path}': {e}", exc_info=True)
        raise

def process_extracted_tables(
    tables: List[pandas.DataFrame],
    column_rename_map: Dict[str, str]
) -> Optional[pandas.DataFrame]:
    logger.info(f"Processing {len(tables)} extracted tables.")
    processed_tables: List[pandas.DataFrame] = []
    for i, df in enumerate(tables):
        if not isinstance(df, pandas.DataFrame):
            logger.warning(f"Item at index {i} is not a DataFrame ({type(df)}), skipping.")
            continue

        df_cleaned = df.dropna(axis=1, how='all').dropna(axis=0, how='all')

        if not df_cleaned.empty:
            processed_tables.append(df_cleaned)
        else:
            logger.debug(f"Table at index {i} was empty after cleaning, discarding.")

    logger.info(f"Retained {len(processed_tables)} non-empty tables after cleaning.")

    if not processed_tables:
        logger.warning("No valid tables remaining after cleaning.")
        return None

    try:
        combined_df = pandas.concat(processed_tables, ignore_index=True)
        logger.info(f"Combined DataFrame shape before renaming: {combined_df.shape}")

        rename_actual = {k: v for k, v in column_rename_map.items() if k in combined_df.columns}
        if rename_actual:
            combined_df.rename(columns=rename_actual, inplace=True)
            logger.info(f"Renamed columns: {rename_actual}")
        elif column_rename_map:
             logger.warning(f"None of the specified columns to rename {list(column_rename_map.keys())} were found.")

        logger.info(f"Final combined DataFrame shape: {combined_df.shape}")
        return combined_df
    except Exception as e:
        logger.error(f"Error combining or renaming DataFrames: {e}", exc_info=True)
        raise