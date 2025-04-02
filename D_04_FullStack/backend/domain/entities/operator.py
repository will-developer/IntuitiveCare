from dataclasses import dataclass, field
from typing import Optional

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

    _csv_column_map = {
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
    def from_dict(cls, data: dict):
        mapped_data = {
            cls._csv_column_map[csv_col]: value
            for csv_col, value in data.items()
            if csv_col in cls._csv_column_map
        }
        instance_data = {
            field_name: mapped_data.get(field_name)
            for field_name in cls.__annotations__ if not field_name.startswith('_')
        }
        return cls(**instance_data)

    def to_dict(self) -> dict:
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__annotations__ if not field_name.startswith('_')
            if getattr(self, field_name) is not None
        }