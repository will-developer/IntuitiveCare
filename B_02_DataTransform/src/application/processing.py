import pandas
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def process_extracted_tables(
    tables: List[pandas.DataFrame],  # List of DataFrames to process
    column_rename_map: Dict[str, str]  # Dictionary for renaming columns
) -> Optional[pandas.DataFrame]:  # Returns processed DataFrame or None
    """Process and combine multiple DataFrames from PDF tables"""
    
    # Log start of processing
    logger.info(f"Processing {len(tables)} provided tables.")
    if not tables:
        logger.warning("Received an empty list of tables to process.")
        return None

    # Step 1: Clean each table
    processed_tables: List[pandas.DataFrame] = []
    for i, df in enumerate(tables):
        # Check if item is actually a DataFrame
        if not isinstance(df, pandas.DataFrame):
            logger.warning(f"Item at index {i} is not a DataFrame ({type(df)}), skipping.")
            continue

        # Remove completely empty rows and columns
        df_cleaned = df.dropna(axis=1, how='all').dropna(axis=0, how='all')

        # Keep only non-empty DataFrames
        if not df_cleaned.empty:
            processed_tables.append(df_cleaned)
        else:
            logger.debug(f"Table at index {i} was empty after cleaning, discarding.")

    logger.info(f"Retained {len(processed_tables)} non-empty tables after cleaning.")

    # Return None if all tables were empty
    if not processed_tables:
        logger.warning("No valid tables remaining after cleaning.")
        return None

    # Step 2: Combine and transform tables
    try:
        # Combine all cleaned tables into one DataFrame
        combined_df = pandas.concat(processed_tables, ignore_index=True)
        logger.info(f"Combined DataFrame shape before renaming: {combined_df.shape}")

        # Only rename columns that actually exist in the DataFrame
        rename_actual = {k: v for k, v in column_rename_map.items() if k in combined_df.columns}
        if rename_actual:
            combined_df.rename(columns=rename_actual, inplace=True)
            logger.info(f"Renamed columns: {rename_actual}")
        elif column_rename_map:
             logger.warning(f"None of the specified columns to rename {list(column_rename_map.keys())} were found in the combined table.")

        # Log final result and return
        logger.info(f"Final combined DataFrame shape: {combined_df.shape}")
        return combined_df
        
    except Exception as e:
        logger.error(f"Error during DataFrame combination or renaming: {e}", exc_info=True)
        raise