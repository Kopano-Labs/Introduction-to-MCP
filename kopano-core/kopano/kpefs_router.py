"""KPEFS four-vector routing — plant, animal, homo sapiens, diaspora."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VECTOR_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPEFS_FOUR_VECTOR_DOCTRINE.json"


def load_vectors() -> dict[str, Any]:
    if not VECTOR_PATH.is_file():
        return {"vectors": []}
    return json.loads(VECTOR_PATH.read_text(encoding="utf-8"))


def vector_for_stem_domain(stem_domain: str, department_code: str = "KP") -> str:
    """Static KPEFS vector for a catalog agent from stem_domain + department."""
    doc = load_vectors()
    domain = (stem_domain or "").strip()
    for v in doc.get("vectors", []):
        if domain in v.get("agent_domains", []):
            return v["id"]
    if department_code.upper() == "APE":
        return "V3_HOMO_SAPIENS"
    if domain in ("ICT & Instrumentation", "Information & Communication Technology"):
        return "V2_ANIMAL"
    return "V4_DIASPORA"


def route_vector(message: str) -> dict[str, Any]:
    """Pick dominant KPEFS vector from keywords (V4 diaspora wins ties)."""
    doc = load_vectors()
    text = (message or "").lower()
    scores: dict[str, int] = {}
    for v in doc.get("vectors", []):
        vid = v["id"]
        score = 0
        for kw in v.get("routing_keywords", []):
            if kw.lower() in text:
                score += 1
        scores[vid] = score

    # Diaspora priority on tie (rank 4 — very important in doctrine)
    order = ["V4_DIASPORA", "V1_PLANT", "V2_ANIMAL", "V3_HOMO_SAPIENS"]
    best = max(scores.values()) if scores else 0
    if best == 0:
        active = "V4_DIASPORA"
    else:
        active = next((k for k in order if scores.get(k, 0) == best), "V4_DIASPORA")

    vec = next((v for v in doc.get("vectors", []) if v["id"] == active), {})
    department_hint = "kopano_labs_experimentation"
    if active == "V3_HOMO_SAPIENS" or vec.get("ape_bias"):
        department_hint = "ama_phu_creativity"
    if active == "V4_DIASPORA":
        department_hint = "kopano_labs_experimentation"

    return {
        "active_vector": active,
        "rank": vec.get("rank"),
        "metaphor": vec.get("metaphor"),
        "scores": scores,
        "department_hint": department_hint,
        "bracket_snippet": (
            f"[KPEFS_FOUR_VECTOR] active: {active} | "
            f"v1: PLANT | v2: ANIMAL | v3: HOMO_SAPIENS | v4: DIASPORA"
        ),
    }


def kpefs_status() -> dict[str, Any]:
    from .phu_boot_governance import boot_status

    operating_mesh: dict[str, Any] = {}
    try:
        from .operating_mesh import operating_mesh_status

        operating_mesh = operating_mesh_status()
    except ImportError:
        operating_mesh = {"error": "operating_mesh_unavailable"}

    graduation_bar: dict[str, Any] = {}
    try:
        from .graduation_bar import graduation_bar_status

        graduation_bar = graduation_bar_status()
    except ImportError:
        graduation_bar = {"error": "graduation_bar_unavailable"}

    closure: dict[str, Any] = {}
    try:
        from .external_swarm_lane import kpefs_closure_status

        closure = kpefs_closure_status()
    except ImportError:
        closure = {"error": "closure_unavailable"}

    return {
        "schema": "kpefs_status_v1",
        "system": "KPEFS",
        "vectors": load_vectors(),
        "boot": boot_status().get("mesh_summary"),
        "operating_mesh": operating_mesh,
        "graduation_bar": graduation_bar,
        "closure": closure,
        "linguistics": "docs/swarm-ops/BRACKET_LINGUISTIC_RECREATION.md",
        "blasphemy_register": "docs/swarm-ops/BRACKET_BLASPHEMY_REGISTER.json",
        "implementation_plan": "docs/swarm-ops/KPEFS_IMPLEMENTATION_PLAN.md",
    }
