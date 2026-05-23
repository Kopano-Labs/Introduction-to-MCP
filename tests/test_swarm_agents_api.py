"""Swarm agents + triad API."""

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


def test_swarm_agents_endpoint(client: TestClient) -> None:
    r = client.get("/api/kc/swarm-agents")
    assert r.status_code == 200
    body = r.json()
    assert body["lead_student"] == "cassy"
    assert any(a["id"] == "cassey" for a in body["agents"])


def test_triad_endpoint(client: TestClient) -> None:
    r = client.get("/api/kc/triad")
    assert r.status_code == 200
    body = r.json()
    assert body["unified"] is True
    assert "grit" in body["triad"]
