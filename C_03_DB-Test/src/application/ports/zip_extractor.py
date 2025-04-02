import abc  # For creating abstract base classes
from pathlib import Path  # For type-safe path handling

class ZipExtractor(abc.ABC):
    """Abstract interface for ZIP archive extraction operations"""

    @abc.abstractmethod
    def extract(self, 
               zip_path: Path,    # Path to the ZIP file to extract
               extract_dir: Path  # Directory where contents should be extracted
              ) -> bool:          # Returns True if successful, False if failed
        """
        Extracts all contents from a ZIP archive to the specified directory
        """
        pass