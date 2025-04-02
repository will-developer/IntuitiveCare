import abc  # For creating abstract base classes
from pathlib import Path  # For type-safe file path handling

# Abstract base class defining the file downloader interface
class FileDownloader(abc.ABC):
    
    @abc.abstractmethod
    def download(self, 
                url: str,          # The URL of the file to download
                save_path: Path,   # Where to save the downloaded file (as Path object)
                timeout: int = 60  # Timeout in seconds (default 60)
               ) -> bool:          # Returns True if successful, False otherwise
        pass