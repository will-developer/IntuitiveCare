import pandas as pd
import os
import traceback
from typing import List, Optional

from src.application.repositories.operator_repository import OperatorRepository
from src.domain.entities.operator import Operator

class CsvOperatorRepository(OperatorRepository):
    def __init__(self, csv_file_path: str):
        if not csv_file_path or not isinstance(csv_file_path, str):
            raise ValueError("A valid CSV file path must be provided.")
        self._csv_path = csv_file_path
        self._df: Optional[pd.DataFrame] = None
        self._load_error: Optional[Exception] = None
        self._columns_to_search = [
            'corporate_name', 'fantasy_name', 'registration_ans',
            'cnpj', 'city', 'state_uf', 'zip_code', 'modality',
            'street_address', 'neighborhood', 'phone', 'email',
            'representative'
        ]
        self._entity_to_csv_map = {v: k for k, v in Operator._csv_column_map.items()}

    def load_data(self) -> None:
        self._df = None
        self._load_error = None
        try:
            if not os.path.exists(self._csv_path):
                raise FileNotFoundError(f"CSV file not found at: {self._csv_path}")

            dtypes = {
                self._entity_to_csv_map.get('zip_code'): str,
                self._entity_to_csv_map.get('cnpj'): str,
                self._entity_to_csv_map.get('registration_ans'): str,
                self._entity_to_csv_map.get('ddd'): str,
                self._entity_to_csv_map.get('phone'): str,
                self._entity_to_csv_map.get('fax'): str
            }
            dtypes = {k: v for k, v in dtypes.items() if k is not None}

            self._df = pd.read_csv(
                self._csv_path,
                sep=';',
                encoding='utf-8',
                dtype=dtypes,
                low_memory=False,
                on_bad_lines='warn'
            )
            if self._df.empty:
                 print(f"Warning: CSV file loaded but is empty: {self._csv_path}")
            self._df.rename(columns=Operator._csv_column_map, inplace=True)
            for field_name in Operator.__annotations__:
                 if not field_name.startswith('_') and field_name not in self._df.columns:
                     self._df[field_name] = None

            print(f"CSV loaded successfully from: {self._csv_path}. Shape: {self._df.shape}")

        except FileNotFoundError as e:
            self._load_error = e
            print(f"Error loading CSV: {e}")
        except pd.errors.ParserError as e:
            self._load_error = e
            print(f"Error parsing CSV: {e}. Check separator, encoding, file integrity.")
        except Exception as e:
            self._load_error = e
            print(f"An unexpected error occurred during CSV loading: {e}")
            print(traceback.format_exc())

    def is_data_loaded(self) -> bool:
        return self._df is not None and self._load_error is None

    def get_data_shape(self) -> Optional[tuple]:
         if self.is_data_loaded() and self._df is not None:
             return self._df.shape
         return None

    def search(
        self,
        query: Optional[str] = None,
        ddd: Optional[str] = None,
        phone: Optional[str] = None,
        limit: int = 50
    ) -> List[Operator]:

        if not self.is_data_loaded() or self._df is None:
            print("Search cannot proceed: Data not loaded.")
            return []

        if not query and not ddd and not phone:
            return []

        try:
            filtered_df = self._df.copy()

            if ddd:
                filtered_df = filtered_df[filtered_df['ddd'].astype(str) == str(ddd)]
            if phone:
                filtered_df = filtered_df[filtered_df['phone'].astype(str) == str(phone)]

            if filtered_df.empty:
                return []

            if query:
                query_lower = query.lower().strip()
                if query_lower:
                    search_cols_in_df = [col for col in self._columns_to_search if col in filtered_df.columns]

                    if not search_cols_in_df:
                         print("Warning: None of the specified search columns exist in the DataFrame.")
                         return []

                    mask = filtered_df[search_cols_in_df].apply(
                        lambda col: col.astype(str).str.lower().str.contains(query_lower, na=False)
                    ).any(axis=1)

                    filtered_df = filtered_df.loc[mask]

            results_df = filtered_df.head(limit)
            results_df_filled = results_df.where(pd.notna(results_df), None)
            results_dict = results_df_filled.to_dict(orient='records')

            operators = [Operator.from_dict(record) for record in results_dict]
            return operators

        except Exception as e:
            print(f"An error occurred during search operation: {e}")
            print(traceback.format_exc())
            return []