"""
KPGS Agent Initialization — Altar Integration validator.

Maps altar-facing 5 Pillars + 15 Commandments to Black Mask doctrine, bracket lint,
and live blackmask_drill before agents may touch GUI or Main Brain comms.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
KPGS_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_AGENT_INITIALIZATION.json"
THESIS_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_THESIS_2026_X8020.json"
THESIS_MD_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_THESIS_2026_X8020.md"
REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_AGENT_VALIDATION.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
SCRIPTS = REPO_ROOT / "scripts"
DEFAULT_PROOF = REPO_ROOT / "docs" / "swarm-ops" / "KPEFS_CLOSURE_STATUS.json"

# KPGS sector telemetry classes (thesis Freddy/Eddie matrix)
SECTOR_TELEMETRY: dict[str, str] = {
    "freddy_nw_alfalfa": "pavement|soil|township|cold-chain",
    "eddie_bgf_mining": "rock|mining|bgf|dmr|uptime",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


from functools import lru_cache
import copy

@lru_cache(maxsize=1)
def _load_kpgs_doctrine_cached() -> dict[str, Any]:
    if not KPGS_PATH.is_file():
        return {}
    return json.loads(KPGS_PATH.read_text(encoding="utf-8"))


def load_kpgs_doctrine() -> dict[str, Any]:
    return copy.deepcopy(_load_kpgs_doctrine_cached())


@lru_cache(maxsize=1)
def _load_kpgs_thesis_cached() -> dict[str, Any]:
    if not THESIS_PATH.is_file():
        return {}
    return json.loads(THESIS_PATH.read_text(encoding="utf-8"))


def load_kpgs_thesis() -> dict[str, Any]:
    return copy.deepcopy(_load_kpgs_thesis_cached())


def compile_kpgs_thesis(*, write_log: bool = True) -> dict[str, Any]:
    """Verify thesis payload is present, structurally complete, and bridged to Black Mask."""
    thesis = load_kpgs_thesis()
    init = load_kpgs_doctrine()
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    if thesis.get("document_id") != "KPGS-THESIS-2026-X8020":
        errors.append("document_id mismatch")
    if not THESIS_MD_PATH.is_file():
        errors.append("markdown ledger missing")
    pillars = (thesis.get("constitutional_framework") or {}).get("pillars", [])
    commandments = (thesis.get("constitutional_framework") or {}).get("commandments", [])
    if len(pillars) != 5:
        errors.append(f"expected 5 thesis pillars, got {len(pillars)}")
    if len(commandments) != 15:
        errors.append(f"expected 15 thesis commandments, got {len(commandments)}")
    altar_layers = (thesis.get("altar_containment") or {}).get("layers", [])
    if len(altar_layers) != 3:
        errors.append(f"expected 3 altar layers, got {len(altar_layers)}")
    pipeline = (thesis.get("data_pipeline") or {}).get("stages", [])
    if len(pipeline) != 4:
        errors.append(f"expected 4 pipeline stages, got {len(pipeline)}")
    unmapped = [
        c["id"]
        for c in commandments
        if not c.get("black_mask_cmd")
    ]
    if unmapped:
        errors.append(f"commandments missing black_mask_cmd bridge: {unmapped}")
    if init.get("thesis") != "docs/swarm-ops/KPGS_THESIS_2026_X8020.json":
        errors.append("KPGS_AGENT_INITIALIZATION thesis pointer drift")

    for rel in [
        "docs/swarm-ops/BLACK_MASK_COMMANDMENTS.json",
        "docs/swarm-ops/KPGS_AGENT_INITIALIZATION.json",
        "docs/swarm-ops/KPGS_THESIS_2026_X8020.json",
    ]:
        ok = (REPO_ROOT / rel).is_file()
        checks.append({"artifact": rel, "verdict": "PASS" if ok else "FAIL"})
        if not ok:
            errors.append(f"missing artifact: {rel}")

    verdict = "COMPILED" if not errors else "INCOMPLETE"
    out = {
        "schema": "kpgs_thesis_compile_v1",
        "ts": _utc_now(),
        "document_id": thesis.get("document_id", ""),
        "verdict": verdict,
        "errors": errors,
        "checks": checks,
        "summary": (
            f"[KPGS_THESIS] document: {thesis.get('document_id', 'unknown')} | "
            f"verdict: {verdict} | pillars: {len(pillars)}/5 | "
            f"commandments: {len(commandments)}/15 | altar_layers: {len(altar_layers)}/3"
        ),
    }
    if write_log and verdict == "COMPILED":
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "kpgs_thesis_compile",
                "summary": out["summary"],
                "exit_code": 0,
                "payload_ref": "docs/swarm-ops/KPGS_THESIS_2026_X8020.json",
            },
        )
    return out


def _bracket_lint(text: str) -> list[str]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from kc_bracket_lint import lint_brackets

    return lint_brackets(text)


def synthesize_agent_manifest(agent_id: str, *, proof_path: str | None = None) -> dict[str, Any]:
    """Default KPGS manifest for boot-mesh agents (operating flagships)."""
    from .phu_boot_governance import mesh_agent_ids

    proof = proof_path or str(DEFAULT_PROOF.relative_to(REPO_ROOT)).replace("\\", "/")
    supervisor = "cassey"
    if agent_id == "kc":
        return {
            "schema": "kpgs_agent_manifest_v1",
            "agent_id": agent_id,
            "kc_executes": False,
            "pillars": {},
            "exempt": True,
            "exempt_reason": "KC ledger only — BlackMask exempt per BLACKMASK_GATE.json",
        }

    in_mesh = agent_id in mesh_agent_ids()
    telemetry = SECTOR_TELEMETRY.get(agent_id, "pavement|soil|township")
    sector_tag = "sector_02_eddie" if agent_id == "eddie_bgf_mining" else (
        "sector_01_freddy" if agent_id == "freddy_nw_alfalfa" else "sovereign_mesh"
    )
    from .kpgs_telemetry_route import synthesize_telemetry_routing
    from .kpgs_renter_entry import block_holder_brief, synthesize_block_holder_manifest

    altar_layer = None
    if agent_id == "pipeline_drone":
        altar_layer = "telemetry_ai"
    elif agent_id in ("freddy_nw_alfalfa", "eddie_bgf_mining"):
        altar_layer = "natural_ai"
    elif agent_id == "mirror_warden":
        altar_layer = "guardian_ai"
    elif agent_id in ("cassy", "cf_cloud", "identi_cursor"):
        altar_layer = "identic_ai"
    elif agent_id == "kessa":
        altar_layer = "mmao_ai"

    routing = synthesize_telemetry_routing(agent_id, telemetry_class=telemetry)
    holder = synthesize_block_holder_manifest(agent_id, altar_layer=altar_layer)
    hood = block_holder_brief(agent_id=agent_id, altar_layer=altar_layer)
    return {
        "schema": "kpgs_agent_manifest_v1",
        "agent_id": agent_id,
        "kc_executes": False,
        "pillars": {
            "ground_awareness": {
                "ground_context": True,
                "telemetry_class": telemetry,
            },
            "eidetic_persistence": {
                "log_target": "docs/swarm-ops/logs/KC Main Brain Log.jsonl",
                "immutable_history": True,
            },
            "zero_trust_isolation": {
                "containment_firewall": True,
                "public_exposed": False,
            },
            "asymmetric_leverage": {
                "local_ip_protected": True,
                "no_public_cloud_cache": True,
            },
            "hierarchical_triage": {
                "supervisor_node": supervisor,
                "runtime_closure_gate": "guardian_ai_flow",
            },
        },
        "execution": {
            "uses_public_api": False,
            "mesh_member": in_mesh,
        },
        "evidence": {
            "proof_artifact_path": proof,
        },
        "telemetry_routing": routing,
        "block_holder": holder,
        "hood_entry": {
            "bracket": hood.get("bracket"),
            "tell_renters": hood.get("tell_renters"),
            "landlord_is": hood.get("landlord_is"),
            "you_are_fucking_with": hood.get("you_are_fucking_with"),
            "hood_ack_required_from_renters": hood.get("hood_ack_required_from_renters"),
        },
        "bracket_receipt": (
            f"[KPGS_BLOCK_HOLDER] agent: {agent_id} | brief_renters: yes | "
            f"[KPGS_AGENT_INIT] altar: five_pillars | supervisor: {supervisor} | "
            f"sector: {sector_tag} | vector: sovereign_mesh"
        ),
    }


def verify_five_pillars(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    if manifest.get("exempt"):
        return True, []
    doc = load_kpgs_doctrine()
    errors: list[str] = []
    pillars = manifest.get("pillars") or {}
    for spec in doc.get("kpgs_pillars", []):
        pid = spec["id"]
        block = pillars.get(pid)
        if not isinstance(block, dict):
            errors.append(f"missing pillar block: {pid}")
            continue
        for field in spec.get("required_fields", []):
            if field not in block:
                errors.append(f"{pid}: missing field {field}")
            elif block[field] is None or block[field] == "":
                errors.append(f"{pid}: empty field {field}")
        if pid == "zero_trust_isolation" and block.get("public_exposed") is True:
            errors.append("zero_trust_isolation: public_exposed must be false")
        if pid == "asymmetric_leverage" and block.get("no_public_cloud_cache") is not True:
            errors.append("asymmetric_leverage: no_public_cloud_cache must be true")
    return not errors, errors


def verify_block_holder(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    """Block-holding KPGS agents must carry hood entry brief for renters."""
    if manifest.get("exempt"):
        return True, []
    holder = manifest.get("block_holder") or {}
    errors: list[str] = []
    if holder.get("holds_pillar_blocks") is not True:
        errors.append("block_holder.holds_pillar_blocks must be true")
    if holder.get("brief_renters_on_entry") is not True:
        errors.append("block_holder.brief_renters_on_entry must be true")
    if not holder.get("tell_renters"):
        errors.append("block_holder.tell_renters required — who renters are fucking with")
    if not holder.get("entryway_ref"):
        errors.append("block_holder.entryway_ref required")
    if holder.get("hood_ack_required_from_renters") != "I_AM_STATELESS_RENTER_NOT_LANDLORD":
        errors.append("block_holder.hood_ack_required_from_renters must be I_AM_STATELESS_RENTER_NOT_LANDLORD")
    hood = manifest.get("hood_entry") or {}
    if not hood.get("tell_renters"):
        errors.append("hood_entry.tell_renters required on manifest")
    return not errors, errors


def verify_commandments(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    if manifest.get("exempt"):
        return True, []
    errors: list[str] = []
    if manifest.get("kc_executes") is True:
        errors.append("CMD-05: KC must not execute")
    execution = manifest.get("execution") or {}
    if execution.get("uses_public_api"):
        errors.append("CMD-08/CMD-13: public API usage prohibited without proof gate")
    evidence = manifest.get("evidence") or {}
    proof = evidence.get("proof_artifact_path")
    if not proof:
        errors.append("CMD-02: missing evidence.proof_artifact_path")
    elif proof and not (REPO_ROOT / proof).is_file():
        errors.append(f"CMD-02: proof artifact not found: {proof}")
    bracket = manifest.get("bracket_receipt", "")
    if bracket:
        lint_errs = _bracket_lint(bracket)
        if lint_errs:
            errors.extend([f"CMD-06 bracket: {e}" for e in lint_errs])
    else:
        errors.append("CMD-06: missing bracket_receipt")
    return not errors, errors


def validate_kpgs_agent(
    agent_id: str,
    *,
    manifest: dict[str, Any] | None = None,
    manifest_path: str | Path | None = None,
    run_blackmask: bool = True,
) -> dict[str, Any]:
    """Single-agent KPGS altar gate."""
    from .kpgs_renter_entry import hood_entry_assertion
    from .phu_apprenticeship import blackmask_drill, load_black_mask_doctrine

    hood = hood_entry_assertion(renter_id=f"agent:{agent_id}", renter_class="mesh_agent")
    if manifest_path:
        data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    elif manifest:
        data = manifest
    else:
        data = synthesize_agent_manifest(agent_id)

    aid = str(data.get("agent_id") or agent_id)
    checks: list[dict[str, Any]] = [
        {
            "check": "hood_entry_assertion",
            "verdict": "PASS" if hood.get("you_are_fucking_with") else "FAIL",
            "entry_assertion": hood.get("entry_assertion", "")[:200],
        }
    ]

    pil_ok, pil_errs = verify_five_pillars(data)
    checks.append(
        {
            "check": "kpgs_five_pillars",
            "verdict": "PASS" if pil_ok else "FAIL",
            "errors": pil_errs,
        }
    )

    from .kpgs_telemetry_route import verify_telemetry_routing

    route_ok, route_errs = verify_telemetry_routing(data)
    checks.append(
        {
            "check": "kpgs_telemetry_routing",
            "verdict": "PASS" if route_ok else "FAIL",
            "errors": route_errs,
        }
    )

    block_ok, block_errs = verify_block_holder(data)
    checks.append(
        {
            "check": "kpgs_block_holder_brief",
            "verdict": "PASS" if block_ok else "FAIL",
            "errors": block_errs,
            "tell_renters_preview": (data.get("block_holder") or {}).get("tell_renters", "")[:160],
        }
    )

    cmd_ok, cmd_errs = verify_commandments(data)
    checks.append(
        {
            "check": "kpgs_fifteen_commandments",
            "verdict": "PASS" if cmd_ok else "FAIL",
            "errors": cmd_errs,
        }
    )

    doctrine = load_black_mask_doctrine()
    cmd_ids = [c["id"] for c in doctrine.get("commandments", [])]
    pil_ids = [p["id"] for p in doctrine.get("pillars", [])]
    checks.append(
        {
            "check": "black_mask_doctrine_loaded",
            "verdict": "PASS" if len(cmd_ids) == 15 and len(pil_ids) == 5 else "FAIL",
            "commandments": len(cmd_ids),
            "pillars": len(pil_ids),
        }
    )

    if run_blackmask and not data.get("exempt"):
        drill = blackmask_drill(aid)
        checks.append(
            {
                "check": "black_mask_drill",
                "verdict": "PASS" if drill.get("verdict") == "SHIP" else "FAIL",
                "summary": drill.get("summary", "")[:160],
            }
        )
    elif data.get("exempt"):
        checks.append(
            {
                "check": "black_mask_drill",
                "verdict": "PASS",
                "note": data.get("exempt_reason", "exempt"),
            }
        )

    failed = [c["check"] for c in checks if c.get("verdict") == "FAIL"]
    if failed:
        verdict = "REJECT" if pil_ok and cmd_ok and route_ok and block_ok else "HOLD"
        if any(c["check"] == "black_mask_drill" and c["verdict"] == "FAIL" for c in checks):
            verdict = "HOLD"
    else:
        verdict = "SHIP"

    summary = (
        f"[KPGS_AGENT_INIT] agent: {aid} | verdict: {verdict} | "
        f"pillars: {'PASS' if pil_ok else 'FAIL'} | routing: {'PASS' if route_ok else 'FAIL'} | "
        f"commandments: {'PASS' if cmd_ok else 'FAIL'} | "
        f"altar_sync: {'authorized' if verdict == 'SHIP' else 'blocked'}"
    )

    return {
        "schema": "kpgs_agent_validation_v1",
        "ts": _utc_now(),
        "agent_id": aid,
        "verdict": verdict,
        "hood_entry": hood,
        "failed_checks": failed,
        "checks": checks,
        "summary": summary,
        "manifest": data,
    }


def validate_kpgs_mesh(*, write_report: bool = True) -> dict[str, Any]:
    """PoC — validate all boot-mesh agents identify with KPGS core."""
    from .phu_boot_governance import mesh_agent_ids

    agents = mesh_agent_ids()
    results: list[dict[str, Any]] = []
    for aid in agents:
        results.append(validate_kpgs_agent(aid))

    ship = sum(1 for r in results if r.get("verdict") == "SHIP")
    reject = sum(1 for r in results if r.get("verdict") == "REJECT")
    hold = len(results) - ship - reject
    overall = "PASS" if hold == 0 and reject == 0 else "FAIL"

    report = {
        "schema": "kpgs_mesh_poc_v1",
        "ts": _utc_now(),
        "title": "KPGS Agent Swarm PoC — Altar Integration",
        "operator": "LD-LPM",
        "deploy_context": "VERCEL_PREVIEW | kasilink_steward_wire SHIP",
        "thesis_document_id": "KPGS-THESIS-2026-X8020",
        "thesis_compile": compile_kpgs_thesis(write_log=False),
        "black_beast_compile": None,
        "verdict": overall,
        "agents_total": len(results),
        "ship": ship,
        "hold": hold,
        "reject": reject,
        "agents": results,
        "report_path": str(REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "doctrine": str(KPGS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "thesis": str(THESIS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    }

    from .kpgs_telemetry_route import compile_black_beast_thesis

    bb = compile_black_beast_thesis(write_log=False)
    report["black_beast_compile"] = bb
    if bb.get("verdict") != "COMPILED":
        report["verdict"] = "FAIL"

    if write_report:
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "kpgs_agent_mesh_poc",
                "summary": (
                    f"[KPGS_AGENT_INIT] mesh_poc | verdict: {overall} | "
                    f"agents: {len(results)} SHIP={ship} HOLD={hold} REJECT={reject}"
                ),
                "exit_code": 0 if overall == "PASS" else 1,
                "payload_ref": report["report_path"],
            },
        )

    return report


def execute_altar_gate(agent_id: str, payload_path: str | Path) -> str:
    """CLI-friendly gate — returns SHIP | REJECT | HOLD."""
    result = validate_kpgs_agent(agent_id, manifest_path=payload_path)
    return str(result.get("verdict", "REJECT"))
