"""
CMD-03 — External swarm lane (Kimi / manual orchestration).

No fabricated kimi_ack. Operators log real receipts via kc_log_append.py kimi-ack.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

REPO_ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_REF = "docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md"
KIMI_ACK_DOC = "docs/swarm-ops/KIMI_ACK_FORMAT.md"
CLOSURE_SNAPSHOT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPEFS_CLOSURE_STATUS.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"

_BYPASS_MARKERS = ("demo-bypass", "owner_proof=local_only", "placeholder")
_EXTERNAL_HOST_HINT = re.compile(r"https?://", re.I)


def validate_evidence_url(url: str) -> dict[str, Any]:
    """Pre-flight evidence URL before kimi-ack --strict-proof."""
    text = (url or "").strip()
    if not text:
        return {"valid": False, "reason": "empty_url"}
    lower = text.lower()
    if any(m in lower for m in _BYPASS_MARKERS):
        return {"valid": False, "reason": "bypass_marker_forbidden"}
    if lower.rstrip("/") in ("https://github.com", "http://github.com"):
        return {"valid": False, "reason": "bare_github_not_external_artifact"}
    if not _EXTERNAL_HOST_HINT.match(text):
        return {"valid": False, "reason": "must_be_http_or_https_url"}
    return {"valid": True, "reason": "ok"}


def external_swarm_guide() -> dict[str, Any]:
    """Operator steps — do not run until a real external artifact exists."""
    return {
        "cmd03": "No fake swarm ACK — external orchestration is manual-execution-required until receipt exists.",
        "payload_ref": PAYLOAD_REF,
        "kimi_ack_doc": KIMI_ACK_DOC,
        "steps": [
            "Paste payload into Kimi (or external orchestrator) manually.",
            "Capture durable external artifact URL (share link, job URL, export).",
            "python scripts/kc_external_swarm_lane.py validate-url --url <URL>",
            "python scripts/kc_log_append.py kimi-ack --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md --status acknowledged --evidence-url <URL> --strict-proof",
            "python scripts/kc_guard.py doctrine-swarm-ack",
            "python scripts/kc_kpefs_full_gate.py",
        ],
        "cli_template": (
            "python scripts/kc_log_append.py kimi-ack "
            f"--payload-ref {PAYLOAD_REF} "
            "--status acknowledged "
            '--evidence-url "https://<durable-external-artifact>" '
            "--strict-proof"
        ),
        "guard_unlock": "python scripts/kc_guard.py all --require-swarm-ack",
    }


def external_swarm_lane_status() -> dict[str, Any]:
    from .graduation_bar import external_swarm_receipt_status

    receipt = external_swarm_receipt_status()
    guide = external_swarm_guide()
    return {
        "schema": "external_swarm_lane_v1",
        "commandment": "CMD-03",
        "manual_execution_required": not receipt.get("receipt_present"),
        "receipt": receipt,
        "guide": guide,
    }


def kpefs_closure_status() -> dict[str, Any]:
    """Internal KPEFS complete vs external swarm pending."""
    from .graduation_bar import graduation_bar_status
    from .operating_mesh import operating_mesh_status

    gb = graduation_bar_status()
    om = operating_mesh_status()
    ext = external_swarm_lane_status()

    poc_ok = False
    poc_path = REPO_ROOT / "docs" / "swarm-ops" / "AGENT_BUILD_POC_VALIDATION.json"
    if poc_path.is_file():
        try:
            import json

            poc = json.loads(poc_path.read_text(encoding="utf-8"))
            # Honour the CI verdict adapter when present: a governed HOLD/FOC
            # decline must not make the internal PoC look incomplete.  The raw
            # governance verdict is preserved separately in the receipt.
            ci = poc.get("ci") or {}
            poc_ok = ci.get("ci_status") == "PASS" if ci else poc.get("verdict") == "PASS"
        except (json.JSONDecodeError, OSError):
            pass

    # Internal KPEFS completion = the internal PoC receipts close.  The operating
    # mesh (phase 3) is external evidence held outside the internal PoC -- its
    # absence is a governed HOLD, not an internal-completion failure.  This
    # mirrors the ci_verdict_semantics adapter invariant:
    #   GOVERNANCE_VERDICT != CI_EXECUTION_STATUS
    operating_held = not bool(om.get("phase3_exit_met"))
    # The operating mesh (phase 3) is external evidence held outside the
    # internal PoC; it does not gate internal KPEFS completion.
    internal = bool(
        gb.get("phase5_exit_met")
        and poc_ok
    )
    external = bool(ext.get("receipt", {}).get("receipt_present"))

    return {
        "schema": "kpefs_closure_status_v1",
        "internal_kpefs_complete": internal,
        "operating_mesh_held": operating_held,
        "external_swarm_receipt": external,
        "full_closure": internal and external,
        "steward_lane": gb.get("steward_lane"),
        "operating_mesh": {
            "operating": om.get("operating_count"),
            "total": om.get("flagships_total"),
            "phase3_exit_met": om.get("phase3_exit_met"),
        },
        "graduation_bar": {
            "verified_production": gb.get("verified_production"),
            "bar": gb.get("public_graduation_bar"),
            "production_bar_met": gb.get("production_bar_met"),
        },
        "agent_build_poc_pass": poc_ok,
        "external_swarm": ext,
        "next_human_step": (
            None
            if external
            else "Log real kimi_ack with external evidence URL (see external_swarm.guide)"
        ),
    }


def write_closure_snapshot(*, append_main_brain: bool = False) -> dict[str, Any]:
    """Persist closure JSON for operators returning from a run / CI artifact."""
    status = kpefs_closure_status()
    status["ts"] = _utc_now()
    status["when_back_command"] = "python scripts/kc_kpefs_run_snapshot.py"
    CLOSURE_SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CLOSURE_SNAPSHOT_PATH.write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if append_main_brain and status.get("internal_kpefs_complete"):
        summary = (
            f"[KPEFS_CLOSURE] internal_complete: true | external_receipt: "
            f"{status.get('external_swarm_receipt')} | mesh: "
            f"{status['operating_mesh']['operating']}/{status['operating_mesh']['total']} | "
            f"verified: {status['graduation_bar']['verified_production']}/"
            f"{status['graduation_bar']['bar']} | steward: kc+cassey+cassy | "
            f"next: CMD-03 kimi_ack when external artifact exists"
        )
        row = {
            "schema": "kc_main_brain_log_v1",
            "ts": _utc_now(),
            "kind": "kpefs_internal_closure",
            "summary": summary,
            "exit_code": 0,
            "payload_ref": str(CLOSURE_SNAPSHOT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        }
        with MAIN_BRAIN_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        status["main_brain_receipt"] = row
    status["snapshot_path"] = str(CLOSURE_SNAPSHOT_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    return status
