import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.adapters.pdf_reader_adapter import TabulaPdfReader

@pytest.fixture
def pdf_reader() -> TabulaPdfReader:
    return TabulaPdfReader()

@pytest.fixture
def mock_dataframe() -> pd.DataFrame:
    return pd.DataFrame({'col1': ['data1'], 'col2': ['data2']})

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_returns_list(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader, mock_dataframe: pd.DataFrame):
    mock_read_pdf.return_value = [mock_dataframe, mock_dataframe.copy()]
    pdf_path = "dummy/path/to.pdf"

    result = pdf_reader.extract_tables_from_pdf(pdf_path)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] is mock_dataframe
    mock_read_pdf.assert_called_once_with(
        pdf_path,
        pages='all',
        lattice=True,
        pandas_options={'dtype': str}
    )

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_returns_single_dataframe(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader, mock_dataframe: pd.DataFrame):
    mock_read_pdf.return_value = mock_dataframe
    pdf_path = "dummy/path/to.pdf"

    result = pdf_reader.extract_tables_from_pdf(pdf_path)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] is mock_dataframe
    mock_read_pdf.assert_called_once()

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_returns_none(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader):
    mock_read_pdf.return_value = None
    pdf_path = "dummy/path/to.pdf"

    result = pdf_reader.extract_tables_from_pdf(pdf_path)

    assert isinstance(result, list)
    assert len(result) == 0
    mock_read_pdf.assert_called_once()

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_returns_empty_list(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader):
    mock_read_pdf.return_value = []
    pdf_path = "dummy/path/to.pdf"

    result = pdf_reader.extract_tables_from_pdf(pdf_path)

    assert isinstance(result, list)
    assert len(result) == 0
    mock_read_pdf.assert_called_once()

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_returns_list_with_none(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader, mock_dataframe: pd.DataFrame):
    mock_read_pdf.return_value = [mock_dataframe, None, mock_dataframe.copy()]
    pdf_path = "dummy/path/to.pdf"

    result = pdf_reader.extract_tables_from_pdf(pdf_path)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] is mock_dataframe
    mock_read_pdf.assert_called_once()

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_raises_exception(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader):
    mock_read_pdf.side_effect = Exception("Tabula failed miserably")
    pdf_path = "dummy/path/to.pdf"

    with pytest.raises(Exception, match="Tabula failed miserably"):
        pdf_reader.extract_tables_from_pdf(pdf_path)

    mock_read_pdf.assert_called_once()

@patch('src.adapters.pdf_reader_adapter.tabula.read_pdf')
def test_extract_tables_returns_unexpected_type(mock_read_pdf: MagicMock, pdf_reader: TabulaPdfReader):
    mock_read_pdf.return_value = "this is not a dataframe or list"
    pdf_path = "dummy/path/to.pdf"

    result = pdf_reader.extract_tables_from_pdf(pdf_path)

    assert isinstance(result, list)
    assert len(result) == 0
    mock_read_pdf.assert_called_once()