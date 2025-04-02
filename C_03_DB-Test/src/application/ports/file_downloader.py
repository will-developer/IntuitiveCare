import abc
from pathlib import Path

class FileDownloader(abc.ABC):
    @abc.abstractmethod
    def download(self, url: str, save_path: Path, timeout: int = 60) -> bool:
        pass