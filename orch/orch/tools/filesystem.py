import os
from pathlib import Path

def read_file(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist."
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

def write_file(file_path: str, content: str) -> str:
    """Writes content to a file."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to '{file_path}'."
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"

def list_directory(directory_path: str = ".") -> str:
    """Lists the contents of a directory."""
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: Directory '{directory_path}' does not exist."
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory."
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory '{directory_path}': {e}"

def delete_file(file_path: str) -> str:
    """Deletes a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist."
        if path.is_dir():
            return f"Error: '{file_path}' is a directory, not a file."
        path.unlink()
        return f"Successfully deleted '{file_path}'."
    except Exception as e:
        return f"Error deleting file '{file_path}': {e}"
