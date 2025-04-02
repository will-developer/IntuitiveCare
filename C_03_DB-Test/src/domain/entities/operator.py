from dataclasses import dataclass
from datetime import date
from typing import Optional

# Represents an operator/company entity
@dataclass
class Operator:
    registry_code: int                   # Unique registry identification number
    cnpj: str                            # Brazilian tax ID (14 digits)
    business_name: str                   # Official company name
    fantasy_name: Optional[str] = None   # Trade name
    modality: Optional[str] = None       # Business sector/category
    
    # Address information (all optional)
    street_address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Contact information (all optional)
    ddd: Optional[str] = None            # Area code
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    
    # Representative information
    representative_name: Optional[str] = None
    representative_position: Optional[str] = None
    
    # Additional business information
    commercialization_region: Optional[str] = None  # Business operation area
    registration_date: Optional[date] = None       # Company registration date