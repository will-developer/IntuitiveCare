from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

@dataclass
class AccountingStatement:
    reference_date: date
    registry_code: int
    account_code: str
    account_description: str
    initial_balance: Optional[Decimal] = None
    final_balance: Optional[Decimal] = None