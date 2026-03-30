"""
Pytest tests for the tool functions in orch/tools.
"""
import pytest
from pathlib import Path

from orch.tools.filesystem import read_file
from orch.tools.write_file import write_file


def test_write_and_read_file(tmp_path: Path):
    """
    Tests that write_file correctly writes content and read_file can read it back.
    """
    test_file = tmp_path / "test.txt"
    test_content = "Hello, world!\nThis is a test."

    # Test writing
    write_result = write_file(str(test_file), test_content)
    assert "Successfully wrote" in write_result
    assert test_file.exists()
    assert test_file.read_text(encoding='utf-8') == test_content

    # Test reading
    read_result = read_file(str(test_file))
    assert test_content in read_result


def test_read_file_not_found(tmp_path: Path):
    """
    Tests that read_file returns an error for a non-existent file.
    """
    non_existent_file = tmp_path / "not_here.txt"
    result = read_file(str(non_existent_file))
    assert "Error: File not found" in result


def test_read_file_is_directory(tmp_path: Path):
    """
    Tests that read_file returns an error when given a directory path.
    """
    result = read_file(str(tmp_path))
    assert "is not a file" in result


def test_write_file_creates_directories(tmp_path: Path):
    """
    Tests that write_file can create nested directories for the output file.
    """
    nested_file = tmp_path / "new_dir" / "another_dir" / "nested.txt"
    content = "This should be in a nested directory."

    write_result = write_file(str(nested_file), content)
    assert "Successfully wrote" in write_result
    assert nested_file.exists()
    assert nested_file.read_text(encoding='utf-8') == content
