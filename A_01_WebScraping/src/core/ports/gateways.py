from abc import ABC, abstractmethod
from typing import List, Optional

class HttpGateway(ABC):
    @abstractmethod
    def get_content(self, url: str, timeout: int) -> Optional[str]:
        pass

class HtmlParser(ABC):
    @abstractmethod
    def find_links(self, html_content: str, base_url: str, selector: str, keywords: List[str], suffix: str) -> List[str]:
        pass

class FileDownloader(ABC):
    @abstractmethod
    def download(self, url: str, destination_folder: str, filename: str, timeout: int) -> bool:
        pass

class ArchiveManager(ABC):
    @abstractmethod
    def create_archive(self, source_folder: str, archive_filepath: str, filenames: List[str]) -> bool:
        pass

class FileManager(ABC):
    @abstractmethod
    def ensure_directory(self, path: str) -> bool:
        pass

    @abstractmethod
    def remove_files(self, folder: str, filenames: List[str]) -> None:
        pass

    @abstractmethod
    def get_filename_from_url(self, url: str, suffix: str) -> str:
        pass