import abc
from pathlib import Path

class FileSystem(abc.ABC):
    @abc.abstractmethod
    def create_directories(self, path: Path) -> None:
        pass

    @abc.abstractmethod
    def list_files(self, directory: Path, pattern: str) -> list[Path]:
        pass

    @abc.abstractmethod
    def get_absolute_path(self, path: Path) -> Path:
        pass

    @abc.abstractmethod
    def path_exists(self, path: Path) -> bool:
        pass

    @abc.abstractmethod
    def get_filename(self, path: Path) -> str:
        pass