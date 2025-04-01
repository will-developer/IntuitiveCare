# tests/adapters/test_file_manager.py
import os
import pytest
from src.adapters.file_manager import FileSystemManager

@pytest.fixture
def file_manager():
    return FileSystemManager()

def test_ensure_directory_creates_if_not_exists(file_manager, tmp_path):
    new_dir = tmp_path / "new_folder"
    assert not new_dir.exists()
    result = file_manager.ensure_directory(str(new_dir))
    assert result is True
    assert new_dir.exists()
    assert new_dir.is_dir()

def test_ensure_directory_returns_true_if_exists(file_manager, tmp_path):
    existing_dir = tmp_path / "existing_folder"
    existing_dir.mkdir()
    assert existing_dir.exists()
    result = file_manager.ensure_directory(str(existing_dir))
    assert result is True
    assert existing_dir.exists()

def test_remove_files_removes_existing_files(file_manager, tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.log"
    file1.write_text("content1")
    file2.write_text("content2")

    assert file1.exists()
    assert file2.exists()

    file_manager.remove_files(str(tmp_path), ["file1.txt", "file2.log"])

    assert not file1.exists()
    assert not file2.exists()

def test_remove_files_ignores_non_existing_files(file_manager, tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.write_text("content1")
    assert file1.exists()

    try:
        file_manager.remove_files(str(tmp_path), ["file1.txt", "missing.txt"])
    except Exception as e:
        pytest.fail(f"remove_files raised an exception unexpectedly: {e}")

    assert not file1.exists()

@pytest.mark.parametrize(
    "url, suffix, expected_filename",
    [
        ("http://example.com/path/to/document.pdf", ".pdf", "document.pdf"),
        ("https://server.net/archive/Anexo_II_File.PDF", ".pdf", "Anexo_II_File.PDF"),
        ("http://domain.org/file.pdf?query=123¶m=abc", ".pdf", "file.pdf"),
        ("http://just.domain/no_file_extension", ".pdf", "no_file_extension"),
        ("http://test.com/", ".pdf", None),
        ("http://another.com/weird%20name.pdf", ".pdf", "weird%20name.pdf"),
        ("http://case.com/File.Pdf", ".pdf", "File.Pdf"),
        ("http://wrong.ext/file.txt", ".pdf", None),
    ]
)
def test_get_filename_from_url(file_manager, url, suffix, expected_filename):
    filename = file_manager.get_filename_from_url(url, suffix)
    if expected_filename is None:
        assert suffix in filename
        assert "downloaded_file_" in filename
        assert len(filename) > 40
    else:
        assert filename == expected_filename