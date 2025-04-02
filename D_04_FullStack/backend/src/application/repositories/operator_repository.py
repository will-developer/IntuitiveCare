from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.operator import Operator

class OperatorRepository(ABC):
    @abstractmethod
    def load_data(self) -> None:
        pass

    @abstractmethod
    def is_data_loaded(self) -> bool:
        pass

    @abstractmethod
    def search(
        self,
        query: Optional[str] = None,
        ddd: Optional[str] = None,
        phone: Optional[str] = None,
        limit: int = 50
    ) -> List[Operator]:
        pass

    @abstractmethod
    def get_data_shape(self) -> Optional[tuple]:
        pass