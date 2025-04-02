import abc  # For creating abstract base classes
from pathlib import Path  # For handling file paths
from datetime import date  # For date handling

# Import the entity class this repository works with
from src.domain.entities.accounting_statement import AccountingStatement

# Abstract base class defining the accounting data repository interface
class AccountingRepository(abc.ABC):
    
    @abc.abstractmethod
    def clear_all(self) -> None:
        """Clears all accounting statements from the repository"""
        pass

    @abc.abstractmethod
    def load_from_csv(self, csv_path: Path, reference_date: date) -> int:
        """
        Loads accounting statements from a CSV file into the repository
        """
        pass