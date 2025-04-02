import pytest
from unittest.mock import MagicMock, mock_open, call
import requests 
from pathlib import Path

from src.infrastructure.web import RequestsDownloader

@pytest.fixture
def downloader():
    """Provides an instance of RequestsDownloader."""
    return RequestsDownloader()

@pytest.fixture
def mock_path_mkdir(mocker):
    """Mocks Path.mkdir to avoid actual directory creation."""
    return mocker.patch.object(Path, 'mkdir')

@pytest.fixture
def mock_builtin_open(mocker):
    """Mocks the built-in open function."""
    # Use mock_open provided by unittest.mock
    m = mock_open()
    mocker.patch('builtins.open', m)
    return m # Return the mock object itself for assertions


# Use patching within each test function for better isolation
def test_download_success(downloader, mock_path_mkdir, mock_builtin_open, mocker):
    """Tests successful download."""
    # Arrange
    url = "http://example.com/file.dat"
    save_path = Path("/tmp/file.dat") # Use Path object
    file_content = b"dummy file content"

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    # Simulate iter_content yielding chunks
    mock_response.iter_content.return_value = [file_content[i:i+5] for i in range(0, len(file_content), 5)]

    # Patch requests.get specifically for this test
    mock_requests_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    result = downloader.download(url, save_path)

    # Assert
    assert result is True
    # Check that the parent directory of save_path had mkdir called
    mock_path_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    # Check requests.get call
    mock_requests_get.assert_called_once_with(url, timeout=60, stream=True)
    mock_response.raise_for_status.assert_called_once()
    # Check file open call
    mock_builtin_open.assert_called_once_with(save_path, 'wb')
    # Check if content was written (mock_open tracks calls to write)
    handle = mock_builtin_open() # Get the file handle mock
    expected_write_calls = [call(file_content[i:i+5]) for i in range(0, len(file_content), 5)]
    handle.write.assert_has_calls(expected_write_calls)


def test_download_http_error(downloader, mock_path_mkdir, mocker):
    """Tests download failure due to HTTP error."""
    # Arrange
    url = "http://example.com/notfound.dat"
    save_path = Path("/tmp/notfound.dat")
    mock_response = MagicMock()
    # Create a mock response object for the error attribute
    error_response_mock = MagicMock(status_code=404, reason="Not Found")
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error: Not Found", response=error_response_mock
    )
    mock_requests_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    result = downloader.download(url, save_path)

    # Assert
    assert result is False
    mock_path_mkdir.assert_called_once() # Directory creation is attempted
    mock_requests_get.assert_called_once_with(url, timeout=60, stream=True)
    mock_response.raise_for_status.assert_called_once()


def test_download_timeout_error(downloader, mock_path_mkdir, mocker):
    """Tests download failure due to timeout."""
    # Arrange
    url = "http://example.com/slow.dat"
    save_path = Path("/tmp/slow.dat")
    mock_requests_get = mocker.patch('requests.get', side_effect=requests.exceptions.Timeout("Connection timed out"))

    # Act
    result = downloader.download(url, save_path, timeout=10) # Use specific timeout

    # Assert
    assert result is False
    mock_path_mkdir.assert_called_once()
    mock_requests_get.assert_called_once_with(url, timeout=10, stream=True)


def test_download_request_exception(downloader, mock_path_mkdir, mocker):
    """Tests download failure due to a generic request exception."""
    # Arrange
    url = "http://invalid-url"
    save_path = Path("/tmp/invalid.dat")
    mock_requests_get = mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Some connection error"))

    # Act
    result = downloader.download(url, save_path)

    # Assert
    assert result is False
    mock_path_mkdir.assert_called_once()
    mock_requests_get.assert_called_once_with(url, timeout=60, stream=True)


def test_download_os_error_on_save(downloader, mock_path_mkdir, mock_builtin_open, mocker):
    """Tests download failure due to OS error when saving file."""
    # Arrange
    url = "http://example.com/file.dat"
    save_path = Path("/tmp/file.dat")
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.iter_content.return_value = [b"data"]
    mock_requests_get = mocker.patch('requests.get', return_value=mock_response)

    # Configure the mock_open to raise OSError on write
    mock_builtin_open.side_effect = OSError("Permission denied")

    # Act
    result = downloader.download(url, save_path)

    # Assert
    assert result is False
    mock_path_mkdir.assert_called_once()
    mock_requests_get.assert_called_once_with(url, timeout=60, stream=True)
    # Check that open was called, even though write failed
    mock_builtin_open.assert_called_once_with(save_path, 'wb')