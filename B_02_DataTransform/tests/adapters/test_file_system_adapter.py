import pytest
import pandas as pd
import zipfile
import os
from unittest.mock import patch, MagicMock, mock_open, call

from src.adapters.file_system_adapter import LocalFileSystemAdapter

@pytest.fixture
def fs_adapter() -> LocalFileSystemAdapter:
    return LocalFileSystemAdapter()

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({'colA': [1, 2], 'colB': ['x', 'y']})

@patch('src.adapters.file_system_adapter.os.path.exists')
@patch('src.adapters.file_system_adapter.zipfile.ZipFile')
@patch('src.adapters.file_system_adapter.os.path.basename')
@patch('src.adapters.file_system_adapter.os.rename')
@patch('src.adapters.file_system_adapter.os.rmdir')
def test_find_extract_success_no_subdir(
    mock_rmdir, mock_rename, mock_basename,
    mock_zipfile, mock_exists, fs_adapter
):
    mock_exists.return_value = True
    mock_zip_ref = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip_ref
    mock_zip_ref.namelist.return_value = ['other_file.txt', 'target_Anexo_I.pdf', 'another.doc']
    mock_basename.return_value = 'target_Anexo_I.pdf'

    zip_path = "/fake/input.zip"
    target_part = "Anexo_I"
    extract_dir = "/fake/temp_dir"
    expected_extracted_path = os.path.join(extract_dir, 'target_Anexo_I.pdf')

    result = fs_adapter.find_and_extract_target_file(zip_path, target_part, extract_dir)

    mock_exists.assert_called_once_with(zip_path)
    mock_zipfile.assert_called_once_with(zip_path, 'r')
    mock_zip_ref.namelist.assert_called_once()
    mock_zip_ref.extract.assert_called_once_with('target_Anexo_I.pdf', extract_dir)
    mock_basename.assert_called_once_with('target_Anexo_I.pdf')
    mock_rename.assert_not_called()
    mock_rmdir.assert_not_called()
    assert result == expected_extracted_path

@patch('src.adapters.file_system_adapter.os.path.exists')
@patch('src.adapters.file_system_adapter.zipfile.ZipFile')
@patch('src.adapters.file_system_adapter.os.path.basename')
@patch('src.adapters.file_system_adapter.os.rename')
@patch('src.adapters.file_system_adapter.os.rmdir')
def test_find_extract_success_with_subdir(
    mock_rmdir, mock_rename, mock_basename,
    mock_zipfile, mock_exists, fs_adapter
):
    mock_exists.return_value = True
    mock_zip_ref = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip_ref
    mock_zip_ref.namelist.return_value = ['folder/target_Anexo_I.pdf', 'other.txt']
    mock_basename.return_value = 'target_Anexo_I.pdf'

    zip_path = "/fake/input.zip"
    target_part = "Anexo_I"
    extract_dir = "/fake/temp_dir"
    original_extracted_path = os.path.join(extract_dir, 'folder/target_Anexo_I.pdf')
    desired_final_path = os.path.join(extract_dir, 'target_Anexo_I.pdf')

    result = fs_adapter.find_and_extract_target_file(zip_path, target_part, extract_dir)

    mock_exists.assert_called_once_with(zip_path)
    mock_zipfile.assert_called_once_with(zip_path, 'r')
    mock_zip_ref.extract.assert_called_once_with('folder/target_Anexo_I.pdf', extract_dir)
    mock_basename.assert_called_once_with('folder/target_Anexo_I.pdf')
    mock_rename.assert_called_once_with(original_extracted_path, desired_final_path)
    mock_rmdir.assert_called_once_with(os.path.dirname(original_extracted_path))
    assert result == desired_final_path

@patch('src.adapters.file_system_adapter.os.path.exists')
def test_find_extract_zip_not_found(mock_exists, fs_adapter):
    mock_exists.return_value = False
    zip_path = "/fake/nonexistent.zip"

    with pytest.raises(FileNotFoundError, match="Input ZIP file not found"):
        fs_adapter.find_and_extract_target_file(zip_path, "Anexo_I", "/fake/temp")

    mock_exists.assert_called_once_with(zip_path)

@patch('src.adapters.file_system_adapter.os.path.exists')
@patch('src.adapters.file_system_adapter.zipfile.ZipFile')
def test_find_extract_target_not_found(mock_zipfile, mock_exists, fs_adapter):
    mock_exists.return_value = True
    mock_zip_ref = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip_ref
    mock_zip_ref.namelist.return_value = ['file1.txt', 'file2.pdf']

    zip_path = "/fake/input.zip"
    target_part = "Anexo_I"

    with pytest.raises(ValueError, match="'Anexo_I' not found in ZIP archive"):
        fs_adapter.find_and_extract_target_file(zip_path, target_part, "/fake/temp")

    mock_exists.assert_called_once_with(zip_path)
    mock_zip_ref.namelist.assert_called_once()

@patch('src.adapters.file_system_adapter.os.path.exists')
@patch('src.adapters.file_system_adapter.zipfile.ZipFile')
def test_find_extract_bad_zip(mock_zipfile, mock_exists, fs_adapter):
    mock_exists.return_value = True
    mock_zipfile.return_value.__enter__.side_effect = zipfile.BadZipFile("Bad zip")

    zip_path = "/fake/bad.zip"

    with pytest.raises(zipfile.BadZipFile, match="Bad zip"):
        fs_adapter.find_and_extract_target_file(zip_path, "Anexo_I", "/fake/temp")

    mock_exists.assert_called_once_with(zip_path)
    mock_zipfile.assert_called_once_with(zip_path, 'r')

