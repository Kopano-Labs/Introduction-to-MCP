import os

def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a specified file, creating directories if they don't exist.

    Args:
        file_path: The path to the file to write.
        content: The content to write to the file.

    Returns:
        A confirmation message or an error string.
    """
    print(f"TOOL: Attempting to write to file: '{file_path}'...")

    # IMPORTANT: In a production environment, write access must be strictly sandboxed
    # to prevent agents from overwriting critical files or introducing security risks.
    # This implementation is for demonstration purposes in a controlled environment.

    try:
        # Ensure the directory exists
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"