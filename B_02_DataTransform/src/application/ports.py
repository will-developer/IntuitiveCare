import abc
import pandas
from typing import List, Optional

class IFileSystemAdapter(abc.ABC):
    @abc.abstractmethod
    def find_and_extract_target_file(
        self,
        zip_path: str,
        target_filename_part: str,
        extract_to_dir: str
    ) -> str:
        pass

    @abc.abstractmethod
    def save_dataframe_to_zipped_csv(
        self,
        df: Optional[pandas.DataFrame],
        output_dir: str,
        csv_filename_in_zip: str,
        zip_filename: str
    ) -> None:
        pass

class IPdfReader(abc.ABC):
    @abc.abstractmethod
    def extract_tables_from_pdf(self, pdf_path: str) -> List[pandas.DataFrame]:
        pass