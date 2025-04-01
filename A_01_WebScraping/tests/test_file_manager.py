import pytest
from src.adapters.file_manager import FileSystemManager

# Fixture that provides a FileSystemManager instance for tests
@pytest.fixture
def file_manager():
    return FileSystemManager()

# Test creating a new directory when it doesn't exist
def test_ensure_directory_creates_if_not_exists(file_manager, tmp_path):
    new_dir = tmp_path / "new_folder"
    assert not new_dir.exists()  # Verify directory doesn't exist yet
    result = file_manager.ensure_directory(str(new_dir))  # Try to create it
    assert result is True  # Should return True on success
    assert new_dir.exists()  # Directory should now exist
    assert new_dir.is_dir()  # Should be a directory (not file)

# Test behavior when directory already exists
def test_ensure_directory_returns_true_if_exists(file_manager, tmp_path):
    existing_dir = tmp_path / "existing_folder"
    existing_dir.mkdir()  # Create directory first
    assert existing_dir.exists()  # Verify it exists
    result = file_manager.ensure_directory(str(existing_dir))  # Try to "create" again
    assert result is True  # Should return True (already exists)
    assert existing_dir.exists()  # Should still exist

# Test removing existing files
def test_remove_files_removes_existing_files(file_manager, tmp_path):
    # Create test files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.log"
    file1.write_text("content1")
    file2.write_text("content2")

    assert file1.exists()  # Verify files exist before removal
    assert file2.exists()

    file_manager.remove_files(str(tmp_path), ["file1.txt", "file2.log"])  # Remove them

    assert not file1.exists()  # Verify files were removed
    assert not file2.exists()

# Test removing files when some don't exist
def test_remove_files_ignores_non_existing_files(file_manager, tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.write_text("content1")
    assert file1.exists()  # Only file1 exists

    try:
        # Try to remove both existing and non-existing file
        file_manager.remove_files(str(tmp_path), ["file1.txt", "missing.txt"])
    except Exception as e:
        pytest.fail(f"remove_files raised an exception unexpectedly: {e}")

    assert not file1.exists()  # Existing file should be removed

# Test extracting filenames from URLs with different cases
@pytest.mark.parametrize(
    "url, suffix, expected_filename",
    [
        # Test cases with expected successful extraction
        ("http://example.com/path/to/document.pdf", ".pdf", "document.pdf"),
        ("https://server.net/archive/Anexo_II_File.PDF", ".pdf", "Anexo_II_File.PDF"),
        ("http://domain.org/file.pdf?query=123¶m=abc", ".pdf", "file.pdf"),
        ("http://weird.com/weird%20name.pdf", ".pdf", "weird%20name.pdf"),
        ("http://case.com/File.Pdf", ".pdf", "File.Pdf"),
        
        # Test cases where extraction should fail (use fallback)
        ("http://just.domain/no_file_extension", ".pdf", None),  # No extension
        ("http://test.com/", ".pdf", None),  # No filename at all
        ("http://wrong.ext/file.txt", ".pdf", None),  # Wrong extension
    ]
)
def test_get_filename_from_url(file_manager, url, suffix, expected_filename):
    filename = file_manager.get_filename_from_url(url, suffix)
    if expected_filename is None:
        # For failed cases, verify fallback filename format
        assert suffix in filename  # Should have correct suffix
        assert "downloaded_file_" in filename  # Should have prefix
        assert len(filename) > 40  # Should be long enough (contains UUID)
    else:
        # For success cases, verify exact match
        assert filename == expected_filename