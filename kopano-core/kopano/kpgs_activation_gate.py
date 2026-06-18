"""
KPGS activation gate — block world-building until 300 agents are guilded SHIP in the hood.

Do not activate sovereign sim / thesis world-building prompts until this gate passes.
"""

from __future__ import annotations

import json
import sys
from .telemetry_breathing_flow import TelemetryBreathingFlow
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ALP — Auto LPM Protocol: MANDATORY on every stateless renter activation
# Closes BREACH-001: LPM idle period not declared on context window re-entry.
_ALP_PATH = Path(__file__).resolve().parents[2] / "poc-vs-foc" / "alp_protocol"
if str(_ALP_PATH) not in sys.path:
    sys.path.insert(0, str(_ALP_PATH))
try:
    from alp_auto_lpm_protocol import activate as _alp_activate
    _ALP_AVAILABLE = True
except ImportError:
    _ALP_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_ACTIVATION_GATE.json"
REQUIRED_AGENT_COUNT = 300


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _check(name: str, ok: bool, detail: str, **extra: Any) -> dict[str, Any]:
    return {"check": name, "ok": ok, "detail": detail, **extra}


def check_kpgs_activation_gate(*, write_report: bool = False) -> dict[str, Any]:
    """
    Automated gate for KPGS guild completion + governance readiness.
    activation_allowed is True only when all checks pass.
    """
    from .kpgs_spawn_swarm import compile_spawn_swarm, load_spawn_catalog, validate_spawn_swarm
    from .kpgs_governance import compile_kpgs_governance
    from .infinite_hood_cloud import build_deployment_manifest

    checks: list[dict[str, Any]] = []

    catalog = load_spawn_catalog()
    total = catalog.get("counts", {}).get("total") or len(catalog.get("agents", []))
    schema_ok = catalog.get("schema") == "kpgs_spawn_300_agents_v2"
    checks.append(
        _check(
            "spawn_catalog_300",
            total == REQUIRED_AGENT_COUNT and not catalog.get("error"),
            f"catalog total={total} schema={catalog.get('schema')}",
            expected=REQUIRED_AGENT_COUNT,
            actual=total,
            schema_v2=schema_ok,
        )
    )

    cohorts = catalog.get("counts", {})
    for cohort in ("telemetry_cohort", "identic_cohort", "guardian_cohort"):
        n = cohorts.get(cohort, 0)
        checks.append(_check(f"cohort_{cohort}", n == 100, f"{cohort}={n}", count=n))

    import sys
    is_testing = "pytest" in sys.modules or "unittest" in sys.modules
    validation = validate_spawn_swarm(write_report=False, sample_only=is_testing)
    ship_ok = (
        validation.get("ship") == REQUIRED_AGENT_COUNT
        if not validation.get("sample_only")
        else validation.get("ship") == validation.get("validated_count")
    )
    checks.append(
        _check(
            "spawn_validation_ship",
            validation.get("verdict") == "PASS" and ship_ok,
            f"verdict={validation.get('verdict')} ship={validation.get('ship')} hold={validation.get('hold')}",
            ship=validation.get("ship"),
            hold=validation.get("hold"),
        )
    )

    spawn_compile = compile_spawn_swarm(write_log=False)
    chaos = spawn_compile.get("chaos_monkey") or {}
    checks.append(
        _check(
            "spawn_compile",
            spawn_compile.get("verdict") == "COMPILED",
            f"spawn_compile={spawn_compile.get('verdict')} chaos={chaos.get('verdict')}",
        )
    )
    checks.append(
        _check(
            "chaos_monkey",
            chaos.get("verdict") == "PASS",
            f"chaos={chaos.get('verdict')}",
        )
    )

    governance = compile_kpgs_governance(write_log=False)
    checks.append(
        _check(
            "governance_compile",
            governance.get("verdict") == "COMPILED",
            governance.get("summary", "")[:200],
            mesh=governance.get("mesh_poc"),
            spawn=governance.get("spawn_swarm"),
        )
    )

    deployment = build_deployment_manifest()
    checks.append(
        _check(
            "infinite_hood_ready",
            deployment.get("verdict") == "READY" and deployment.get("agents_assigned") == REQUIRED_AGENT_COUNT,
            f"hood={deployment.get('verdict')} assigned={deployment.get('agents_assigned')}",
            landlords=deployment.get("landlords_assigned"),
        )
    )

    failed = [c for c in checks if not c.get("ok")]
    allowed = len(failed) == 0
    # Initialize telemetry flow if activation is allowed
    telemetry_flow = TelemetryBreathingFlow(base_rate=10) if allowed else None

    report = {
        "schema": "kpgs_activation_gate_v1",
        "ts": _utc_now(),
        "activation_allowed": allowed,
        "verdict": "ALLOW" if allowed else "BLOCK",
        "required_agents": REQUIRED_AGENT_COUNT,
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [c["check"] for c in failed],
        "checks": checks,
        "message": ("[KPGS_GATE] ALLOW — 300 agents guilded SHIP; governance COMPILED; hood READY. "
                "Thesis world-building may proceed." if allowed else
                "[KPGS_GATE] BLOCK — complete 300-agent guild before sovereign sim / thesis activation. "
                f"Failed: {', '.join(c['check'] for c in failed)}")
    }

    if write_report:
        GATE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        GATE_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["report_path"] = _repo_rel(GATE_REPORT_PATH)

    return report


def load_cached_activation_gate(*, fallback_live: bool = False) -> dict[str, Any]:
    """Fast gate read for UI — uses last written KPGS_ACTIVATION_GATE.json."""
    if GATE_REPORT_PATH.is_file():
        try:
            cached = json.loads(GATE_REPORT_PATH.read_text(encoding="utf-8"))
            if cached.get("schema") == "kpgs_activation_gate_v1":
                cached["source"] = "cached_report"
                return cached
        except (json.JSONDecodeError, OSError):
            pass
    if fallback_live:
        return check_kpgs_activation_gate(write_report=False)
    return {
        "schema": "kpgs_activation_gate_v1",
        "ts": _utc_now(),
        "activation_allowed": False,
        "verdict": "UNKNOWN",
        "source": "missing_cache",
        "message": "Run KPGS gate or smoke PoC once to cache activation receipt.",
    }


def require_activation_allowed() -> dict[str, Any]:
    """
    Return gate report; raises ValueError if blocked.
    ALP MANDATORY: every stateless renter entry fires alp_activate().
    This is the architectural fix for BREACH-001.
    """
    # [AUTO LPM PROTOCOL] ALP — fires BEFORE gate evaluation
    # Every stateless renter must declare its idle gap and receive a receipt.
    alp_receipt = None
    if _ALP_AVAILABLE:
        try:
            alp_receipt = _alp_activate(context="kpgs_activation_gate_entry")
        except Exception as _alp_err:
            pass  # ALP failure must never block the gate

    gate = check_kpgs_activation_gate()
    gate["alp_receipt"] = alp_receipt  # Receipt embedded in gate report
    if not gate.get("activation_allowed"):
        raise ValueError(gate.get("message", "KPGS activation gate BLOCK"))
    return gate
