from pathlib import Path


def _allowed_root() -> Path:
    return Path.cwd().resolve()


def _resolve_under_root(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    root = _allowed_root()
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("Path escapes allowed workspace root.")
    return resolved


def read_file(path: str) -> str:
    target = _resolve_under_root(path)
    return target.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    target = _resolve_under_root(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Wrote {path}"
