"""Swarm Console status API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))


@pytest.fixture()
def client() -> TestClient:
    from kopano.api import app

    return TestClient(app)


def test_swarm_console_status(client: TestClient) -> None:
    r = client.get("/api/kc/swarm-console/status")
    assert r.status_code == 200
    body = r.json()
    assert body["schema"] == "kc_swarm_console_status_v1"
    assert "git" in body
    assert body["git"]["branch"]
    assert "checks" in body
    assert "doctrine" in body
    assert body["doctrine"]["verified_production"] >= 10
    assert body["doctrine"]["production_bar_met"] is True
    assert body["cassy"]["lead_student"] == "cassy"
    assert body["cassy"]["teacher"] == "cassey"
    assert "student_primary" in body["cassy"]["role"]
    assert body["ci"]["actions_url"].startswith("https://github.com/")
    agents = body["agents"]
    assert agents["registry_total"] == 13
    assert agents["orch_runnable"] == 7
    assert agents["swarm_slots"] == 4
    assert agents["mesh"] == 4
    assert agents["operator_cf"] == "cf_cloud"
