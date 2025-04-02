import os
import logging
from pathlib import Path
from typing import List

from src.application.ports.file_system import FileSystem

logger = logging.getLogger(__name__)

class OsFileSystem(FileSystem):
    def create_directories(self, path: Path) -> None:
        try:
            os.makedirs(path, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path}")
        except OSError as e:
            logger.error(f"Failed to create directory: {path}: {e}")
            raise

    def list_files(self, directory: Path, pattern: str) -> List[Path]:
        if not directory.is_dir():
            logger.warning(f"Directory not found for listing files: {directory}")
            return []
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            logger.error(f"Error listing files in {directory} with pattern {pattern}: {e}")
            return []

    def get_absolute_path(self, path: Path) -> Path:
        return path.resolve()

    def path_exists(self, path: Path) -> bool:
        return path.exists()

    def get_filename(self, path: Path) -> str:
        return path.name