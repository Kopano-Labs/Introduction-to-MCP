"""Super God / Cassy-forward KC god API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano import operator_auth  # noqa: E402
from kopano.api import app  # noqa: E402


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def god_headers(tmp_path, monkeypatch):
    import kopano.database as database

    db_file = tmp_path / "datalake.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    monkeypatch.setenv("KOPANO_GOD_EMAIL", "god@test.local")
    monkeypatch.setenv("KOPANO_GOD_PASSWORD", "god-test-pass")

    from kopano.database import init_db
    from kopano.runtime import ensure_desktop_operator

    init_db()
    ensure_desktop_operator()

    token = operator_auth.create_session(
        {
            "id": 1,
            "email": "god@test.local",
            "role": "admin",
            "god_mode": True,
            "is_active": True,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def test_god_capabilities_public(client):
    res = client.get("/api/kc/god/capabilities")
    assert res.status_code == 200
    body = res.json()
    assert "script_actions" in body
    assert "cassy_activate_seed" in body["script_actions"]


def test_god_me_requires_bearer(client):
    assert client.get("/api/kc/god/me").status_code == 401


def test_god_me_cassy_forward(client, god_headers):
    res = client.get("/api/kc/god/me", headers=god_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["super_god_mode"] is True
    assert body["lead_student"] == "cassy"
    assert body["teacher"] == "cassey"
    assert body["brain"] == "kc"


def test_god_overview_includes_cassy(client, god_headers):
    res = client.get("/api/kc/god/overview", headers=god_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["schema"] == "kc_god_overview_v1"
    assert "cassy" in body
    assert "swarm_console" in body


def test_god_desktop_session_localhost_only(client):
    res = client.get("/api/kc/god/desktop-session")
    assert res.status_code in {403, 404}
