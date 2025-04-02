import pytest
import zipfile
from pathlib import Path

from src.infrastructure.archive import ZipfileExtractor

@pytest.fixture
def zip_extractor():
    """Provides an instance of the ZipfileExtractor."""
    return ZipfileExtractor()

@pytest.fixture
def create_test_zip(tmp_path):
    """Creates a dummy zip file for testing."""
    zip_path = tmp_path / "test.zip"
    file1_content = b"This is file one."
    file2_content = b"This is file two in a subdir."
    file1_path = "file1.txt"
    file2_path = Path("subdir") / "file2.txt" # Path object for subdir structure

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(file1_path, file1_content)
        # ZipInfo requires string paths, ensure conversion
        zf.writestr(str(file2_path), file2_content)

    return {
        "zip_path": zip_path,
        "extract_dir": tmp_path / "extracted",
        "file1_path": file1_path,
        "file1_content": file1_content,
        "file2_path": file2_path, # Keep as Path for assertion checks
        "file2_content": file2_content,
    }

def test_extract_success(zip_extractor, create_test_zip):
    """Tests successful extraction."""
    # Arrange
    zip_info = create_test_zip
    zip_path = zip_info["zip_path"]
    extract_dir = zip_info["extract_dir"]

    # Act
    result = zip_extractor.extract(zip_path, extract_dir)

    # Assert
    assert result is True
    assert extract_dir.exists()
    extracted_file1 = extract_dir / zip_info["file1_path"]
    extracted_file2 = extract_dir / zip_info["file2_path"] # Use Path object here
    assert extracted_file1.exists()
    assert extracted_file1.read_bytes() == zip_info["file1_content"]
    assert extracted_file2.parent.exists() # Check subdir was created
    assert extracted_file2.exists()
    assert extracted_file2.read_bytes() == zip_info["file2_content"]

def test_extract_zip_not_found(zip_extractor, tmp_path):
    """Tests extraction when the zip file doesn't exist."""
    # Arrange
    non_existent_zip = tmp_path / "not_a_real.zip"
    extract_dir = tmp_path / "extracted"

    # Act
    result = zip_extractor.extract(non_existent_zip, extract_dir)

    # Assert
    assert result is False
    assert not extract_dir.exists() # Should not create dir if zip doesn't exist

def test_extract_not_a_zip_file(zip_extractor, tmp_path):
    """Tests extraction when the source is not a valid zip file."""
    # Arrange
    not_a_zip_path = tmp_path / "fake.zip"
    not_a_zip_path.write_text("This is not zip content")
    extract_dir = tmp_path / "extracted"

    # Act
    result = zip_extractor.extract(not_a_zip_path, extract_dir)

    # Assert
    assert result is False