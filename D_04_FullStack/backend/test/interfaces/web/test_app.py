import pytest
import json
from unittest.mock import MagicMock, create_autospec
from src.interfaces.web.app import create_app
from src.application.repositories.operator_repository import OperatorRepository
from src.application.use_cases.search_operators import SearchOperatorsUseCase

@pytest.fixture
def mock_repo() -> MagicMock:
    repo = create_autospec(OperatorRepository, instance=True)
    return repo

@pytest.fixture
def mock_use_case() -> MagicMock:
    uc = create_autospec(SearchOperatorsUseCase, instance=True)
    return uc

@pytest.fixture
def test_client(mock_repo: MagicMock, mock_use_case: MagicMock):
    app = create_app(
        operator_repository=mock_repo,
        search_operators_use_case=mock_use_case
    )
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route_data_loaded(test_client, mock_repo: MagicMock):
    mock_repo.is_data_loaded.return_value = True
    mock_repo.get_data_shape.return_value = (100, 15)
    response = test_client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "API is running and data is loaded."
    assert data['data_shape'] == [100, 15]

def test_index_route_data_not_loaded(test_client, mock_repo: MagicMock):
    mock_repo.is_data_loaded.return_value = False
    response = test_client.get('/')
    assert response.status_code == 503
    data = json.loads(response.data)
    assert data['message'] == "API is running, but data failed to load or is not loaded yet."

def test_search_route_success_returns_portuguese_keys(test_client, mock_repo: MagicMock, mock_use_case: MagicMock):
    mock_repo.is_data_loaded.return_value = True
    mock_search_result_portuguese = [
        {'Registro_ANS': '123', 'Razao_Social': 'Found Corp 1 PT', 'CNPJ': '111'},
        {'Registro_ANS': '456', 'Razao_Social': 'Found Corp 2 PT', 'CNPJ': '222'}
    ]
    mock_use_case.execute.return_value = mock_search_result_portuguese

    response = test_client.get('/api/search?q=corp&ddd=11&telefone=9999')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data == mock_search_result_portuguese
    assert len(data) == 2
    assert 'Registro_ANS' in data[0]
    assert 'Razao_Social' in data[0]
    assert data[0]['Razao_Social'] == 'Found Corp 1 PT'
    assert 'registration_ans' not in data[0]
    assert 'corporate_name' not in data[0]

    mock_use_case.execute.assert_called_once_with(
        query='corp',
        ddd='11',
        phone='9999'
    )
    mock_repo.is_data_loaded.assert_called_once()

def test_search_route_no_params(test_client, mock_repo: MagicMock, mock_use_case: MagicMock):
    mock_repo.is_data_loaded.return_value = True
    mock_use_case.execute.return_value = []

    response = test_client.get('/api/search')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []
    mock_use_case.execute.assert_called_once_with(
        query=None,
        ddd=None,
        phone=None
    )

def test_search_route_data_not_loaded(test_client, mock_repo: MagicMock, mock_use_case: MagicMock):
    mock_repo.is_data_loaded.return_value = False

    response = test_client.get('/api/search?q=test')

    assert response.status_code == 503
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == "Data is not available for searching"
    mock_use_case.execute.assert_not_called()

def test_search_route_internal_error(test_client, mock_repo: MagicMock, mock_use_case: MagicMock):
    mock_repo.is_data_loaded.return_value = True
    mock_use_case.execute.side_effect = Exception("Something went wrong!")

    response = test_client.get('/api/search?q=test')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == "Internal server error during search"
    mock_use_case.execute.assert_called_once_with(query='test', ddd=None, phone=None)