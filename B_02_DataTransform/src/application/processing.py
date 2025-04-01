import pandas
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def process_extracted_tables(
    tables: List[pandas.DataFrame],
    column_rename_map: Dict[str, str]
) -> Optional[pandas.DataFrame]:
    logger.info(f"Processing {len(tables)} provided tables.")
    if not tables:
        logger.warning("Received an empty list of tables to process.")
        return None

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
             logger.warning(f"None of the specified columns to rename {list(column_rename_map.keys())} were found in the combined table.")

        logger.info(f"Final combined DataFrame shape: {combined_df.shape}")
        return combined_df
    except Exception as e:
        logger.error(f"Error during DataFrame combination or renaming: {e}", exc_info=True)
        raise