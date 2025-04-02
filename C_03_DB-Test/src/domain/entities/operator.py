from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Operator:
    registry_code: int
    cnpj: str
    business_name: str
    fantasy_name: Optional[str] = None
    modality: Optional[str] = None
    street_address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    ddd: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    representative_name: Optional[str] = None
    representative_position: Optional[str] = None
    commercialization_region: Optional[str] = None
    registration_date: Optional[date] = None