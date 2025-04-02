# src/domain/entities/operator.py
from dataclasses import dataclass, field, fields
from typing import Optional, Dict, Any, ClassVar
import logging

logger = logging.getLogger(__name__)

@dataclass
class Operator:
    registration_ans: Optional[str] = field(default=None)
    cnpj: Optional[str] = field(default=None)
    corporate_name: Optional[str] = field(default=None)
    fantasy_name: Optional[str] = field(default=None)
    modality: Optional[str] = field(default=None)
    street_address: Optional[str] = field(default=None)
    number: Optional[str] = field(default=None)
    complement: Optional[str] = field(default=None)
    neighborhood: Optional[str] = field(default=None)
    city: Optional[str] = field(default=None)
    state_uf: Optional[str] = field(default=None)
    zip_code: Optional[str] = field(default=None)
    ddd: Optional[str] = field(default=None)
    phone: Optional[str] = field(default=None)
    fax: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)
    representative: Optional[str] = field(default=None)
    representative_position: Optional[str] = field(default=None)
    last_update_date: Optional[str] = field(default=None)

    _csv_column_map: ClassVar[Dict[str, str]] = {
        'Registro_ANS': 'registration_ans',
        'CNPJ': 'cnpj',
        'Razao_Social': 'corporate_name',
        'Nome_Fantasia': 'fantasy_name',
        'Modalidade': 'modality',
        'Logradouro': 'street_address',
        'Numero': 'number',
        'Complemento': 'complement',
        'Bairro': 'neighborhood',
        'Cidade': 'city',
        'UF': 'state_uf',
        'CEP': 'zip_code',
        'DDD': 'ddd',
        'Telefone': 'phone',
        'Fax': 'fax',
        'Endereco_eletronico': 'email',
        'Representante': 'representative',
        'Cargo_Representante': 'representative_position',
        'Data_Atualizacao': 'last_update_date'
    }

    @classmethod
    def _get_reverse_map(cls) -> Dict[str, str]:
        return {v: k for k, v in cls._csv_column_map.items()}

    @classmethod
    def from_dict(cls, data: dict):
        defined_field_names = {f.name for f in fields(cls)}

        instance_data = {
            key: value
            for key, value in data.items()
            if key in defined_field_names
        }

        try:
            return cls(**instance_data)
        except TypeError as e:
            logger.error(f"TypeError during Operator instantiation: {e}")
            logger.debug(f"Input data keys: {list(data.keys())}")
            logger.debug(f"Filtered instance_data keys to pass: {list(instance_data.keys())}")
            logger.debug(f"Defined dataclass fields: {defined_field_names}")
            raise e

    def to_dict(self) -> Dict[str, Any]:
        portuguese_dict = {}
        reverse_map = self._get_reverse_map()

        for field_info in fields(self):
            field_name = field_info.name
            if field_name.startswith('_'):
                continue

            value = getattr(self, field_name)

            if value is not None:
                output_key = reverse_map.get(field_name, field_name)
                portuguese_dict[output_key] = value

        return portuguese_dict