from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

# Represents an accounting statement entry
@dataclass
class AccountingStatement:
    reference_date: date          # Date of the accounting record
    registry_code: int            # Registry identifier code
    account_code: str             # Account identifier code
    account_description: str      # Description of the account
    initial_balance: Optional[Decimal] = None  # Starting balance
    final_balance: Optional[Decimal] = None    # Ending balance