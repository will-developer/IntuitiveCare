import pytest
from src.domain.entities.operator import Operator
from dataclasses import field, fields
from typing import Optional 

def test_operator_creation_from_dict_english_keys():
    data = {
        'registration_ans': '123456',
        'cnpj': '11.222.333/0001-44',
        'corporate_name': 'Health Corp Brasil',
        'fantasy_name': 'HealthCorp',
        'city': 'Sao Paulo',
        'state_uf': 'SP',
        'phone': '987654321',
        'email': 'contato@healthcorp.com',
        'non_existent_field': 'should_be_ignored' 
    }
    operator = Operator.from_dict(data)

    assert isinstance(operator, Operator)
    assert operator.registration_ans == '123456'
    assert operator.corporate_name == 'Health Corp Brasil'
    assert operator.city == 'Sao Paulo'
    assert operator.state_uf == 'SP'
    assert operator.phone == '987654321'
    assert operator.email == 'contato@healthcorp.com'
    assert operator.modality is None
    assert not hasattr(operator, 'non_existent_field')

def test_operator_to_dict_returns_portuguese_keys():
    operator = Operator(
        registration_ans='654321',
        cnpj='99.888.777/0001-55',
        corporate_name='Vida Segura Planos',
        fantasy_name='VidaSeg',
        city='Rio de Janeiro',
        state_uf='RJ',
        email='sac@vidaseg.com',
        modality=None
    )

    result_dict = operator.to_dict()

    assert 'Registro_ANS' in result_dict
    assert 'CNPJ' in result_dict
    assert 'Razao_Social' in result_dict
    assert 'Nome_Fantasia' in result_dict
    assert 'Cidade' in result_dict
    assert 'UF' in result_dict
    assert 'Endereco_eletronico' in result_dict
    assert result_dict['Registro_ANS'] == '654321'
    assert result_dict['Razao_Social'] == 'Vida Segura Planos'
    assert result_dict['Cidade'] == 'Rio de Janeiro'
    assert result_dict['UF'] == 'RJ'
    assert result_dict['Endereco_eletronico'] == 'sac@vidaseg.com'
    assert 'registration_ans' not in result_dict
    assert 'corporate_name' not in result_dict
    assert 'state_uf' not in result_dict
    assert 'email' not in result_dict
    assert 'Modalidade' not in result_dict
    assert 'modality' not in result_dict

def test_operator_from_dict_ignores_unknown_keys():
    data = {
        'corporate_name': 'Known Corp',
        'unknown_key': 'ignore me',
        'another_extra': 123
    }
    try:
        operator = Operator.from_dict(data)
        assert operator.corporate_name == 'Known Corp'
        assert not hasattr(operator, 'unknown_key')
        assert not hasattr(operator, 'another_extra')
    except TypeError as e:
        pytest.fail(f"Operator.from_dict raised unexpected TypeError: {e}")