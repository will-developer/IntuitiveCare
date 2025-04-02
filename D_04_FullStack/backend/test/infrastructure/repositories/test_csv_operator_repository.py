import pytest
import os
import pandas as pd
from src.infrastructure.repositories.csv_operator_repository import CsvOperatorRepository
from src.domain.entities.operator import Operator

MAIN_CSV_PATH = os.path.abspath(os.path.join('..', 'csv', 'Relatorio_cadop.csv'))
INVALID_CSV_PATH = os.path.abspath(os.path.join('tests', 'fixtures', 'non_existent.csv'))

print(f"DEBUG: Checking for MAIN CSV at: {MAIN_CSV_PATH}")
if not os.path.exists(MAIN_CSV_PATH):
    print(f"!!! ERRO: Arquivo CSV principal NÃO ENCONTRADO em: {MAIN_CSV_PATH} !!!")
else:
    print("DEBUG: Main CSV file found.")

@pytest.fixture
def test_csv_file(tmp_path):
    d = {'Registro_ANS': [999], 'Razao_Social': ['Test Temp'], 'CNPJ': ['000'], 'UF': ['TT']}
    df = pd.DataFrame(data=d)
    p = tmp_path / "temp_operators.csv"
    df.to_csv(p, index=False, sep=';')
    return str(p)

def test_init_repository_invalid_path():
    with pytest.raises(ValueError):
        CsvOperatorRepository(csv_file_path=None)
    with pytest.raises(ValueError):
        CsvOperatorRepository(csv_file_path=123)

def test_load_data_success():
    if not os.path.exists(MAIN_CSV_PATH):
        pytest.fail(f"Setup failed: Main CSV file not found at expected path: {MAIN_CSV_PATH}. Current dir: {os.getcwd()}")

    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded() is True, f"repo.load_data() failed. Error: {repo._load_error}"
    assert repo._df is not None
    assert not repo._df.empty, "Loaded DataFrame is empty, check the main CSV file."
    assert 'corporate_name' in repo._df.columns
    assert 'registration_ans' in repo._df.columns
    assert 'state_uf' in repo._df.columns
    assert 'Razao_Social' not in repo._df.columns
    assert 'Registro_ANS' not in repo._df.columns
    assert 'UF' not in repo._df.columns

def test_load_data_file_not_found():
    repo = CsvOperatorRepository(csv_file_path=INVALID_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded() is False
    assert repo.get_data_shape() is None
    assert isinstance(repo._load_error, FileNotFoundError)

def test_search_when_not_loaded():
    repo = CsvOperatorRepository(csv_file_path=INVALID_CSV_PATH)
    repo.load_data()
    assert not repo.is_data_loaded()
    results = repo.search(query="test")
    assert results == []

def test_search_no_criteria():
    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded(), f"Prerequisite failed: Data could not be loaded from {MAIN_CSV_PATH}"
    results = repo.search()
    assert results == []

def test_search_returns_operator_instances():
    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded(), f"Prerequisite failed: Data could not be loaded from {MAIN_CSV_PATH}"

    results = repo.search(query="unimed")
    if results:
        assert isinstance(results[0], Operator)
        assert hasattr(results[0], 'corporate_name')
        assert hasattr(results[0], 'registration_ans')

def test_search_by_ddd_returns_operator():
    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded(), f"Prerequisite failed: Data could not be loaded from {MAIN_CSV_PATH}"

    results = repo.search(ddd="11")
    if results:
        assert isinstance(results[0], Operator)
        assert hasattr(results[0], 'city')
        assert results[0].ddd == "11"

def test_search_by_phone_returns_operator():
    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded(), f"Prerequisite failed: Data could not be loaded from {MAIN_CSV_PATH}"

    if repo._df is None:
         pytest.fail("DataFrame is None after loading data.")

    first_valid_phone_series = repo._df[repo._df['phone'].notna() & (repo._df['phone'] != '')].iloc[0] if not repo._df[repo._df['phone'].notna() & (repo._df['phone'] != '')].empty else None

    if first_valid_phone_series is None:
        pytest.skip("Skipping phone search test: No valid phone numbers found in the main CSV.")
        return

    phone_to_search = first_valid_phone_series['phone']
    print(f"DEBUG: Found phone number in CSV to test search: {phone_to_search}")

    results = repo.search(phone=phone_to_search)

    assert len(results) >= 1
    assert isinstance(results[0], Operator)
    assert results[0].phone == phone_to_search

def test_search_no_results():
    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded(), f"Prerequisite failed: Data could not be loaded from {MAIN_CSV_PATH}"

    results = repo.search(query="xyzzy_nonexistent_term_12345")
    assert len(results) == 0

def test_search_with_limit():
    repo = CsvOperatorRepository(csv_file_path=MAIN_CSV_PATH)
    repo.load_data()
    assert repo.is_data_loaded(), f"Prerequisite failed: Data could not be loaded from {MAIN_CSV_PATH}"

    results_unlimited = repo.search(query="a", limit=1000)
    results_limited = repo.search(query="a", limit=5)

    assert len(results_limited) <= 5
    if len(results_unlimited) > 5:
        assert len(results_limited) == 5
    else:
        assert len(results_limited) == len(results_unlimited)

    if results_limited:
        assert isinstance(results_limited[0], Operator)