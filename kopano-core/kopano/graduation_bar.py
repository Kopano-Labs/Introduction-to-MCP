"""
Phase 5 — Graduation bar (separate from BOOT, drill, and operating mesh).

Public "graduated" requires verified production rows in Review Log — not:
- BlackMask drill alone
- operating_mesh status
- KPEFS vector tags
- MAO route success

External swarm (Kimi): CMD-03 — manual receipt only (swarm_ack / kimi_ack + evidence_urls).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
MANIFEST_PATH = REPO_ROOT / "docs" / "swarm-ops" / "apprenticeship" / "kc_apprenticeship_250.json"
PROMOTION_LAW_PATH = REPO_ROOT / "Structure" / "07-Agents" / "PROMOTION_LAW.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _verified_production() -> tuple[int, bool, int, str]:
    import sys

    scripts = REPO_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from kc_verified_production import DEFAULT_MIN, check_minimum, count_verified

    n, _rows = count_verified()
    bar = int(DEFAULT_MIN)
    if MANIFEST_PATH.is_file():
        try:
            bar = int(json.loads(MANIFEST_PATH.read_text(encoding="utf-8")).get("public_graduation_bar", bar))
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            pass
    ok, msg = check_minimum(bar)
    return n, ok, bar, msg


def _load_main_brain_rows() -> list[dict[str, Any]]:
    if not MAIN_BRAIN_LOG.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in MAIN_BRAIN_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def external_swarm_receipt_status() -> dict[str, Any]:
    """CMD-03 — external orchestration needs manual kimi_ack / swarm_ack receipt."""
    ack_kinds = frozenset({"swarm_ack", "kimi_ack"})
    matches: list[dict[str, Any]] = []
    for row in _load_main_brain_rows():
        if row.get("kind") not in ack_kinds:
            continue
        urls = row.get("evidence_urls") or []
        if urls:
            matches.append(
                {
                    "kind": row.get("kind"),
                    "ts": row.get("ts"),
                    "summary": (row.get("summary") or "")[:120],
                }
            )
    return {
        "cmd03": "No fake swarm ACK — external orchestration is manual-execution-required until receipt exists.",
        "receipt_present": len(matches) > 0,
        "receipt_count": len(matches),
        "latest": matches[-1] if matches else None,
        "how_to_log": "python scripts/kc_log_append.py kimi-ack (see docs/swarm-ops/KIMI_ACK_FORMAT.md)",
    }


def graduation_bar_status() -> dict[str, Any]:
    """Full Phase 5 status for API / Studio / PoC."""
    n, bar_met, bar, vp_msg = _verified_production()
    external = external_swarm_receipt_status()

    operating_mesh: dict[str, Any] = {}
    try:
        from .operating_mesh import operating_mesh_status

        operating_mesh = operating_mesh_status()
    except ImportError:
        operating_mesh = {"error": "operating_mesh_unavailable"}

    phase3 = bool(operating_mesh.get("phase3_exit_met"))
    public_graduated = bar_met  # Chief Architect sign-off remains external/human

    law: dict[str, Any] = {}
    if PROMOTION_LAW_PATH.is_file():
        try:
            law = json.loads(PROMOTION_LAW_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    kpgs: dict[str, Any] = {}
    try:
        from .kpgs_governance import governance_status

        kpgs = governance_status()
    except ImportError:
        kpgs = {"error": "kpgs_governance_unavailable"}

    return {
        "schema": "graduation_bar_status_v1",
        "law": law.get("law", "No promotion without proof. Drill is not graduation."),
        "forbidden_claims": law.get("forbidden_claims", []),
        "verified_production": n,
        "public_graduation_bar": bar,
        "production_bar_met": bar_met,
        "production_bar_message": vp_msg,
        "operating_mesh_phase3_met": phase3,
        "operating_is_not_graduation": True,
        "public_graduated": public_graduated,
        "external_swarm": external,
        "guard_command": f"python scripts/kc_guard.py all --require-verified-production {bar}",
        "kpgs_governance": kpgs,
        "main_brain_authority": "Schematics",
        "steward_lane": {
            "brain": "kc",
            "teacher": "cassey",
            "lead_student": "cassy",
            "note": "KC Save|Watch only — Cassey teacher_review — students under Cassy apprenticeship.",
        },
        "phase5_exit_met": bar_met,
    }


def graduation_claim_allowed(*, claim: str) -> dict[str, Any]:
    """
    Validate a human-facing claim string does not conflate operating/drill with graduation.
    """
    text = (claim or "").lower()
    st = graduation_bar_status()
    wants_graduation = any(
        w in text
        for w in (
            "graduated",
            "graduation complete",
            "production graduated",
            "public graduation",
        )
    )
    conflates_operating = wants_graduation and (
        "operating mesh" in text
        or "operating alone" in text
        or ("operating" in text and "mesh" in text)
    )
    conflates_drill = wants_graduation and any(
        w in text for w in ("drill promoted", "250 promoted", "blackmask alone", "from drill")
    )

    allowed = True
    reasons: list[str] = []
    if wants_graduation and not st["production_bar_met"]:
        allowed = False
        reasons.append(
            f"verified_production={st['verified_production']} need {st['public_graduation_bar']}"
        )
    if conflates_operating:
        allowed = False
        reasons.append("operating_mesh is not public graduation — use verified production bar")
    if conflates_drill:
        allowed = False
        reasons.append("drill promotion is not graduation")

    return {
        "claim": claim[:200],
        "allowed": allowed,
        "wants_graduation_language": wants_graduation,
        "reasons": reasons,
        "status": st,
    }


def record_steward_trust(*, note: str = "") -> dict[str, Any]:
    """Append Main Brain receipt — Chief Architect trust in KC / Cassey / student lane."""
    st = graduation_bar_status()
    extra = (note or "").strip()
    summary = (
        f"[KPEFS_GRADUATION_BAR] steward_trust | KC ledger Save|Watch | "
        f"teacher: cassey | lead_student: cassy | "
        f"verified_production: {st['verified_production']}/{st['public_graduation_bar']} | "
        f"operating_mesh: {st['operating_mesh_phase3_met']} | "
        f"drill_is_not_graduation: true"
    )
    if extra:
        summary = f"{summary} | {extra[:160]}"

    row = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now(),
        "kind": "kpefs_steward_trust",
        "summary": summary,
        "exit_code": 0,
        "boot": "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1",
    }
    MAIN_BRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MAIN_BRAIN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"stored": True, **row}


def lock_kpefs_phases_3_5() -> dict[str, Any]:
    """Main Brain receipt — Phases 3-5 complete (operating mesh + graduation bar)."""
    st = graduation_bar_status()
    try:
        from .operating_mesh import operating_mesh_status

        om = operating_mesh_status()
    except ImportError:
        om = {}
    summary = (
        f"[KPEFS_FOUR_VECTOR] Phases 3-5 locked | operating: "
        f"{om.get('operating_count', 0)}/{om.get('flagships_total', 9)} | "
        f"verified_production: {st['verified_production']}/{st['public_graduation_bar']} | "
        f"drill_is_not_graduation: true | steward: kc+cassey+cassy"
    )
    row = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now(),
        "kind": "kpefs_phases_3_5_locked",
        "summary": summary,
        "exit_code": 0,
    }
    MAIN_BRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MAIN_BRAIN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"stored": True, **row}


def run_guard_verified_production(*, min_required: int | None = None) -> dict[str, Any]:
    """Invoke kc_guard doctrine-verified-production check."""
    import subprocess
    import sys

    st = graduation_bar_status()
    n = min_required if min_required is not None else st["public_graduation_bar"]
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "kc_guard.py"),
            "doctrine-verified-production",
            "--min",
            str(n),
            "--repo-root",
            str(REPO_ROOT),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "passed": proc.returncode == 0,
    }
