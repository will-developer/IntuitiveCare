import pytest
import requests
from src.adapters.http_gateway import RequestsHttpGateway

# Fixture that provides a RequestsHttpGateway instance for tests
@pytest.fixture
def http_gateway():
    return RequestsHttpGateway()

# Test successful HTTP GET request
def test_get_content_success(http_gateway, requests_mock):
    test_url = "http://test.com/page"  # Test URL
    expected_content = "<html>Success</html>"  # Expected response content
    
    # Setup mock HTTP response
    requests_mock.get(test_url, text=expected_content, status_code=200)

    # Make the HTTP request
    content = http_gateway.get_content(test_url, timeout=5)

    # Verify results
    assert content == expected_content  # Should return expected content
    assert requests_mock.called  # Should have made the request
    assert requests_mock.last_request.url == test_url  # Should call correct URL

# Test different HTTP error responses (404, 500, 403)
@pytest.mark.parametrize("status_code", [404, 500, 403])
def test_get_content_http_error(http_gateway, requests_mock, status_code):
    test_url = f"http://test.com/error_{status_code}"  # Test URL with error
    
    # Setup mock error response
    requests_mock.get(test_url, status_code=status_code)

    # Make the HTTP request
    content = http_gateway.get_content(test_url, timeout=5)

    # Verify results
    assert content is None  # Should return None for errors
    assert requests_mock.called  # Should have made the request

# Test request timeout scenario
def test_get_content_timeout(http_gateway, requests_mock):
    test_url = "http://test.com/timeout"  # Test URL
    
    # Setup mock timeout exception
    requests_mock.get(test_url, exc=requests.exceptions.Timeout)

    # Make the HTTP request
    content = http_gateway.get_content(test_url, timeout=5)

    # Verify results
    assert content is None  # Should return None on timeout
    assert requests_mock.called  # Should have attempted the request

# Test connection error scenario
def test_get_content_connection_error(http_gateway, requests_mock):
    test_url = "http://test.com/connect_error"  # Test URL
    
    # Setup mock connection error
    requests_mock.get(test_url, exc=requests.exceptions.ConnectionError)

    # Make the HTTP request
    content = http_gateway.get_content(test_url, timeout=5)

    # Verify results
    assert content is None  # Should return None on connection error
    assert requests_mock.called  # Should have attempted the request