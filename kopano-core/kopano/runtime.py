"""Frozen/desktop runtime paths for KopanoContext.exe."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def is_frozen_runtime() -> bool:
    return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))


def bundle_root() -> Path | None:
    if is_frozen_runtime():
        return Path(sys._MEIPASS)
    return None


def executable_dir() -> Path:
    if is_frozen_runtime():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def user_data_dir() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    path = base / "KopanoContext"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_db_path() -> Path:
    return user_data_dir() / "datalake.db"


def _seed_database(db_path: Path) -> None:
    if db_path.exists():
        return
    candidates: list[Path] = []
    bundle = bundle_root()
    if bundle is not None:
        candidates.append(bundle / "db" / "datalake.db")
    candidates.append(executable_dir() / "db" / "datalake.db")
    repo_db = Path(__file__).resolve().parents[2].parent / "db" / "datalake.db"
    candidates.append(repo_db)
    for template in candidates:
        if template.is_file():
            db_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, db_path)
            return


def configure_frozen_runtime() -> None:
    """Call before importing kopano modules that load Settings / DB_PATH."""
    if not is_frozen_runtime():
        return
    exe_dir = executable_dir()
    os.chdir(exe_dir)
    db_path = default_db_path()
    os.environ.setdefault("KOPANO_DB_PATH", str(db_path))
    _seed_database(db_path)
    logs = user_data_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
