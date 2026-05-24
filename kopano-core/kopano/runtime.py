"""Frozen/desktop runtime paths for KopanoContext.exe."""

from __future__ import annotations

import json
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
    ensure_desktop_admin()
    ensure_desktop_operator()


def _operator_bootstrap_path() -> Path:
    return user_data_dir() / "operator.bootstrap.json"


def ensure_desktop_operator() -> None:
    """Provision Super God operator from env or LocalAppData bootstrap (never committed)."""
    email = os.environ.get("KOPANO_GOD_EMAIL", "").strip().lower()
    password = os.environ.get("KOPANO_GOD_PASSWORD", "")
    bootstrap = _operator_bootstrap_path()
    if bootstrap.is_file():
        try:
            data = json.loads(bootstrap.read_text(encoding="utf-8"))
            email = str(data.get("email", email)).strip().lower()
            password = str(data.get("password", password))
        except (json.JSONDecodeError, OSError, TypeError):
            pass
    if not email or not password:
        return

    from .database import upsert_operator_account
    from .operator_auth import create_session, load_persisted_desktop_session, persist_desktop_session

    user = upsert_operator_account(
        email,
        password,
        full_name=os.environ.get("KOPANO_GOD_NAME", "Kopano Super Operator"),
        god_mode=True,
    )
    existing = load_persisted_desktop_session()
    if existing and str(existing.get("user", {}).get("email", "")).lower() == email:
        return
    token = create_session({**user, "god_mode": True})
    persist_desktop_session(token, {**user, "god_mode": True})


def ensure_desktop_admin() -> None:
    """Bootstrap a local admin account for desktop / frozen installs."""
    from .database import get_db_connection, grant_admin, init_db, register_user

    init_db()
    email = os.environ.get("KOPANO_ADMIN_EMAIL", "admin@kopano.local").strip().lower()
    password = os.environ.get("KOPANO_ADMIN_PASSWORD", "demo-admin")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    has_admin = cursor.fetchone() is not None
    conn.close()
    if has_admin:
        return

    try:
        register_user(email, password, full_name="Kopano Desktop Admin")
    except ValueError:
        pass
    try:
        grant_admin(email)
    except ValueError:
        pass
