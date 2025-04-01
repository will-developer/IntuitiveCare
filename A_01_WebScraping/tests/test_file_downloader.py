import pytest
import requests
from src.adapters.file_downloader import RequestsFileDownloader

@pytest.fixture
def file_downloader():
    return RequestsFileDownloader()

def test_download_success(file_downloader, requests_mock, tmp_path):
    test_url = "http://test.com/file.pdf"
    filename = "downloaded.pdf"
    destination_folder = tmp_path
    expected_content = b"%PDF-1.4\nFake PDF content."
    requests_mock.get(test_url, content=expected_content, status_code=200)

    result = file_downloader.download(test_url, str(destination_folder), filename, timeout=5)
    filepath = destination_folder / filename

    assert result is True
    assert filepath.exists()
    assert filepath.read_bytes() == expected_content
    assert requests_mock.called
    assert requests_mock.last_request.url == test_url

@pytest.mark.parametrize("status_code", [404, 500, 403])
def test_download_http_error(file_downloader, requests_mock, tmp_path, status_code):
    test_url = f"http://test.com/error_{status_code}.pdf"
    filename = "error.pdf"
    destination_folder = tmp_path
    requests_mock.get(test_url, status_code=status_code)

    result = file_downloader.download(test_url, str(destination_folder), filename, timeout=5)
    filepath = destination_folder / filename

    assert result is False
    assert not filepath.exists()
    assert requests_mock.called

def test_download_timeout(file_downloader, requests_mock, tmp_path):
    test_url = "http://test.com/timeout.pdf"
    filename = "timeout.pdf"
    destination_folder = tmp_path
    requests_mock.get(test_url, exc=requests.exceptions.Timeout)

    result = file_downloader.download(test_url, str(destination_folder), filename, timeout=5)
    filepath = destination_folder / filename

    assert result is False
    assert not filepath.exists()
    assert requests_mock.called