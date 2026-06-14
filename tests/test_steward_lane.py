"""Steward lane — KC Save|Watch + Cassy execute orchestration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.steward_lane import (  # noqa: E402
    activate_cassy_profile,
    steward_lane_status,
)


def test_activate_cassy_profile_writes_registry_fields():
    profile = activate_cassy_profile()
    assert profile.get("lead_student") == "cassy"
    assert profile.get("brain") == "kc"
    assert profile.get("teacher") == "cassey"
    path = REPO / "kopano-core" / ".kc" / "swarm_profile.json"
    assert path.is_file()
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk.get("lead_student") == "cassy"


def test_steward_lane_status_schema():
    status = steward_lane_status()
    assert status.get("schema") == "steward_lane_status_v1"
    assert "kc_mode" in status
    assert status.get("lead_student") == "cassy"
