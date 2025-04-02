import abc
from pathlib import Path

from src.domain.entities.operator import Operator

class OperatorRepository(abc.ABC):
    @abc.abstractmethod
    def clear_all(self) -> None:
        pass

    @abc.abstractmethod
    def load_from_csv(self, csv_path: Path) -> int:
        pass