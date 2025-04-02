import abc
from pathlib import Path

class ZipExtractor(abc.ABC):
    @abc.abstractmethod
    def extract(self, zip_path: Path, extract_dir: Path) -> bool:
        pass