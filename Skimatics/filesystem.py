import os

def read_file(file_path: str) -> str:
    """
    Reads the content of a specified file.

    Args:
        file_path: The path to the file to read.

    Returns:
        The content of the file as a string, or an error message if the file
        cannot be read.
    """
    print(f"TOOL: Attempting to read file: '{file_path}'...")
    
    # IMPORTANT: In a production environment, direct file system access by an AI
    # agent must be heavily restricted and sandboxed to prevent security vulnerabilities.
    # This implementation is for demonstration purposes within a controlled environment.
    
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at '{file_path}'."
        
        if not os.path.isfile(file_path):
            return f"Error: '{file_path}' is not a file."

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Content of '{file_path}':\n---\n{content}\n---"
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"