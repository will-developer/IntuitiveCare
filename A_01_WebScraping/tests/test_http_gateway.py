import pytest
import requests
from src.adapters.http_gateway import RequestsHttpGateway

@pytest.fixture
def http_gateway():
    return RequestsHttpGateway()

def test_get_content_success(http_gateway, requests_mock):
    test_url = "http://test.com/page"
    expected_content = "<html>Success</html>"
    requests_mock.get(test_url, text=expected_content, status_code=200)

    content = http_gateway.get_content(test_url, timeout=5)

    assert content == expected_content
    assert requests_mock.called
    assert requests_mock.last_request.url == test_url

@pytest.mark.parametrize("status_code", [404, 500, 403])
def test_get_content_http_error(http_gateway, requests_mock, status_code):
    test_url = f"http://test.com/error_{status_code}"
    requests_mock.get(test_url, status_code=status_code)

    content = http_gateway.get_content(test_url, timeout=5)

    assert content is None
    assert requests_mock.called

def test_get_content_timeout(http_gateway, requests_mock):
    test_url = "http://test.com/timeout"
    requests_mock.get(test_url, exc=requests.exceptions.Timeout)

    content = http_gateway.get_content(test_url, timeout=5)

    assert content is None
    assert requests_mock.called

def test_get_content_connection_error(http_gateway, requests_mock):
    test_url = "http://test.com/connect_error"
    requests_mock.get(test_url, exc=requests.exceptions.ConnectionError)

    content = http_gateway.get_content(test_url, timeout=5)

    assert content is None
    assert requests_mock.called