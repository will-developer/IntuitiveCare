import pytest
from unittest.mock import MagicMock, call, patch
from pathlib import Path
import requests

from src.application.use_cases import DownloadAnsDataUseCase
from src.application.dto import DownloadConfig
from src.application.ports import FileSystem, FileDownloader, HtmlParser, ZipExtractor

@pytest.fixture
def mock_fs(mocker):
    """Mock for FileSystem port."""
    return mocker.MagicMock(spec=FileSystem)

@pytest.fixture
def mock_downloader(mocker):
    """Mock for FileDownloader port."""
    return mocker.MagicMock(spec=FileDownloader)

@pytest.fixture
def mock_parser(mocker):
    """Mock for HtmlParser port."""
    return mocker.MagicMock(spec=HtmlParser)

@pytest.fixture
def mock_extractor(mocker):
    """Mock for ZipExtractor port."""
    return mocker.MagicMock(spec=ZipExtractor)

@pytest.fixture
def download_config():
    """Provides a sample DownloadConfig DTO."""
    # Use dummy paths for testing DTO creation
    base = Path("/fake/data")
    return DownloadConfig(
        base_accounting_url="http://fake-ans.gov/acc/",
        operators_csv_url="http://fake-ans.gov/ops.csv",
        years_to_download=["2023", "2024"],
        data_dir=base,
        accounting_dir=base / "accounting",
        zips_dir=base / "accounting" / "zips",
        csvs_dir=base / "accounting" / "csvs",
        operators_dir=base / "operators",
        operators_csv_path=base / "operators" / "operators.csv",
    )

@pytest.fixture
def download_use_case(mock_fs, mock_downloader, mock_parser, mock_extractor):
    """Provides an instance of the use case with mocked dependencies."""
    return DownloadAnsDataUseCase(
        file_system=mock_fs,
        file_downloader=mock_downloader,
        html_parser=mock_parser,
        zip_extractor=mock_extractor,
    )

@patch('requests.get') # Patch at the module level or per test
def test_execute_success(
    mock_requests_get, # Needs to be argument if patched at function level
    download_use_case,
    download_config,
    mock_fs,
    mock_downloader,
    mock_parser,
    mock_extractor
):
    """Tests the successful execution path."""
    # Arrange
    mock_downloader.download.return_value = True # Simulate successful downloads
    mock_extractor.extract.return_value = True   # Simulate successful extractions
    mock_parser.find_links_ending_with.side_effect = [
        ["http://fake-ans.gov/acc/2023/1T2023.zip"], # Links for 2023
        ["http://fake-ans.gov/acc/2024/1T2024.zip"], # Links for 2024
    ]

    # Mock the response from requests.get
    mock_response = MagicMock()
    mock_response.text = "<html><a>Link</a></html>" # Dummy HTML
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response # Configure the mock

    result = download_use_case.execute(download_config)

    assert result is True

    # Check directory creation calls
    expected_dirs = [
        download_config.data_dir, download_config.accounting_dir, download_config.zips_dir,
        download_config.csvs_dir, download_config.operators_dir
    ]
    mock_fs.create_directories.assert_has_calls([call(d) for d in expected_dirs], any_order=True)

    # Check operator download call
    mock_downloader.download.assert_any_call(
        download_config.operators_csv_url, download_config.operators_csv_path
    )

    # Check requests.get calls for HTML fetching
    mock_requests_get.assert_has_calls([
        call("http://fake-ans.gov/acc/2023/", timeout=30),
        call("http://fake-ans.gov/acc/2024/", timeout=30),
    ], any_order=True)

    # Check parser calls
    mock_parser.find_links_ending_with.assert_has_calls([
        call("http://fake-ans.gov/acc/2023/", mock_response.text, ".zip"),
        call("http://fake-ans.gov/acc/2024/", mock_response.text, ".zip"),
    ])

    # Check zip download and extraction calls
    zip_url_2023 = "http://fake-ans.gov/acc/2023/1T2023.zip"
    zip_path_2023 = download_config.zips_dir / "1T2023.zip"
    zip_url_2024 = "http://fake-ans.gov/acc/2024/1T2024.zip"
    zip_path_2024 = download_config.zips_dir / "1T2024.zip"

    mock_downloader.download.assert_any_call(zip_url_2023, zip_path_2023)
    mock_extractor.extract.assert_any_call(zip_path_2023, download_config.csvs_dir)
    mock_downloader.download.assert_any_call(zip_url_2024, zip_path_2024)
    mock_extractor.extract.assert_any_call(zip_path_2024, download_config.csvs_dir)


@patch('requests.get')
def test_execute_operator_download_fails(
    mock_requests_get, download_use_case, download_config, mock_downloader, mock_extractor, mock_parser
):
    # Arrange
    # Operator download fails, accounting download/extract succeeds
    mock_downloader.download.side_effect = [False, True, True] # Op fails, Zips succeed
    mock_extractor.extract.return_value = True
    # Mock parser and requests.get as in success test
    mock_parser.find_links_ending_with.side_effect = [["http://z.zip"], ["http://y.zip"]]
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    # Act
    result = download_use_case.execute(download_config)

    # Assert
    assert result is True # Should still return True if accounting succeeds
    # Check that operator download was attempted first
    mock_downloader.download.assert_any_call(
        download_config.operators_csv_url, download_config.operators_csv_path
    )
    # Check that accounting download/extraction was still attempted
    assert mock_extractor.extract.call_count == 2


@patch('requests.get')
def test_execute_html_fetch_fails(
    mock_requests_get, download_use_case, download_config, mock_downloader
):
    """Tests when fetching the HTML page for a year fails."""
    # Arrange
    mock_downloader.download.return_value = True # Operator download succeeds
    mock_requests_get.side_effect = requests.exceptions.RequestException("Fetch failed")

    # Act
    result = download_use_case.execute(download_config)

    # Assert
    assert result is False
    mock_downloader.download.assert_called_once_with( # Only operator download attempted
        download_config.operators_csv_url, download_config.operators_csv_path
    )


@patch('requests.get')
def test_execute_zip_extraction_fails(
    mock_requests_get, download_use_case, download_config, mock_downloader, mock_extractor, mock_parser
):
    """Tests when zip extraction fails."""
    # Arrange
    mock_downloader.download.return_value = True # All downloads succeed
    mock_extractor.extract.return_value = False  # Extraction fails
    # Mock parser and requests.get
    mock_parser.find_links_ending_with.side_effect = [["http://z.zip"], ["http://y.zip"]]
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    # Act
    result = download_use_case.execute(download_config)

    # Assert
    assert result is False # Fails if no extractions succeed
    assert mock_downloader.download.call_count == 3 # Operator + 2 Zips
    assert mock_extractor.extract.call_count == 2 # Both extractions attempted


@patch('requests.get')
def test_execute_no_zip_links_found(
    mock_requests_get, download_use_case, download_config, mock_downloader, mock_parser
):
    """Tests when the parser finds no zip links."""
    # Arrange
    mock_downloader.download.return_value = True # Operator download succeeds
    mock_parser.find_links_ending_with.return_value = [] # No links found
    # Mock requests.get
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    # Act
    result = download_use_case.execute(download_config)

    # Assert
    assert result is False # Fails if no zips to process
    mock_downloader.download.assert_called_once_with( # Only operator download happened
        download_config.operators_csv_url, download_config.operators_csv_path
    )
    assert mock_parser.find_links_ending_with.call_count == 2 # Parser was called for both years