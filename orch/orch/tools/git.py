import subprocess
from pathlib import Path

def _run_git_command(args: list) -> str:
    """Helper to run git commands."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def git_init() -> str:
    """Initializes a new git repository."""
    return _run_git_command(["init"])

def git_add(file_path: str) -> str:
    """Adds a file to the git staging area."""
    res = _run_git_command(["add", file_path])
    if res.startswith("Error:"):
        return res
    return f"Successfully added '{file_path}' to staging."

def git_commit(message: str) -> str:
    """Commits the staged changes."""
    return _run_git_command(["commit", "-m", message])

def git_status() -> str:
    """Returns the current git status."""
    return _run_git_command(["status"])

def git_log() -> str:
    """Returns the git commit log."""
    return _run_git_command(["log"])
