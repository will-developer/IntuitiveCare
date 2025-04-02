import abc
from pathlib import Path
from datetime import date

from src.domain.entities.accounting_statement import AccountingStatement

class AccountingRepository(abc.ABC):
    @abc.abstractmethod
    def clear_all(self) -> None:
        pass

    @abc.abstractmethod
    def load_from_csv(self, csv_path: Path, reference_date: date) -> int:
        pass