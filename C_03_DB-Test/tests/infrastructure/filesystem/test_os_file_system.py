import pytest
from pathlib import Path

from src.infrastructure.filesystem import OsFileSystem

@pytest.fixture
def fs():
    """Provides an instance of OsFileSystem."""
    return OsFileSystem()

def test_create_directories(fs, tmp_path):
    """Tests creating directories."""
    # Arrange
    new_dir = tmp_path / "a" / "b" / "c"
    assert not new_dir.exists() # Ensure it doesn't exist initially

    # Act
    fs.create_directories(new_dir)

    # Assert
    assert new_dir.exists()
    assert new_dir.is_dir()

    # Test creating existing directory (should not raise error)
    try:
        fs.create_directories(new_dir)
    except Exception as e:
        pytest.fail(f"create_directories raised an exception on existing dir: {e}")

def test_list_files(fs, tmp_path):
    """Tests listing files with a pattern."""
    # Arrange
    dir_path = tmp_path / "list_test"
    dir_path.mkdir()
    file1 = dir_path / "file1.txt"
    file2 = dir_path / "file2.csv"
    file3 = dir_path / "another.txt"
    subdir = dir_path / "subdir"
    subdir.mkdir()
    file4 = subdir / "subfile.txt"

    file1.touch()
    file2.touch()
    file3.touch()
    file4.touch()

    # Act
    txt_files = fs.list_files(dir_path, "*.txt")
    csv_files = fs.list_files(dir_path, "*.csv")
    all_files = fs.list_files(dir_path, "*") # Should not list recursively by default
    sub_files = fs.list_files(subdir, "*.txt")
    empty_files = fs.list_files(dir_path, "*.log")
    non_existent_dir_files = fs.list_files(tmp_path / "ghost", "*")


    # Assert
    # Use sets for easier comparison when order doesn't matter
    assert set(txt_files) == {file1, file3}
    assert set(csv_files) == {file2}
    # Glob '*' might include subdirectories depending on OS/Pathlib version, filter to files
    assert set(f for f in all_files if f.is_file()) == {file1, file2, file3}
    assert set(sub_files) == {file4}
    assert set(empty_files) == set()
    assert set(non_existent_dir_files) == set()


def test_get_absolute_path(fs, tmp_path):
    """Tests getting the absolute path."""
    # Arrange
    # Create a file within tmp_path to ensure it's handled correctly
    relative_file = Path("temp.file") # Relative path string
    absolute_file = tmp_path / relative_file
    absolute_file.touch()

    # Act
    # Get absolute path of the file created inside tmp_path
    abs_path = fs.get_absolute_path(absolute_file)

    # Assert
    assert abs_path.is_absolute()
    assert abs_path == absolute_file.resolve()

def test_path_exists(fs, tmp_path):
    """Tests checking path existence."""
    # Arrange
    existing_file = tmp_path / "exists.txt"
    existing_dir = tmp_path / "dir_exists"
    non_existent = tmp_path / "ghost"
    existing_file.touch()
    existing_dir.mkdir()

    # Act & Assert
    assert fs.path_exists(existing_file) is True
    assert fs.path_exists(existing_dir) is True
    assert fs.path_exists(non_existent) is False

def test_get_filename(fs, tmp_path):
    """Tests getting the filename from a path."""
    # Arrange
    p1 = Path("/some/dir/file.txt")
    p2 = tmp_path / "another_file.zip"
    p3 = Path("relative/path/doc.pdf")
    p4 = tmp_path # A directory path object
    p5 = Path("just_a_file.csv")

    # Act & Assert
    assert fs.get_filename(p1) == "file.txt"
    assert fs.get_filename(p2) == "another_file.zip"
    assert fs.get_filename(p3) == "doc.pdf"
    assert fs.get_filename(p4) == tmp_path.name
    assert fs.get_filename(p5) == "just_a_file.csv"