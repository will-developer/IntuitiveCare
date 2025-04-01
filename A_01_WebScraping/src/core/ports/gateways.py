from abc import ABC, abstractmethod
from typing import List, Optional

# Abstract base class for HTTP operations
class HttpGateway(ABC):
    @abstractmethod
    def get_content(self, url: str, timeout: int) -> Optional[str]:
        """Get HTML content from a URL with timeout"""
        pass

# Abstract base class for HTML parsing operations
class HtmlParser(ABC):
    @abstractmethod
    def find_links(self, html_content: str, base_url: str, selector: str, keywords: List[str], suffix: str) -> List[str]:
        """Find specific links in HTML content based on given criteria"""
        pass

# Abstract base class for file downloading operations
class FileDownloader(ABC):
    @abstractmethod
    def download(self, url: str, destination_folder: str, filename: str, timeout: int) -> bool:
        """Download a file from URL to local folder with timeout"""
        pass

# Abstract base class for archive (zip) operations
class ArchiveManager(ABC):
    @abstractmethod
    def create_archive(self, source_folder: str, archive_filepath: str, filenames: List[str]) -> bool:
        """Create archive file from multiple source files"""
        pass

# Abstract base class for file system operations
class FileManager(ABC):
    @abstractmethod
    def ensure_directory(self, path: str) -> bool:
        """Create directory if it doesn't exist"""
        pass

    @abstractmethod
    def remove_files(self, folder: str, filenames: List[str]) -> None:
        """Remove multiple files from a folder"""
        pass

    @abstractmethod
    def get_filename_from_url(self, url: str, suffix: str) -> str:
        """Extract filename from URL or generate a new one"""
        pass