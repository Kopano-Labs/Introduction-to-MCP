"""
Filesystem MCP Tool for orch — Production Grade
================================================
Capability #2  (Critical) — Formalise filesystem MCP tool
Unlocks: #1, #5, #6, #8, #9, #12, #18, #19, #36, #39, #40, #41,
         #43, #50, #54, #65, #66, #67, #84, #87, #89 and more.

Replaces: orch/orch/tools/filesystem.py

Key hardening over the original:
  - SANDBOX: all paths are resolved and must stay inside ALLOWED_ROOT
  - PATH TRAVERSAL blocked (../../etc/passwd style attacks)
  - BLOCKED EXTENSIONS: .env, .key, .pem, .p12, .pfx, credentials
  - BLOCKED FILENAMES: .env, secrets, id_rsa, known_hosts, etc.
  - MAX FILE SIZE enforced on reads (default 10 MB)
  - MAX WRITE SIZE enforced (default 5 MB)
  - READ-ONLY MODE flag for safe agent contexts
  - AUDIT LOG: every operation logged with timestamp + outcome
  - Full MCP tool definitions + dispatcher included
  - CLI quick-test included

Environment variables (.env):
  FS_ALLOWED_ROOT=.          # sandbox root (default: project dir)
  FS_READ_ONLY=false         # set true to block all writes/deletes
  FS_MAX_READ_MB=10          # max file size to read (MB)
  FS_MAX_WRITE_MB=5          # max file size to write (MB)
  FS_AUDIT_LOG=.orch_data/fs_audit.log  # audit log path
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _root() -> Path:
    """Resolved sandbox root. All operations must stay inside this."""
    raw = _env("FS_ALLOWED_ROOT", ".")
    return Path(raw).resolve()


def _read_only() -> bool:
    return _env("FS_READ_ONLY", "false").lower() in ("true", "1", "yes")


def _max_read_bytes() -> int:
    return int(_env("FS_MAX_READ_MB", "10")) * 1024 * 1024


def _max_write_bytes() -> int:
    return int(_env("FS_MAX_WRITE_MB", "5")) * 1024 * 1024


def _audit_log_path() -> Path:
    return Path(_env("FS_AUDIT_LOG", ".orch_data/fs_audit.log"))


# ---------------------------------------------------------------------------
# Blocked patterns
# ---------------------------------------------------------------------------

BLOCKED_EXTENSIONS = {
    ".env", ".key", ".pem", ".p12", ".pfx", ".ppk",
    ".jks", ".keystore", ".cer", ".crt", ".der",
}

BLOCKED_NAMES = {
    ".env", ".env.local", ".env.production", ".env.staging",
    "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa",
    "known_hosts", "authorized_keys",
    "secrets", "credentials", "passwd", "shadow",
    "*.pem", "*.key",
}

BLOCKED_DIRS = {
    ".git", ".ssh", ".gnupg", ".aws", ".azure",
    "__pycache__", ".venv", "venv", "node_modules",
}


# ---------------------------------------------------------------------------
# Sandbox enforcement
# ---------------------------------------------------------------------------

class SandboxViolation(Exception):
    """Raised when a path escapes the allowed root."""


class BlockedFileError(Exception):
    """Raised when a sensitive file is accessed."""


class ReadOnlyError(Exception):
    """Raised when a write is attempted in read-only mode."""


class FileSizeError(Exception):
    """Raised when a file exceeds size limits."""


def _resolve(path_str: str) -> Path:
    """
    Resolve a path and verify it stays inside the sandbox root.
    Raises SandboxViolation if it escapes.
    """
    root = _root()
    # Resolve relative to root so agents can use relative paths naturally
    candidate = (root / path_str).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise SandboxViolation(
            f"Path '{path_str}' escapes the allowed root '{root}'. "
            f"All file operations must stay inside: {root}"
        )
    return candidate


def _check_blocked(path: Path) -> None:
    """Raise BlockedFileError if the path matches any blocked pattern."""
    name = path.name.lower()
    ext  = path.suffix.lower()

    if ext in BLOCKED_EXTENSIONS:
        raise BlockedFileError(
            f"Access to '{path.name}' is blocked (extension: {ext}). "
            "Sensitive file types cannot be read or written by the filesystem tool."
        )

    if name in {b.lower() for b in BLOCKED_NAMES}:
        raise BlockedFileError(
            f"Access to '{path.name}' is blocked (sensitive filename). "
            "Use environment variables or a secrets manager instead."
        )

    # Block if any parent directory is in BLOCKED_DIRS
    for part in path.parts:
        if part.lower() in {b.lower() for b in BLOCKED_DIRS}:
            raise BlockedFileError(
                f"Access inside '{part}/' is blocked for security reasons."
            )


def _check_writable() -> None:
    if _read_only():
        raise ReadOnlyError(
            "Filesystem tool is in READ-ONLY mode (FS_READ_ONLY=true). "
            "No writes or deletes are permitted."
        )


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------

def _audit(operation: str, path: str, outcome: str, detail: str = "") -> None:
    """Append one line to the audit log."""
    try:
        log_path = _audit_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        ts    = datetime.now(timezone.utc).isoformat(timespec="seconds")
        entry = json.dumps({
            "ts": ts, "op": operation,
            "path": path, "outcome": outcome, "detail": detail
        })
        with log_path.open("a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass  # Never let logging break the actual operation


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read a file inside the sandbox.

    Args:
        file_path: Path to file (relative to sandbox root or absolute within it).
        encoding:  Text encoding (default utf-8). Use 'binary' for base64 output.

    Returns:
        File contents as string, or an error message prefixed with 'Error:'.
    """
    try:
        path = _resolve(file_path)
        _check_blocked(path)

        if not path.exists():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        if path.is_dir():
            raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")

        size = path.stat().st_size
        max_bytes = _max_read_bytes()
        if size > max_bytes:
            raise FileSizeError(
                f"File '{file_path}' is {size / 1024 / 1024:.1f} MB, "
                f"exceeding the {max_bytes // 1024 // 1024} MB read limit. "
                "Increase FS_MAX_READ_MB to allow larger reads."
            )

        if encoding == "binary":
            import base64
            content = base64.b64encode(path.read_bytes()).decode("ascii")
            _audit("read_binary", file_path, "ok", f"{size} bytes")
            return content

        content = path.read_text(encoding=encoding)
        _audit("read", file_path, "ok", f"{size} bytes")
        return content

    except (SandboxViolation, BlockedFileError, FileSizeError) as e:
        _audit("read", file_path, "blocked", str(e))
        return f"Error: {e}"
    except FileNotFoundError as e:
        _audit("read", file_path, "not_found", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("read", file_path, "error", str(e))
        return f"Error reading '{file_path}': {e}"


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Write content to a file inside the sandbox.

    Args:
        file_path: Destination path (relative to sandbox root).
        content:   Text content to write.
        encoding:  Text encoding (default utf-8).

    Returns:
        Success message or error string prefixed with 'Error:'.
    """
    try:
        _check_writable()
        path = _resolve(file_path)
        _check_blocked(path)

        size = len(content.encode(encoding))
        max_bytes = _max_write_bytes()
        if size > max_bytes:
            raise FileSizeError(
                f"Content is {size / 1024 / 1024:.1f} MB, "
                f"exceeding the {max_bytes // 1024 // 1024} MB write limit. "
                "Increase FS_MAX_WRITE_MB to allow larger writes."
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        _audit("write", file_path, "ok", f"{size} bytes")
        return f"Successfully wrote {size:,} bytes to '{file_path}'."

    except (SandboxViolation, BlockedFileError, ReadOnlyError, FileSizeError) as e:
        _audit("write", file_path, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("write", file_path, "error", str(e))
        return f"Error writing to '{file_path}': {e}"


def append_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Append content to an existing file (or create it).

    Args:
        file_path: Destination path.
        content:   Text to append.
    """
    try:
        _check_writable()
        path = _resolve(file_path)
        _check_blocked(path)

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding=encoding) as f:
            f.write(content)
        size = len(content.encode(encoding))
        _audit("append", file_path, "ok", f"+{size} bytes")
        return f"Successfully appended {size:,} bytes to '{file_path}'."

    except (SandboxViolation, BlockedFileError, ReadOnlyError) as e:
        _audit("append", file_path, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("append", file_path, "error", str(e))
        return f"Error appending to '{file_path}': {e}"


def list_directory(
    directory_path: str = ".",
    show_hidden: bool = False,
    recursive: bool = False,
    max_depth: int = 3,
) -> str:
    """
    List directory contents inside the sandbox.

    Args:
        directory_path: Path to list (default: sandbox root).
        show_hidden:    Include hidden files/dirs (default False).
        recursive:      Recurse into subdirectories (default False).
        max_depth:      Max recursion depth when recursive=True (default 3).

    Returns:
        Formatted directory listing or error string.
    """
    try:
        path = _resolve(directory_path)
        _check_blocked(path)

        if not path.exists():
            return f"Error: Directory '{directory_path}' does not exist."
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory."

        lines: list[str] = [f"📁 {path} (sandbox root: {_root()})"]

        def _list(p: Path, prefix: str, depth: int) -> None:
            if depth > max_depth:
                lines.append(f"{prefix}... (max depth {max_depth} reached)")
                return
            try:
                entries = sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
            except PermissionError:
                lines.append(f"{prefix}[permission denied]")
                return
            for entry in entries:
                if not show_hidden and entry.name.startswith("."):
                    continue
                if entry.name.lower() in {b.lower() for b in BLOCKED_DIRS} and entry.is_dir():
                    lines.append(f"{prefix}🔒 {entry.name}/ [blocked]")
                    continue
                if entry.is_dir():
                    lines.append(f"{prefix}📁 {entry.name}/")
                    if recursive:
                        _list(entry, prefix + "  ", depth + 1)
                else:
                    size = entry.stat().st_size
                    size_str = _human_size(size)
                    lines.append(f"{prefix}📄 {entry.name} ({size_str})")

        _list(path, "  ", 1)
        _audit("list", directory_path, "ok", f"{len(lines)} entries")
        return "\n".join(lines)

    except (SandboxViolation, BlockedFileError) as e:
        _audit("list", directory_path, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("list", directory_path, "error", str(e))
        return f"Error listing '{directory_path}': {e}"


def delete_file(file_path: str) -> str:
    """
    Delete a file inside the sandbox.

    Args:
        file_path: Path to the file to delete.

    Returns:
        Success message or error string.
    """
    try:
        _check_writable()
        path = _resolve(file_path)
        _check_blocked(path)

        if not path.exists():
            return f"Error: '{file_path}' does not exist."
        if path.is_dir():
            return f"Error: '{file_path}' is a directory. Use delete_directory instead."

        path.unlink()
        _audit("delete", file_path, "ok")
        return f"Successfully deleted '{file_path}'."

    except (SandboxViolation, BlockedFileError, ReadOnlyError) as e:
        _audit("delete", file_path, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("delete", file_path, "error", str(e))
        return f"Error deleting '{file_path}': {e}"


def move_file(source: str, destination: str) -> str:
    """
    Move or rename a file inside the sandbox.

    Args:
        source:      Current path.
        destination: New path.
    """
    try:
        _check_writable()
        src  = _resolve(source)
        dest = _resolve(destination)
        _check_blocked(src)
        _check_blocked(dest)

        if not src.exists():
            return f"Error: Source '{source}' does not exist."

        dest.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dest)
        _audit("move", source, "ok", f"-> {destination}")
        return f"Successfully moved '{source}' to '{destination}'."

    except (SandboxViolation, BlockedFileError, ReadOnlyError) as e:
        _audit("move", source, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("move", source, "error", str(e))
        return f"Error moving '{source}': {e}"


def file_info(file_path: str) -> str:
    """
    Return metadata about a file without reading its contents.

    Args:
        file_path: Path to inspect.

    Returns:
        JSON string with size, modified time, mime type, etc.
    """
    try:
        path = _resolve(file_path)
        _check_blocked(path)

        if not path.exists():
            return f"Error: '{file_path}' does not exist."

        stat = path.stat()
        mime, _ = mimetypes.guess_type(str(path))
        info = {
            "path":          str(path),
            "name":          path.name,
            "extension":     path.suffix,
            "size_bytes":    stat.st_size,
            "size_human":    _human_size(stat.st_size),
            "is_file":       path.is_file(),
            "is_dir":        path.is_dir(),
            "mime_type":     mime or "unknown",
            "modified_utc":  datetime.fromtimestamp(
                                 stat.st_mtime, tz=timezone.utc
                             ).isoformat(),
            "created_utc":   datetime.fromtimestamp(
                                 stat.st_ctime, tz=timezone.utc
                             ).isoformat(),
        }
        _audit("info", file_path, "ok")
        return json.dumps(info, indent=2)

    except (SandboxViolation, BlockedFileError) as e:
        _audit("info", file_path, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("info", file_path, "error", str(e))
        return f"Error getting info for '{file_path}': {e}"


def search_files(
    pattern: str,
    directory: str = ".",
    content_search: str = "",
    max_results: int = 50,
) -> str:
    """
    Search for files by name pattern and optionally by content.

    Args:
        pattern:        Glob pattern e.g. '*.py', '**/*.md'
        directory:      Directory to search in (default: sandbox root).
        content_search: If set, only return files containing this string.
        max_results:    Cap results (default 50).

    Returns:
        Newline-separated list of matching file paths.
    """
    try:
        base = _resolve(directory)
        if not base.is_dir():
            return f"Error: '{directory}' is not a directory."

        matches: list[str] = []
        for path in base.glob(pattern):
            if len(matches) >= max_results:
                break
            try:
                _check_blocked(path)
            except BlockedFileError:
                continue

            if path.is_dir():
                continue

            if content_search:
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    if content_search.lower() not in text.lower():
                        continue
                except Exception:
                    continue

            rel = path.relative_to(_root())
            matches.append(str(rel))

        _audit("search", directory, "ok", f"{len(matches)} results for '{pattern}'")
        if not matches:
            return f"No files found matching '{pattern}' in '{directory}'."
        return "\n".join(matches)

    except (SandboxViolation, BlockedFileError) as e:
        _audit("search", directory, "blocked", str(e))
        return f"Error: {e}"
    except Exception as e:
        _audit("search", directory, "error", str(e))
        return f"Error searching '{directory}': {e}"


def read_audit_log(last_n: int = 50) -> str:
    """Return the last N entries from the audit log."""
    try:
        log_path = _audit_log_path()
        if not log_path.exists():
            return "Audit log is empty (no operations recorded yet)."
        lines = log_path.read_text(encoding="utf-8").splitlines()
        recent = lines[-last_n:]
        return "\n".join(recent)
    except Exception as e:
        return f"Error reading audit log: {e}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _human_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size //= 1024
    return f"{size:.0f} TB"


# ---------------------------------------------------------------------------
# MCP Tool Registration
# ---------------------------------------------------------------------------

def get_mcp_tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "fs_read_file",
            "description": "Read a file from the sandboxed filesystem. Blocks access to sensitive files (.env, keys, certs).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file (relative to project root)"},
                    "encoding":  {"type": "string", "description": "Encoding (default: utf-8). Use 'binary' for base64.", "default": "utf-8"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "fs_write_file",
            "description": "Write content to a file. Creates parent directories automatically. Blocked in read-only mode.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Destination path"},
                    "content":   {"type": "string", "description": "Text content to write"},
                },
                "required": ["file_path", "content"],
            },
        },
        {
            "name": "fs_append_file",
            "description": "Append text to a file (creates it if it doesn't exist).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Destination path"},
                    "content":   {"type": "string", "description": "Text to append"},
                },
                "required": ["file_path", "content"],
            },
        },
        {
            "name": "fs_list_directory",
            "description": "List directory contents. Hidden files and sensitive dirs are filtered by default.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Directory to list (default: project root)", "default": "."},
                    "show_hidden":    {"type": "boolean", "description": "Show hidden files", "default": False},
                    "recursive":      {"type": "boolean", "description": "Recurse into subdirectories", "default": False},
                    "max_depth":      {"type": "integer", "description": "Max recursion depth", "default": 3},
                },
                "required": [],
            },
        },
        {
            "name": "fs_delete_file",
            "description": "Delete a file. Blocked in read-only mode.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to delete"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "fs_move_file",
            "description": "Move or rename a file within the sandbox.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "source":      {"type": "string", "description": "Current path"},
                    "destination": {"type": "string", "description": "New path"},
                },
                "required": ["source", "destination"],
            },
        },
        {
            "name": "fs_file_info",
            "description": "Get metadata about a file (size, type, dates) without reading its content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to inspect"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "fs_search_files",
            "description": "Search for files by glob pattern, optionally filtering by content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern":        {"type": "string", "description": "Glob pattern e.g. '*.py', '**/*.md'"},
                    "directory":      {"type": "string", "description": "Directory to search (default: root)", "default": "."},
                    "content_search": {"type": "string", "description": "Only return files containing this string"},
                    "max_results":    {"type": "integer", "description": "Max results to return", "default": 50},
                },
                "required": ["pattern"],
            },
        },
        {
            "name": "fs_audit_log",
            "description": "Read the filesystem audit log showing recent tool operations.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "last_n": {"type": "integer", "description": "Number of recent entries to return", "default": 50},
                },
                "required": [],
            },
        },
    ]


