import abc  # For creating abstract base classes
import pandas  # For DataFrame type hints
from typing import List, Optional  # For type annotations

# Abstract base class defining file system operations interface
class IFileSystemAdapter(abc.ABC):
    
    @abc.abstractmethod
    def find_and_extract_target_file(
        self,
        zip_path: str,             # Path to the input ZIP file
        target_filename_part: str, # Part of filename to search for in ZIP
        extract_to_dir: str        # Directory to extract the file to
    ) -> str:                     # Returns path to extracted file
        """Find a file in ZIP archive and extract it to specified directory"""
        pass

    @abc.abstractmethod
    def save_dataframe_to_zipped_csv(
        self,
        df: Optional[pandas.DataFrame],  # DataFrame to save (can be None)
        output_dir: str,                 # Directory to save the ZIP file
        csv_filename_in_zip: str,        # Name for CSV inside the ZIP
        zip_filename: str                # Name for the output ZIP file
    ) -> None:
        """Save DataFrame to CSV and compress it into a ZIP file"""
        pass

# Abstract base class defining PDF reading operations interface
class IPdfReader(abc.ABC):
    
    @abc.abstractmethod
    def extract_tables_from_pdf(
        self, 
        pdf_path: str  # Path to the input PDF file
    ) -> List[pandas.DataFrame]:  # Returns list of extracted DataFrames
        """Extract all tables from a PDF file and return as DataFrames"""
        pass