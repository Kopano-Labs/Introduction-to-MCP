"""Desktop runtime helpers (non-frozen)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.runtime import configure_frozen_runtime, default_db_path, ensure_desktop_admin, is_frozen_runtime  # noqa: E402


def test_not_frozen_by_default():
    assert is_frozen_runtime() is False
    configure_frozen_runtime()  # no-op when not frozen


def test_default_db_path_under_localappdata():
    path = default_db_path()
    assert path.name == "datalake.db"
    assert path.parent.name == "KopanoContext"


def test_ensure_desktop_admin_creates_admin(tmp_path, monkeypatch):
    import kopano.database as database

    db_file = tmp_path / "datalake.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    monkeypatch.setenv("KOPANO_ADMIN_EMAIL", "admin@kopano.local")
    monkeypatch.setenv("KOPANO_ADMIN_PASSWORD", "demo-admin")

    ensure_desktop_admin()

    from kopano.database import get_db_connection

    conn = get_db_connection()
    row = conn.execute(
        "SELECT email, role FROM users WHERE email = ?",
        ("admin@kopano.local",),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["role"] == "admin"
