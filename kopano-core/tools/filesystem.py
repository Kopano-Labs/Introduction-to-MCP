from pathlib import Path


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    if not path.is_file():
        return f"Error: '{file_path}' is not a file."
    return path.read_text(encoding=encoding)


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)
    return f"Successfully wrote {len(content.encode(encoding)):,} bytes to '{file_path}'."


__all__ = ["read_file", "write_file"]
