import pytest
import zipfile
from src.adapters.archive_manager import ZipArchiveManager

# Fixture that provides a ZipArchiveManager instance for tests
@pytest.fixture
def archive_manager():
    return ZipArchiveManager()

# Fixture that creates a temporary folder with test files
@pytest.fixture
def source_folder(tmp_path):
    src_dir = tmp_path / "source_files"  # Create source folder
    src_dir.mkdir()
    (src_dir / "file1.txt").write_text("content1")  # Create test file 1
    (src_dir / "file2.pdf").write_text("content2")  # Create test file 2
    (src_dir / "empty.dat").touch()  # Create empty test file
    return src_dir

# Test case for successful archive creation
def test_create_archive_success(archive_manager, source_folder, tmp_path):
    zip_filepath = tmp_path / "archive.zip"  # Path for test zip file
    filenames_to_zip = ["file1.txt", "file2.pdf", "empty.dat"]  # Files to include

    # Create the archive
    result = archive_manager.create_archive(str(source_folder), str(zip_filepath), filenames_to_zip)

    # Verify results
    assert result is True  # Check operation succeeded
    assert zip_filepath.exists()  # Check zip file was created

    # Verify zip contents
    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        zipped_files = zf.namelist()  # Get list of files in zip
        assert sorted(zipped_files) == sorted(filenames_to_zip)  # Check all files are there
        assert zf.read("file1.txt") == b"content1"  # Check file content

# Test case for handling missing files
def test_create_archive_ignores_missing_files(archive_manager, source_folder, tmp_path):
    zip_filepath = tmp_path / "partial_archive.zip"  # Path for test zip
    filenames_to_zip = ["file1.txt", "missing.txt"]  # Includes one missing file

    # Create the archive
    result = archive_manager.create_archive(str(source_folder), str(zip_filepath), filenames_to_zip)

    # Verify results
    assert result is True  # Operation should still succeed
    assert zip_filepath.exists()  # Zip file should be created

    # Verify only existing file was added
    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        zipped_files = zf.namelist()
        assert zipped_files == ["file1.txt"]  # Only existing file should be in zip

# Test case for empty file list
def test_create_archive_empty_list(archive_manager, source_folder, tmp_path):
    zip_filepath = tmp_path / "empty_archive.zip"  # Path for test zip
    filenames_to_zip = []  # Empty list of files

    # Create the archive
    result = archive_manager.create_archive(str(source_folder), str(zip_filepath), filenames_to_zip)

    # Verify results
    assert result is True  # Operation should succeed
    assert zip_filepath.exists()  # Zip file should be created

    # Verify zip is empty
    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        assert zf.namelist() == []  # Zip should contain no files