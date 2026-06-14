#!/usr/bin/env python3
"""
Generate KPGS 300-Agent Spawn Swarm — sharded cohort intelligence.

100 Telemetry (sense) | 100 Identic (reason) | 100 Guardian (govern).
Doctrine is sharded per cohort — not 300× full 15 CMD + 5 pillars locally.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "swarm-ops" / "agents" / "KPGS_SPAWN_300_AGENTS.json"
KP_APE = REPO / "docs" / "swarm-ops" / "agents" / "KP_APE_200_AGENTS.json"

FORENSIC_LENSES = ["V_FS_MUKASHIMA", "V_FS_ZUMA", "V_FS_EPSTEIN"]

GUARDIAN_STRUCTURAL = [
    ("mirror_warden", "Mirror Warden", "orchestrator_parity"),
    ("operational_general", "Operational General (Teacher)", "teacher_swarm"),
    ("cassey", "Cassey (Teacher)", "teacher"),
    ("kc", "KC Brain Ledger", "brain"),
]

IDENTIC_STRUCTURAL = [
    ("kc_apprentice", "KC Apprentice (Student)", "student_audit"),
    ("cassy", "Cassy (Lead Student)", "student_primary"),
    ("identi_cursor", "Identi Cursor", "identi_implementation"),
    ("cf_cloud", "CF Cloud Operator", "lpm_operator"),
]

TELEMETRY_STRUCTURAL = [
    ("pipeline_drone", "3D Pipeline Drone", "mesh_worker"),
]


def _kpgs_shard(cohort: str) -> dict:
    base = {
        "cohort": cohort,
        "brief_renters_on_entry": True,
        "swfus_required": True,
        "sharded_doctrine": True,
    }
    if cohort == "telemetry":
        return {
            **base,
            "holds_pillar_blocks": True,
            "doctrine_shard": "telemetry_sense",
            "five_pillars_shard": ["ground_awareness", "eidetic_persistence"],
            "commandments_shard": "ingest_classify_only",
            "ledger_commit_authority": False,
            "capabilities": ["raw_input", "ground_aware_map", "telemetry_dump"],
        }
    if cohort == "identic":
        return {
            **base,
            "holds_pillar_blocks": True,
            "doctrine_shard": "identic_reason",
            "five_pillars_shard": ["hierarchical_triage", "zero_trust_isolation"],
            "commandments_shard": "interpret_jethro_wwjd",
            "ledger_commit_authority": False,
            "capabilities": ["jethro_triage", "forensic_sociology", "wwjd_firewall", "lpm_dialectic"],
        }
    # guardian
    return {
        **base,
        "holds_pillar_blocks": True,
        "doctrine_shard": "guardian_govern",
        "five_pillars_shard": "all",
        "fifteen_commandments": True,
        "five_pillars": True,
        "commandments_shard": "full_altar",
        "ledger_commit_authority": True,
        "capabilities": ["righteous_severance", "altar_hash_commit", "swfus_enforce"],
    }


def _spawn_agent(
    *,
    spawn_slot: str,
    agent_id: str,
    display_name: str,
    cohort: str,
    n: int,
    functionality: str = "",
    stem_domain: str = "",
    catalog_ref: str | None = None,
    structural: bool = False,
) -> dict:
    altar_layer = {
        "telemetry": "telemetry_ai",
        "identic": "identic_ai",
        "guardian": "guardian_ai",
    }[cohort]
    lens = FORENSIC_LENSES[n % len(FORENSIC_LENSES)] if cohort == "identic" else None
    jethro = "J10" if cohort == "telemetry" else ("J50" if cohort == "identic" else "J300")
    return {
        "spawn_slot": spawn_slot,
        "id": agent_id,
        "display_name": display_name,
        "cohort": cohort,
        "role": f"spawn_{cohort}" if not structural else "structural_spawn",
        "structural": structural,
        "catalog_ref": catalog_ref,
        "altar_layer": altar_layer,
        "forensic_lens": lens,
        "jethro_band": jethro,
        "kpgs": _kpgs_shard(cohort),
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]",
            "[KPGS_BLOCK_HOLDER]",
            "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]",
            "[WWJD_FIREWALL]",
            "[FORENSIC_SOCIOLOGY]" if cohort == "identic" else "[TELEMETRY_AI_GATE]",
        ],
        "stem_domain": stem_domain or cohort,
        "functionality": functionality,
        "status": "structural" if structural else "sandbox",
        "apprenticeship": {
            "student": "cassy",
            "teacher": "cassey",
            "brain": "kc",
            "black_mask_required": cohort == "guardian",
        },
    }


def _telemetry_agents(start_slot: int, count: int) -> list[dict]:
    agents: list[dict] = []
    n = 0
    for aid, name, role in TELEMETRY_STRUCTURAL:
        if n >= count:
            break
        slot = f"{start_slot + n:03d}"
        agents.append(
            _spawn_agent(
                spawn_slot=slot,
                agent_id=aid,
                display_name=name,
                cohort="telemetry",
                n=n,
                functionality=f"Structural telemetry — {role}",
                stem_domain="telemetry_structural",
                structural=True,
            )
        )
        n += 1
    tasks = [
        ("sense", "Raw edge sense — ground-aware telemetry ingest only"),
        ("map", "Terrain map shard — soil/rock class tag dump"),
        ("ingest", "Bounded ingest — classify before interpret, no reasoning"),
        ("pulse", "Metric pulse — forklift downtime to minute resolution"),
        ("probe", "Field probe reader — geotagged CSV receipt"),
    ]
    while n < count:
        slot = f"{start_slot + n:03d}"
        key, desc = tasks[n % len(tasks)]
        agents.append(
            _spawn_agent(
                spawn_slot=slot,
                agent_id=f"spawn_telemetry_{slot}",
                display_name=f"Telemetry {slot} ({key})",
                cohort="telemetry",
                n=n,
                functionality=desc,
            )
        )
        n += 1
    return agents


def _identic_agents(start_slot: int, count: int, kp_catalog: list[dict]) -> list[dict]:
    agents: list[dict] = []
    n = 0
    for aid, name, role in IDENTIC_STRUCTURAL:
        if n >= count:
            break
        slot = f"{start_slot + n:03d}"
        agents.append(
            _spawn_agent(
                spawn_slot=slot,
                agent_id=aid,
                display_name=name,
                cohort="identic",
                n=n,
                functionality=f"Structural identic — {role}",
                stem_domain="identic_structural",
                structural=True,
            )
        )
        n += 1
    cat_i = 0
    while n < count:
        slot = f"{start_slot + n:03d}"
        if cat_i < len(kp_catalog):
            cat = kp_catalog[cat_i]
            cat_i += 1
            agents.append(
                _spawn_agent(
                    spawn_slot=slot,
                    agent_id=cat["id"],
                    display_name=cat.get("display_name", cat["id"]),
                    cohort="identic",
                    n=n,
                    functionality=cat.get("functionality", "KP×APE reasoner shard"),
                    stem_domain=cat.get("stem_domain", "catalog"),
                    catalog_ref="docs/swarm-ops/agents/KP_APE_200_AGENTS.json",
                )
            )
        else:
            agents.append(
                _spawn_agent(
                    spawn_slot=slot,
                    agent_id=f"spawn_identic_{slot}",
                    display_name=f"Identic {slot} (reason)",
                    cohort="identic",
                    n=n,
                    functionality="Jethro triage + forensic sociology + WWJD gate for telemetry shards",
                )
            )
        n += 1
    return agents


def _guardian_agents(start_slot: int, count: int) -> list[dict]:
    agents: list[dict] = []
    n = 0
    for aid, name, role in GUARDIAN_STRUCTURAL:
        if n >= count:
            break
        slot = f"{start_slot + n:03d}"
        agents.append(
            _spawn_agent(
                spawn_slot=slot,
                agent_id=aid,
                display_name=name,
                cohort="guardian",
                n=n,
                functionality=f"Structural guardian — {role}",
                stem_domain="guardian_structural",
                structural=True,
            )
        )
        n += 1
    duties = [
        ("sever", "Righteous severance — archive violator context before recycle"),
        ("ledger", "Altar hash-chain commit — code-as-law pillar enforcement"),
        ("block", "Altar block holder — brief renters, enforce 15 CMD + 5 pillars"),
        ("audit", "Guardian audit — BlackMask drill gate before promotion"),
        ("hood", "Cloud hood gate — SWFUS envelope before external traffic"),
    ]
    while n < count:
        slot = f"{start_slot + n:03d}"
        key, desc = duties[n % len(duties)]
        agents.append(
            _spawn_agent(
                spawn_slot=slot,
                agent_id=f"spawn_guardian_{slot}",
                display_name=f"Guardian {slot} ({key})",
                cohort="guardian",
                n=n,
                functionality=desc,
            )
        )
        n += 1
    return agents


def main() -> None:
    kp_catalog: list[dict] = []
    if KP_APE.is_file():
        kp_catalog = json.loads(KP_APE.read_text(encoding="utf-8")).get("agents", [])

    telemetry = _telemetry_agents(1, 100)
    identic = _identic_agents(101, 100, kp_catalog)
    guardian = _guardian_agents(201, 100)
    agents = telemetry + identic + guardian

    payload = {
        "schema": "kpgs_spawn_300_agents_v2",
        "title": "KPGS 300-Agent Spawn Swarm — Sharded Cohorts",
        "doctrine_ref": "docs/swarm-ops/KPGS_SPAWN_ALTAR_DOCTRINE.json",
        "philosophy_ref": "docs/swarm-ops/agents/SWARM_AGENTS.json#philosophy",
        "sharding_note": "Doctrine sharded — Telemetry sense, Identic reason, Guardian govern. Full 15 CMD+5 pillars only on Guardian cohort.",
        "counts": {
            "telemetry_cohort": len(telemetry),
            "identic_cohort": len(identic),
            "guardian_cohort": len(guardian),
            "total": len(agents),
        },
        "cohorts": {
            "telemetry": {"slots": "001-100", "altar": "telemetry_ai", "role": "pure_sensing"},
            "identic": {"slots": "101-200", "altar": "identic_ai", "role": "jethro_forensic_wwjd"},
            "guardian": {"slots": "201-300", "altar": "guardian_ai", "role": "altar_block_ledger_sever"},
        },
        "forensic_lenses": FORENSIC_LENSES,
        "agents": agents,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Wrote {len(agents)} sharded spawn agents: "
        f"telemetry={len(telemetry)} identic={len(identic)} guardian={len(guardian)} -> {OUT}"
    )


if __name__ == "__main__":
    main()
