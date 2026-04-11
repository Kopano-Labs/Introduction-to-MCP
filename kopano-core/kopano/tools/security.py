import subprocess
import sys
import shutil
from pathlib import Path

def scan_code_security(target_path: str) -> str:
    """Scans Python code for security issues using Bandit."""
    if not shutil.which("bandit"):
        # Fallback if bandit is not in PATH
        # We can try to run it via sys.executable -m bandit
        pass

    try:
        # Run bandit: -r (recursive), -q (quiet)
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", target_path, "-f", "txt"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Bandit returns 0 if no issues, 1 if issues found
        if result.returncode == 0:
            return f"No security issues found in '{target_path}'."
        elif result.returncode == 1:
             # Issues found
             output = result.stdout.strip()
             if not output and result.stderr:
                 output = result.stderr.strip()
             return f"Security issues found in '{target_path}':\n{output}"
        else:
            return f"Error running security scan: {result.stderr.strip()}"
    except Exception as e:
        # Try to provide a more helpful error if bandit is missing
        if "No module named bandit" in str(e) or "No such file or directory" in str(e):
             return "Error: Bandit is not installed. Please install it with 'pip install bandit'."
        return f"Error: {str(e)}"

def scan_dependencies(requirements_file: str = "requirements.txt") -> str:
    """Scans project dependencies for known vulnerabilities using Safety."""
    path = Path(requirements_file)
    if not path.exists():
        return f"Error: Requirements file '{requirements_file}' not found."

    try:
        # Run safety: check -r <file>
        # Note: safety might require an API key for full functionality, but basic check should work
        result = subprocess.run(
            [sys.executable, "-m", "safety", "check", "-r", requirements_file],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Safety returns 0 if no vulnerabilities, or non-zero if found
        if result.returncode == 0:
            return f"No dependency vulnerabilities found in '{requirements_file}'."
        else:
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return f"Dependency vulnerabilities found in '{requirements_file}':\n{output}"
    except Exception as e:
        if "No module named safety" in str(e) or "No such file or directory" in str(e):
            return "Error: Safety is not installed. Please install it with 'pip install safety'."
        return f"Error: {str(e)}"
