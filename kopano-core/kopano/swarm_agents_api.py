"""Swarm agent registry + Servitude Triad (unified modes)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY = _REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
_ROADMAP = _REPO_ROOT / "docs" / "swarm-ops" / "MAIN_BRAIN_ROADMAP.json"
_PROFILE = _REPO_ROOT / "kopano-core" / ".kc" / "swarm_profile.json"

router = APIRouter(prefix="/api/kc", tags=["kc-swarm"])


@router.get("/swarm-agents")
def get_swarm_agents() -> dict:
    if not _REGISTRY.is_file():
        raise HTTPException(status_code=404, detail="SWARM_AGENTS.json missing")
    return json.loads(_REGISTRY.read_text(encoding="utf-8"))


@router.get("/triad")
def get_triad() -> dict:
    if not _ROADMAP.is_file():
        raise HTTPException(status_code=404, detail="MAIN_BRAIN_ROADMAP.json missing")
    roadmap = json.loads(_ROADMAP.read_text(encoding="utf-8"))
    profile = {}
    if _PROFILE.is_file():
        profile = json.loads(_PROFILE.read_text(encoding="utf-8"))
    return {
        "triad": roadmap.get("triad"),
        "servitude": roadmap.get("servitude"),
        "unified": True,
        "lead_student": profile.get("lead_student") or roadmap.get("cassy", {}).get("lead_student"),
        "teacher": profile.get("teacher") or roadmap.get("cassy", {}).get("teacher"),
        "brain": profile.get("brain") or roadmap.get("cassy", {}).get("brain"),
        "roadmap_milestones": [m["id"] for m in roadmap.get("milestones", [])],
        "docs": {
            "servitude_triad": "docs/swarm-ops/SERVITUDE_TRIAD.md",
            "roadmap": "docs/swarm-ops/MAIN_BRAIN_ROADMAP.json",
            "black_mass": "docs/swarm-ops/BLACK_MASS_PROTOCOL.md",
        },
    }