def dispatch_mcp_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Route an MCP tool call to the correct function."""
    dispatch = {
        "fs_read_file":      lambda i: read_file(**i),
        "fs_write_file":     lambda i: write_file(**i),
        "fs_append_file":    lambda i: append_file(**i),
        "fs_list_directory": lambda i: list_directory(**i),
        "fs_delete_file":    lambda i: delete_file(**i),
        "fs_move_file":      lambda i: move_file(**i),
        "fs_file_info":      lambda i: file_info(**i),
        "fs_search_files":   lambda i: search_files(**i),
        "fs_audit_log":      lambda i: read_audit_log(**i),
    }
    if tool_name not in dispatch:
        raise ValueError(f"Unknown filesystem tool: {tool_name}")
    return dispatch[tool_name](tool_input)


# ---------------------------------------------------------------------------
# CLI quick-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Sandbox root : {_root()}")
    print(f"Read-only    : {_read_only()}")
    print(f"Max read     : {_max_read_bytes() // 1024 // 1024} MB")
    print(f"Max write    : {_max_write_bytes() // 1024 // 1024} MB")
    print()

    # 1. List root
    print("=== Directory listing ===")
    print(list_directory("."))
    print()

    # 2. Write test file
    print("=== Write test ===")
    print(write_file("orch_test_output.txt", "Hello from kopano filesystem tool!\n"))

    # 3. Read it back
    print("=== Read test ===")
    print(read_file("orch_test_output.txt"))

    # 4. File info
    print("=== File info ===")
    print(file_info("orch_test_output.txt"))

    # 5. Search
    print("=== Search *.py ===")
    print(search_files("*.py", max_results=5))

    # 6. Sandbox violation test
    print("=== Sandbox violation test ===")
    print(read_file("../../etc/passwd"))

    # 7. Blocked file test
    print("=== Blocked file test ===")
    print(read_file(".env"))

    # 8. Cleanup
    print("=== Cleanup ===")
    print(delete_file("orch_test_output.txt"))

    # 9. Audit log
    print("=== Audit log (last 10) ===")
    print(read_audit_log(10))
