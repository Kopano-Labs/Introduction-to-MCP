"""Kopano-Phu ecosystem + Bracket Protocol."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.api import app  # noqa: E402
from kopano.phu_ecosystem import (  # noqa: E402
    load_ecosystem_config,
    merge_sub_brain_rows,
    reattach_detached_subbrains,
    schematics_root,
)


def test_schematics_root_exists():
    root = schematics_root()
    assert root.is_dir()
    assert (root / "04-Updates").is_dir()


def test_ecosystem_config_lists_sub_brains():
    cfg = load_ecosystem_config()
    assert len(cfg.get("sub_brains", [])) >= 9
    assert cfg.get("breaking_point_protocol") == "Bracket Protocol"


def test_merge_sub_brain_rows_have_attachment():
    rows = merge_sub_brain_rows()
    assert rows
    assert all("attachment" in r for r in rows)


def test_reattach_dry_run():
    result = reattach_detached_subbrains(dry_run=True)
    assert result["schema"] == "phu_reattach_v1"
    assert result["dry_run"] is True


@pytest.fixture()
def client():
    return TestClient(app)


def test_phu_ecosystem_endpoint(client):
    res = client.get("/api/kc/phu/ecosystem")
    assert res.status_code == 200
    body = res.json()
    assert body["schema"] == "kopano_phu_ecosystem_status_v1"
    assert body["bracket_protocol"]["name"] == "Bracket Protocol"
    assert body["cassy_legacy"]["lead_student"] == "cassy"


def test_bracket_protocol_endpoint(client):
    res = client.get("/api/kc/phu/bracket-protocol")
    assert res.status_code == 200
    assert res.json()["tagline"] == "The Breaking Point"
