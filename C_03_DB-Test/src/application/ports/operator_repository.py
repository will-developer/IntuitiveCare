import abc  # For abstract base class functionality
from pathlib import Path  # For type-safe path handling

# Import the Operator entity this repository manages
from src.domain.entities.operator import Operator

class OperatorRepository(abc.ABC):
    """Abstract base class defining storage operations for Operator entities"""

    @abc.abstractmethod
    def clear_all(self) -> None:
        """Removes all Operator records from the repository"""
        pass

    @abc.abstractmethod
    def load_from_csv(self, csv_path: Path) -> int:
        """
        Loads Operator records from a CSV file into the repository
        """
        pass