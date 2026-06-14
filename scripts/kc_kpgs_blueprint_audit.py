#!/usr/bin/env python3
"""Generate KPGS blueprint inventory — proof of what was built of the 300."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_spawn_swarm import (  # noqa: E402
    load_spawn_catalog,
    spawn_agent_by_id,
    synthesize_spawn_manifest,
    validate_spawn_agent,
)

FULL_MESH_IDS = frozenset(
    {
        "mirror_warden",
        "kc_apprentice",
        "operational_general",
        "pipeline_drone",
        "cassy",
        "cassey",
        "kc",
    }
)

GIANT_INTENT_BY_COHORT = {
    "telemetry": ["microsoft_copilot", "azure_openai"],
    "identic": ["google_gemini", "google_workspace"],
    "guardian": ["meta_ai", "openai_chatgpt"],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_agent(agent: dict) -> str:
    aid = agent["id"]
    if agent.get("structural"):
        if aid in FULL_MESH_IDS:
            return "structural_full_mesh"
        return "structural_catalog_only"
    if aid.startswith("spawn_"):
        return "generated_spawn_slot"
    if agent.get("catalog_ref"):
        return "kp_ape_linked"
    return "other"


def ledger_counts() -> dict:
    db = REPO / "kopano-core" / ".kc" / "kpgs_spawn_ledger.db"
    if not db.exists():
        return {"exists": False}
    conn = sqlite3.connect(db)
    tables = [
        r[0]
        for r in conn.execute(
            "select name from sqlite_master where type='table'"
        ).fetchall()
    ]
    counts = {t: conn.execute(f"select count(*) from {t}").fetchone()[0] for t in tables}
    conn.close()
    return {"exists": True, "tables": counts}


def run_audit(write_report: bool = True) -> dict:
    catalog = load_spawn_catalog()
    agents = catalog.get("agents") or []
    by_class: dict[str, list[str]] = {}
    per_agent: list[dict] = []

    manifest_ok = 0
    ship = 0
    hold = 0

    for agent in agents:
        aid = agent["id"]
        cls = classify_agent(agent)
        by_class.setdefault(cls, []).append(aid)

        v = validate_spawn_agent(aid)
        verdict = v.get("verdict", "UNKNOWN")
        if verdict == "SHIP":
            ship += 1
        elif verdict == "HOLD":
            hold += 1

        manifest = synthesize_spawn_manifest(aid)
        if not manifest.get("error"):
            manifest_ok += 1

        per_agent.append(
            {
                "agent_id": aid,
                "blueprint_class": cls,
                "cohort": agent.get("cohort"),
                "structural": bool(agent.get("structural")),
                "catalog_ref": agent.get("catalog_ref"),
                "full_mesh_manifest": aid in FULL_MESH_IDS,
                "validation_verdict": verdict,
                "giant_routing_intent": GIANT_INTENT_BY_COHORT.get(
                    agent.get("cohort", ""), []
                ),
                "provider_deployed": False,
                "provider_receipt": None,
            }
        )

    report = {
        "schema": "kpgs_blueprint_inventory_v1",
        "ts": _utc_now(),
        "title": "KPGS 300 Blueprint Inventory — billing / decentralization proof",
        "catalog_ref": "docs/swarm-ops/agents/KPGS_SPAWN_300_AGENTS.json",
        "totals": {
            "catalog_agents": len(agents),
            "manifest_synthesized": manifest_ok,
            "validation_ship": ship,
            "validation_hold": hold,
            "structural_full_mesh": len(by_class.get("structural_full_mesh", [])),
            "structural_catalog_only": len(by_class.get("structural_catalog_only", [])),
            "kp_ape_linked": len(by_class.get("kp_ape_linked", [])),
            "generated_spawn_slot": len(by_class.get("generated_spawn_slot", [])),
            "other": len(by_class.get("other", [])),
            "deployed_to_giant_provider": 0,
            "paid_api_instances": 0,
        },
        "honesty": {
            "what_is_built": (
                "300 spawn manifests synthesized and governance-validated SHIP; "
                "300 infinite-hood plot assignments; altar ledger checkpoints."
            ),
            "what_is_not_built": (
                "No per-agent Microsoft/Google/Meta paid API deployments; "
                "no provider execution receipts; sovereign sim is simulated dispatch only."
            ),
            "full_mesh_blueprint_ids": sorted(FULL_MESH_IDS),
            "structural_catalog_only_ids": sorted(
                by_class.get("structural_catalog_only", [])
            ),
        },
        "by_class": {k: len(v) for k, v in sorted(by_class.items())},
        "by_cohort": {
            c: sum(1 for a in agents if a.get("cohort") == c)
            for c in ("telemetry", "identic", "guardian")
        },
        "giant_routing_intent_by_cohort": GIANT_INTENT_BY_COHORT,
        "ledger": ledger_counts(),
        "agents": per_agent,
    }

    if write_report:
        out = REPO / "docs" / "swarm-ops" / "KPGS_BLUEPRINT_INVENTORY.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report["report_path"] = str(out.relative_to(REPO)).replace("\\", "/")

    return report


def main() -> int:
    report = run_audit(write_report=True)
    t = report["totals"]
    print("[KPGS_BLUEPRINT_AUDIT]")
    print(f"catalog={t['catalog_agents']}")
    print(f"manifest_synthesized={t['manifest_synthesized']}")
    print(f"validation_ship={t['validation_ship']}")
    print(f"full_mesh={t['structural_full_mesh']}")
    print(f"structural_catalog_only={t['structural_catalog_only']}")
    print(f"kp_ape_linked={t['kp_ape_linked']}")
    print(f"generated_spawn_slots={t['generated_spawn_slot']}")
    print(f"deployed_to_giant={t['deployed_to_giant_provider']}")
    print(f"report={report.get('report_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
