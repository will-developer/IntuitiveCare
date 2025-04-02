from typing import List, Optional, Dict, Any

from src.application.repositories.operator_repository import OperatorRepository
from src.domain.entities.operator import Operator

class SearchOperatorsUseCase:
    def __init__(self, operator_repository: OperatorRepository):
        if not isinstance(operator_repository, OperatorRepository):
             raise TypeError("operator_repository must be an instance of OperatorRepository")
        self._operator_repository = operator_repository

    def execute(
        self,
        query: Optional[str] = None,
        ddd: Optional[str] = None,
        phone: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        if not self._operator_repository.is_data_loaded():
            print("Warning: Attempted search, but data is not loaded in the repository.")
            return []

        operators: List[Operator] = self._operator_repository.search(
            query=query,
            ddd=ddd,
            phone=phone,
            limit=limit
        )

        return [operator.to_dict() for operator in operators]