import pytest
import requests
from src.adapters.file_downloader import RequestsFileDownloader

# Fixture that provides a RequestsFileDownloader instance for tests
@pytest.fixture
def file_downloader():
    return RequestsFileDownloader()

# Test successful file download scenario
def test_download_success(file_downloader, requests_mock, tmp_path):
    test_url = "http://test.com/file.pdf"  # Mock URL
    filename = "downloaded.pdf"  # Destination filename
    destination_folder = tmp_path  # Temporary test folder
    expected_content = b"%PDF-1.4\nFake PDF content."  # Mock PDF content
    
    # Setup mock HTTP response
    requests_mock.get(test_url, content=expected_content, status_code=200)

    # Execute download
    result = file_downloader.download(test_url, str(destination_folder), filename, timeout=5)
    filepath = destination_folder / filename  # Full path to downloaded file

    # Verify results
    assert result is True  # Download should succeed
    assert filepath.exists()  # File should exist
    assert filepath.read_bytes() == expected_content  # Content should match
    assert requests_mock.called  # Mock should have been called
    assert requests_mock.last_request.url == test_url  # Correct URL should be called

# Test different HTTP error scenarios (404, 500, 403)
@pytest.mark.parametrize("status_code", [404, 500, 403])
def test_download_http_error(file_downloader, requests_mock, tmp_path, status_code):
    test_url = f"http://test.com/error_{status_code}.pdf"  # Error URL
    filename = "error.pdf"  # Destination filename
    destination_folder = tmp_path  # Temporary test folder
    
    # Setup mock HTTP error response
    requests_mock.get(test_url, status_code=status_code)

    # Execute download
    result = file_downloader.download(test_url, str(destination_folder), filename, timeout=5)
    filepath = destination_folder / filename  # Full path to attempted download

    # Verify results
    assert result is False  # Download should fail
    assert not filepath.exists()  # File should not exist
    assert requests_mock.called  # Mock should have been called

# Test download timeout scenario
def test_download_timeout(file_downloader, requests_mock, tmp_path):
    test_url = "http://test.com/timeout.pdf"  # Timeout URL
    filename = "timeout.pdf"  # Destination filename
    destination_folder = tmp_path  # Temporary test folder
    
    # Setup mock timeout exception
    requests_mock.get(test_url, exc=requests.exceptions.Timeout)

    # Execute download
    result = file_downloader.download(test_url, str(destination_folder), filename, timeout=5)
    filepath = destination_folder / filename  # Full path to attempted download

    # Verify results
    assert result is False  # Download should fail
    assert not filepath.exists()  # File should not exist
    assert requests_mock.called  # Mock should have been called