@patch('src.adapters.file_system_adapter.os.makedirs')
@patch('src.adapters.file_system_adapter.pandas.DataFrame.to_csv')
@patch('src.adapters.file_system_adapter.zipfile.ZipFile')
@patch('src.adapters.file_system_adapter.os.path.exists')
@patch('src.adapters.file_system_adapter.os.remove')
def test_save_success(
    mock_remove, mock_exists, mock_zipfile,
    mock_to_csv, mock_makedirs,
    fs_adapter, sample_dataframe
):
    mock_zip_write_ref = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip_write_ref
    mock_exists.side_effect = [True, True]

    output_dir = "/fake/output"
    csv_name = "data.csv"
    zip_name = "archive.zip"
    temp_csv_path = os.path.join(output_dir, f"~temp_{csv_name}.csv")
    final_zip_path = os.path.join(output_dir, zip_name)

    fs_adapter.save_dataframe_to_zipped_csv(sample_dataframe, output_dir, csv_name, zip_name)

    mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
    mock_to_csv.assert_called_once_with(temp_csv_path, index=False, encoding='utf-8')
    mock_zipfile.assert_called_once_with(final_zip_path, 'w', zipfile.ZIP_DEFLATED)
    mock_zip_write_ref.write.assert_called_once_with(temp_csv_path, arcname=csv_name)
    mock_remove.assert_called_once_with(temp_csv_path)
    mock_exists.assert_called_once_with(temp_csv_path)

def test_save_none_dataframe(fs_adapter):
    with patch('src.adapters.file_system_adapter.os.makedirs') as mock_makedirs, \
         patch('src.adapters.file_system_adapter.pandas.DataFrame.to_csv') as mock_to_csv, \
         patch('src.adapters.file_system_adapter.zipfile.ZipFile') as mock_zipfile:

        fs_adapter.save_dataframe_to_zipped_csv(None, "/out", "f.csv", "a.zip")

        mock_makedirs.assert_not_called()
        mock_to_csv.assert_not_called()
        mock_zipfile.assert_not_called()

def test_save_empty_dataframe(fs_adapter):
    with patch('src.adapters.file_system_adapter.os.makedirs') as mock_makedirs, \
         patch('src.adapters.file_system_adapter.pandas.DataFrame.to_csv') as mock_to_csv, \
         patch('src.adapters.file_system_adapter.zipfile.ZipFile') as mock_zipfile:

        fs_adapter.save_dataframe_to_zipped_csv(pd.DataFrame(), "/out", "f.csv", "a.zip")

        mock_makedirs.assert_not_called()
        mock_to_csv.assert_not_called()
        mock_zipfile.assert_not_called()

@patch('src.adapters.file_system_adapter.os.makedirs', side_effect=OSError("Permission denied"))
def test_save_makedirs_fails(mock_makedirs, fs_adapter, sample_dataframe):
    with pytest.raises(IOError, match="Failed to create output directory"):
        fs_adapter.save_dataframe_to_zipped_csv(sample_dataframe, "/out", "f.csv", "a.zip")
    mock_makedirs.assert_called_once()

@patch('src.adapters.file_system_adapter.os.makedirs')
@patch('src.adapters.file_system_adapter.pandas.DataFrame.to_csv', side_effect=IOError("Disk full"))
@patch('src.adapters.file_system_adapter.os.path.exists', return_value=False)
@patch('src.adapters.file_system_adapter.os.remove')
def test_save_to_csv_fails(
    mock_remove, mock_exists, mock_to_csv,
    mock_makedirs, fs_adapter, sample_dataframe
):
    output_dir = "/fake/output"
    csv_name = "data.csv"
    zip_name = "archive.zip"
    temp_csv_path = os.path.join(output_dir, f"~temp_{csv_name}.csv")

    with pytest.raises(IOError, match="Disk full"):
        fs_adapter.save_dataframe_to_zipped_csv(sample_dataframe, output_dir, csv_name, zip_name)

    mock_makedirs.assert_called_once()
    mock_to_csv.assert_called_once()
    mock_exists.assert_called_once_with(temp_csv_path)
    mock_remove.assert_called_once_with(temp_csv_path)

@patch('src.adapters.file_system_adapter.os.makedirs')
@patch('src.adapters.file_system_adapter.pandas.DataFrame.to_csv')
@patch('src.adapters.file_system_adapter.zipfile.ZipFile', side_effect=zipfile.BadZipFile("Zip creation failed"))
@patch('src.adapters.file_system_adapter.os.path.exists')
@patch('src.adapters.file_system_adapter.os.remove')
def test_save_zip_creation_fails(
    mock_remove, mock_exists, mock_zipfile,
    mock_to_csv, mock_makedirs,
    fs_adapter, sample_dataframe
):
    output_dir = "/fake/output"
    csv_name = "data.csv"
    zip_name = "archive.zip"
    temp_csv_path = os.path.join(output_dir, f"~temp_{csv_name}.csv")
    final_zip_path = os.path.join(output_dir, zip_name)

    mock_exists.side_effect = [True, True]

    with pytest.raises(zipfile.BadZipFile, match="Zip creation failed"):
        fs_adapter.save_dataframe_to_zipped_csv(sample_dataframe, output_dir, csv_name, zip_name)

    mock_makedirs.assert_called_once()
    mock_to_csv.assert_called_once()
    mock_zipfile.assert_called_once()
    assert mock_exists.call_count == 2
    assert call(final_zip_path) in mock_remove.call_args_list
    assert call(temp_csv_path) in mock_remove.call_args_list