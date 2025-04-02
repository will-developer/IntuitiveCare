import pytest
from unittest.mock import MagicMock, create_autospec
from src.application.use_cases.search_operators import SearchOperatorsUseCase
from src.application.repositories.operator_repository import OperatorRepository
from src.domain.entities.operator import Operator

@pytest.fixture
def mock_operator_repo() -> MagicMock:
    mock_repo = create_autospec(OperatorRepository, instance=True)
    return mock_repo

def test_search_operators_success_returns_portuguese_keys(mock_operator_repo: MagicMock):
    mock_operator_repo.is_data_loaded.return_value = True
    op1 = Operator(registration_ans="111", corporate_name="Test Op 1 PT", city="Cidade1")
    op2 = Operator(registration_ans="222", corporate_name="Test Op 2 PT", city="Cidade2")
    mock_operator_repo.search.return_value = [op1, op2]

    use_case = SearchOperatorsUseCase(operator_repository=mock_operator_repo)

    results = use_case.execute(query="test", limit=10)

    mock_operator_repo.search.assert_called_once_with(
        query="test", ddd=None, phone=None, limit=10
    )
    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert isinstance(results[1], dict)

    assert 'Registro_ANS' in results[0]
    assert 'Razao_Social' in results[0]
    assert 'Cidade' in results[0]
    assert results[0]['Registro_ANS'] == "111"
    assert results[0]['Razao_Social'] == "Test Op 1 PT"
    assert results[0]['Cidade'] == "Cidade1"

    assert 'registration_ans' not in results[0]
    assert 'corporate_name' not in results[0]
    assert 'city' not in results[0]

    assert results[1]['Registro_ANS'] == "222"
    assert results[1]['Razao_Social'] == "Test Op 2 PT"

def test_search_operators_data_not_loaded(mock_operator_repo: MagicMock):
    mock_operator_repo.is_data_loaded.return_value = False
    use_case = SearchOperatorsUseCase(operator_repository=mock_operator_repo)

    results = use_case.execute(query="test")

    assert results == []
    mock_operator_repo.search.assert_not_called()

def test_search_operators_passes_all_params(mock_operator_repo: MagicMock):
    mock_operator_repo.is_data_loaded.return_value = True
    mock_operator_repo.search.return_value = []
    use_case = SearchOperatorsUseCase(operator_repository=mock_operator_repo)

    use_case.execute(query="abc", ddd="11", phone="1234", limit=5)

    mock_operator_repo.search.assert_called_once_with(
        query="abc", ddd="11", phone="1234", limit=5
    )

def test_search_operators_handles_empty_repo_result(mock_operator_repo: MagicMock):
    mock_operator_repo.is_data_loaded.return_value = True
    mock_operator_repo.search.return_value = []
    use_case = SearchOperatorsUseCase(operator_repository=mock_operator_repo)

    results = use_case.execute(query="findme")

    assert results == []
    mock_operator_repo.search.assert_called_once_with(
        query="findme", ddd=None, phone=None, limit=50
    )

def test_init_use_case_with_invalid_repo():
    with pytest.raises(TypeError):
        SearchOperatorsUseCase(operator_repository="not a repo")
    with pytest.raises(TypeError):
        SearchOperatorsUseCase(operator_repository=object())