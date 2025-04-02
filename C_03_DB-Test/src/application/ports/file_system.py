import abc
from pathlib import Path

class FileSystem(abc.ABC):
    """Abstract interface for file system operations"""

    @abc.abstractmethod
    def create_directories(self, path: Path) -> None:
        """Create all directories in the specified path if they don't exist"""
        pass

    @abc.abstractmethod
    def list_files(self, directory: Path, pattern: str) -> list[Path]:
        """
        List all files in directory matching the pattern
        Example: pattern="*.txt" lists all text files
        """
        pass

    @abc.abstractmethod
    def get_absolute_path(self, path: Path) -> Path:
        """Convert relative path to absolute path"""
        pass

    @abc.abstractmethod
    def path_exists(self, path: Path) -> bool:
        """Check if a file or directory exists at the given path"""
        pass

    @abc.abstractmethod
    def get_filename(self, path: Path) -> str:
        """Extract just the filename portion from a path (e.g. 'file.txt' from '/path/to/file.txt')"""
        pass