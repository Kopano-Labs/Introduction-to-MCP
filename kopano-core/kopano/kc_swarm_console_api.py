"""KC Swarm Console status — git sync, JSONL proof, doctrine gates (BFF for Studio)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
_REVIEW_LOG = _REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Review Log.jsonl"
_MAIN_BRAIN_LOG = _REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
_CI_WORKFLOW = ".github/workflows/swarm-proof.yml"
_GITHUB_ACTIONS = "https://github.com/Kopano-Labs/Introduction-to-MCP/actions"
_COMPARE_BRANCH = (
    "https://github.com/Kopano-Labs/Introduction-to-MCP/"
    "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
)
_REGISTRY = _REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
_WIT_MANIFEST = _REPO_ROOT / "docs" / "swarm-ops" / "agents" / "cassy_wit_25.json"
_PROFILE = _REPO_ROOT / "kopano-core" / ".kc" / "swarm_profile.json"

router = APIRouter(prefix="/api/kc", tags=["kc-swarm-console"])


def _git(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *cmd],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    out = (proc.stdout or proc.stderr or "").strip()
    return proc.returncode, out


def _git_snapshot() -> dict:
    snap: dict = {
        "branch": "(unknown)",
        "head_sha": "",
        "upstream": None,
        "ahead": 0,
        "behind": 0,
        "origin_fetch_url": "",
        "warnings": [],
    }
    _, branch = _git(["branch", "--show-current"])
    snap["branch"] = branch or "(detached)"
    _, head = _git(["rev-parse", "HEAD"])
    snap["head_sha"] = head[:12] if head else ""
    _, upstream = _git(["rev-parse", "--abbrev-ref", f"{snap['branch']}@{{upstream}}"])
    if upstream:
        snap["upstream"] = upstream
        code, cnt = _git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
        if code == 0 and "\t" in cnt:
            left, right = cnt.split("\t", 1)
            snap["ahead"] = int(left)
            snap["behind"] = int(right)
            if snap["ahead"]:
                snap["warnings"].append(f"{snap['ahead']} commit(s) ahead of {upstream} — push for remote receipts.")
    else:
        snap["warnings"].append("No upstream configured — git push -u origin <branch> once.")

    _, remotes = _git(["remote", "-v"])
    for line in (remotes or "").splitlines():
        if line.startswith("origin\t") and "(fetch)" in line:
            snap["origin_fetch_url"] = line.split()[1]
            break
    if "Kopano-Labs" in snap["origin_fetch_url"]:
        snap["warnings"].append(
            "origin is Kopano-Labs — add a personal fork remote if you need profile-visible receipts."
        )
    return snap


def _run_script(script: str, args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(_SCRIPTS / script), *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    tail = (proc.stdout or proc.stderr or "").strip()
    if len(tail) > 400:
        tail = "…" + tail[-400:]
    return proc.returncode if proc.returncode is not None else 1, tail


def _last_log_line(path: Path) -> dict | None:
    if not path.is_file():
        return None
    for raw in reversed(path.read_text(encoding="utf-8").splitlines()):
        raw = raw.strip()
        if not raw:
            continue
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            continue
    return None


def _doctrine() -> dict:
    scripts = str(_SCRIPTS)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)

    from kc_guard import check_swarm_ack_evidence, check_swarm_doc_hosts  # noqa: WPS433
    from kc_main_brain_roadmap import check_entry_gate  # noqa: WPS433
    from kc_verified_production import DEFAULT_MIN, check_minimum, count_verified  # noqa: WPS433

    verified_n, _ = count_verified()
    prod_ok, prod_msg = check_minimum(int(DEFAULT_MIN))
    roadmap_ok, roadmap_msg = check_entry_gate()
    ack_ok, ack_msg = check_swarm_ack_evidence(_REPO_ROOT)
    hosts_ok, hosts_msg = check_swarm_doc_hosts(_REPO_ROOT)

    return {
        "verified_production": verified_n,
        "production_bar_met": prod_ok,
        "production_bar_message": prod_msg,
        "roadmap_gate_met": roadmap_ok,
        "roadmap_gate_message": roadmap_msg,
        "swarm_ack_met": ack_ok,
        "swarm_ack_message": ack_msg,
        "doc_hosts_ok": hosts_ok,
        "doc_hosts_message": hosts_msg,
        "public_graduation_bar": int(DEFAULT_MIN),
    }


def _agents_inventory() -> dict:
    """Honest agent counts — registry vs orch-runnable vs doctrine-only."""
    registry: dict = {}
    if _REGISTRY.is_file():
        registry = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    agents = registry.get("agents", [])
    seed_path = _REPO_ROOT / "kopano-core" / "config" / "orch_agents.seed.json"
    orch_ids: set[str] = set()
    if seed_path.is_file():
        orch_ids = set(json.loads(seed_path.read_text(encoding="utf-8")).keys())
    orch_excluded = frozenset(
        {"kc", "mirror_warden", "kc_apprentice", "operational_general", "pipeline_drone", "cf_cloud"}
    )
    wit_n = 0
    if _WIT_MANIFEST.is_file():
        wit_n = int(json.loads(_WIT_MANIFEST.read_text(encoding="utf-8")).get("task_count", 0))
    return {
        "registry_total": len(agents),
        "orch_runnable": len(orch_ids),
        "swarm_slots": sum(1 for a in agents if a.get("swarm_slot")),
        "mesh": sum(1 for a in agents if a.get("role") == "mesh"),
        "triad_ids": ["cassy", "cassey", "kc"],
        "wit_tasks": wit_n,
        "operator_cf": "cf_cloud",
        "orch_seed_path": "kopano-core/config/orch_agents.seed.json",
        "registry_path": "docs/swarm-ops/agents/SWARM_AGENTS.json",
        "cf_comms_fragment": "docs/swarm-ops/comms-log-fragments/CF_AGENT_ACTIVATION.md",
        "cf_activate_command": "python scripts/kc_cf_comms_activate.py --prepend-vault",
        "external_kimi_300": "manual-execution-required",
        "agents": [
            {
                "id": a.get("id"),
                "display_name": a.get("display_name"),
                "role": a.get("role"),
                "swarm_slot": a.get("swarm_slot"),
                "orch_runnable": a.get("id") in orch_ids,
                "doctrine_only": a.get("id") in orch_excluded,
            }
            for a in agents
        ],
    }


def _cassy_role() -> dict:
    """Cassy = lead student on apprenticeship; not a corporate swarm-role ceiling."""
    registry: dict = {}
    if _REGISTRY.is_file():
        registry = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    profile: dict = {}
    if _PROFILE.is_file():
        profile = json.loads(_PROFILE.read_text(encoding="utf-8"))

    cassy_agent = next((a for a in registry.get("agents", []) if a.get("id") == "cassy"), {})
    apprenticeship = cassy_agent.get("apprenticeship") or {}
    wit_title = ""
    if _WIT_MANIFEST.is_file():
        wit_title = json.loads(_WIT_MANIFEST.read_text(encoding="utf-8")).get("title", "")

    drill_promoted: int | None = None
    try:
        from kopano.kc_training_store import KcTrainingStore

        counts = KcTrainingStore().status_payload().get("status_counts", {})
        drill_promoted = int(counts.get("promoted", 0))
    except OSError:
        drill_promoted = None

    return {
        "id": "cassy",
        "display_name": cassy_agent.get("display_name", "Cassy"),
        "role": cassy_agent.get("role", "student_primary"),
        "studio_lane": cassy_agent.get("studio_lane", "kopano"),
        "lead_student": registry.get("lead_student") or profile.get("lead_student", "cassy"),
        "teacher": registry.get("teacher") or profile.get("teacher", "cassey"),
        "brain": registry.get("brain") or profile.get("brain", "kc"),
        "mission": apprenticeship.get("mission") or registry.get("servitude", ""),
        "wit_band": wit_title or apprenticeship.get("wit_band", ""),
        "wit_manifest": "docs/swarm-ops/agents/cassy_wit_25.json",
        "drill_manifest": apprenticeship.get("manifest", "docs/swarm-ops/apprenticeship/kc_apprenticeship_250.json"),
        "drill_promoted_local": drill_promoted,
        "drill_is_not_graduation": True,
        "console_role": (
            "Cassy is the lead student: she submits bounded student_response rows; "
            "Cassey (teacher) writes teacher_review; KC stores memory — KC does not chat. "
            "Mesh/swarm workers bind apprenticeship.student=cassy; corporate slot names are not her ceiling."
        ),
        "steward_commands": [
            "python scripts/kc_cassy_activate.py --seed-wit",
            "python scripts/kc_cassy_wit_steward.py --promote",
            "python scripts/kc_apprenticeship_steward.py --promote",
        ],
    }


def gather_status() -> dict:
    validate_code, validate_tail = _run_script("kc_log_append.py", ["validate"])
    proof_code, proof_tail = _run_script("kc_log_append.py", ["proof-check"])
    guard_code, guard_tail = _run_script(
        "kc_guard.py",
        ["all", "--require-verified-production", "10", "--require-roadmap-gate"],
    )

    doctrine = _doctrine()
    proof_bar_pass = validate_code == 0 and proof_code == 0 and guard_code == 0

    gaps: list[str] = []
    if validate_code != 0:
        gaps.append("JSONL validate failed — run python scripts/kc_log_append.py validate")
    if proof_code != 0:
        gaps.append("proof-check failed — run python scripts/kc_log_append.py proof-check")
    if not doctrine["production_bar_met"]:
        gaps.append(doctrine["production_bar_message"])
    if not doctrine["roadmap_gate_met"]:
        gaps.append(doctrine["roadmap_gate_message"])
    if not doctrine["swarm_ack_met"]:
        gaps.append("External swarm ACK missing (manual-execution-required — no fake kimi_ack)")

    return {
        "schema": "kc_swarm_console_status_v1",
        "servitude_triad": "docs/swarm-ops/SERVITUDE_TRIAD.md",
        "wireframe_spec": "docs/swarm-ops/KC_SWARM_CONSOLE_WIREFRAME_SPEC.md",
        "persona_route": "Cassy (student) → Cassey (teacher) · KC (brain ledger)",
        "composer_hint": (
            "Student Cassy: one bounded turn — read first, submit evidence, no owner-proof theater. "
            "Teacher Cassey routes depth; KC stores teacher_review only."
        ),
        "cassy": _cassy_role(),
        "agents": _agents_inventory(),
        "context_host": "https://context.kopanolabs.com",
        "git": _git_snapshot(),
        "checks": {
            "jsonl_validate_ok": validate_code == 0,
            "jsonl_validate_exit": validate_code,
            "jsonl_validate_tail": validate_tail,
            "proof_check_ok": proof_code == 0,
            "proof_check_exit": proof_code,
            "proof_check_tail": proof_tail,
            "guard_all_ok": guard_code == 0,
            "guard_all_exit": guard_code,
            "guard_all_tail": guard_tail,
        },
        "doctrine": doctrine,
        "proof_bar_pass": proof_bar_pass,
        "proof_gaps": gaps,
        "logs": {
            "review_log": str(_REVIEW_LOG.relative_to(_REPO_ROOT)),
            "main_brain_log": str(_MAIN_BRAIN_LOG.relative_to(_REPO_ROOT)),
            "last_review": _last_log_line(_REVIEW_LOG),
            "last_main_brain": _last_log_line(_MAIN_BRAIN_LOG),
        },
        "ci": {
            "workflow": _CI_WORKFLOW,
            "actions_url": _GITHUB_ACTIONS,
            "compare_url": _COMPARE_BRANCH,
            "job_name": "swarm-jsonl",
            "guard_command": (
                "python scripts/kc_guard.py all "
                "--require-verified-production 10 --require-roadmap-gate"
            ),
        },
        "cli": [
            "python scripts/git_sync_monitor.py",
            "python scripts/kc_log_append.py validate",
            "python scripts/kc_log_append.py proof-check",
            "python scripts/kc_guard.py all --require-verified-production 10 --require-roadmap-gate",
            "python scripts/kc_production_verify_run.py",
            "python scripts/kc_cassy_wit_steward.py --promote",
        ],
    }


@router.get("/swarm-console/status")
def get_swarm_console_status() -> dict:
    return gather_status()
