import subprocess
import sys
import tempfile
from pathlib import Path

def execute_code(code: str) -> str:
    """Executes Python code and returns the result."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(code.encode("utf-8"))
        tmp_path = Path(tmp.name)
    
    try:
        result = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout
        if result.stderr:
            output += "\nError:\n" + result.stderr
        return output or "(No output)"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (10s)."
    except Exception as e:
        return f"Error executing code: {e}"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
