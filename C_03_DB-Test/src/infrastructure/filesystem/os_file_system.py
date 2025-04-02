import os
import logging
from pathlib import Path
from typing import List

from src.application.ports.file_system import FileSystem

logger = logging.getLogger(__name__)

class OsFileSystem(FileSystem):
    """Concrete implementation of FileSystem using Python's os and pathlib modules."""

    def create_directories(self, path: Path) -> None:
        """Creates directory structure including parents if needed."""
        try:
            os.makedirs(path, exist_ok=True)  # exist_ok prevents errors if dir exists
            logger.debug(f"Created directory structure at: {path}")
        except OSError as e:
            logger.error(f"Directory creation failed for {path}: {e}")
            raise

    def list_files(self, directory: Path, pattern: str) -> List[Path]:
        """Lists files in directory matching the given glob pattern."""
        if not directory.is_dir():
            logger.warning(f"Invalid directory path: {directory}")
            return []
            
        try:
            files = list(directory.glob(pattern))
            logger.debug(f"Found {len(files)} files matching {pattern} in {directory}")
            return files
        except Exception as e:
            logger.error(f"File listing failed in {directory}: {e}")
            return []  # Fail gracefully by returning empty list

    def get_absolute_path(self, path: Path) -> Path:
        """Returns absolute version of path resolving """
        return path.resolve()

    def path_exists(self, path: Path) -> bool:
        """Checks if path exists in filesystem. """
        return path.exists()

    def get_filename(self, path: Path) -> str:
        """Extracts the filename component from a path."""
        return path.name