import pytest
import zipfile
from src.adapters.archive_manager import ZipArchiveManager

@pytest.fixture
def archive_manager():
    return ZipArchiveManager()

@pytest.fixture
def source_folder(tmp_path):
    src_dir = tmp_path / "source_files"
    src_dir.mkdir()
    (src_dir / "file1.txt").write_text("content1")
    (src_dir / "file2.pdf").write_text("content2")
    (src_dir / "empty.dat").touch()
    return src_dir

def test_create_archive_success(archive_manager, source_folder, tmp_path):
    zip_filepath = tmp_path / "archive.zip"
    filenames_to_zip = ["file1.txt", "file2.pdf", "empty.dat"]

    result = archive_manager.create_archive(str(source_folder), str(zip_filepath), filenames_to_zip)

    assert result is True
    assert zip_filepath.exists()

    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        zipped_files = zf.namelist()
        assert sorted(zipped_files) == sorted(filenames_to_zip)
        assert zf.read("file1.txt") == b"content1"

def test_create_archive_ignores_missing_files(archive_manager, source_folder, tmp_path):
    zip_filepath = tmp_path / "partial_archive.zip"
    filenames_to_zip = ["file1.txt", "missing.txt"]

    result = archive_manager.create_archive(str(source_folder), str(zip_filepath), filenames_to_zip)

    assert result is True
    assert zip_filepath.exists()

    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        zipped_files = zf.namelist()
        assert zipped_files == ["file1.txt"]

def test_create_archive_empty_list(archive_manager, source_folder, tmp_path):
    zip_filepath = tmp_path / "empty_archive.zip"
    filenames_to_zip = []

    result = archive_manager.create_archive(str(source_folder), str(zip_filepath), filenames_to_zip)

    assert result is True
    assert zip_filepath.exists()

    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        assert zf.namelist() == []