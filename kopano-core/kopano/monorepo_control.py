"""Monorepo execution surface for Super God Mode (whole PWA, not console-only)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"

# script file, args, requires_confirm
SCRIPT_ACTIONS: dict[str, tuple[str, list[str], bool]] = {
    "jsonl_validate": ("kc_log_append.py", ["validate"], False),
    "proof_check": ("kc_log_append.py", ["proof-check"], False),
    "guard_all": (
        "kc_guard.py",
        ["all", "--require-verified-production", "10", "--require-roadmap-gate"],
        False,
    ),
    "production_verify": ("kc_production_verify_run.py", [], False),
    "git_sync_monitor": ("git_sync_monitor.py", [], False),
    "swarm_bootstrap": ("kc_swarm_agents_bootstrap.py", [], False),
    "cassy_activate_seed": ("kc_cassy_activate.py", ["--seed-wit"], True),
    "cassy_wit_promote": ("kc_cassy_wit_steward.py", ["--promote"], True),
    "apprenticeship_promote": ("kc_apprenticeship_steward.py", ["--promote"], True),
    "cf_comms_activate": ("kc_cf_comms_activate.py", ["--prepend-vault"], True),
    "phu_populate_main_brain": ("kc_phu_populate_main_brain.py", [], True),
    "phu_reattach_subbrains": ("kc_phu_reattach_subbrains.py", [], False),
}

GIT_ACTIONS: dict[str, list[str]] = {
    "git_status": ["status", "-sb"],
    "git_fetch": ["fetch", "origin"],
    "git_pull_ff": ["pull", "--ff-only"],
    "git_push": ["push"],
}

CASSY_ACTION_IDS = frozenset(
    {
        "cassy_activate_seed",
        "cassy_wit_promote",
        "apprenticeship_promote",
        "swarm_bootstrap",
        "phu_populate_main_brain",
        "phu_reattach_subbrains",
    }
)


def git_run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *cmd],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    out = (proc.stdout or proc.stderr or "").strip()
    return proc.returncode, out


def git_snapshot() -> dict:
    snap: dict = {
        "repo_root": str(REPO_ROOT),
        "branch": "(unknown)",
        "head_sha": "",
        "upstream": None,
        "ahead": 0,
        "behind": 0,
        "origin_fetch_url": "",
        "warnings": [],
    }
    _, branch = git_run(["branch", "--show-current"])
    snap["branch"] = branch or "(detached)"
    _, head = git_run(["rev-parse", "HEAD"])
    snap["head_sha"] = head[:12] if head else ""
    _, upstream = git_run(["rev-parse", "--abbrev-ref", f"{snap['branch']}@{{upstream}}"])
    if upstream:
        snap["upstream"] = upstream
        code, cnt = git_run(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
        if code == 0 and "\t" in cnt:
            left, right = cnt.split("\t", 1)
            snap["ahead"] = int(left)
            snap["behind"] = int(right)
            if snap["ahead"]:
                snap["warnings"].append(
                    f"{snap['ahead']} commit(s) ahead of {upstream} — push for remote receipts."
                )
    else:
        snap["warnings"].append("No upstream configured — git push -u origin <branch> once.")

    _, remotes = git_run(["remote", "-v"])
    for line in (remotes or "").splitlines():
        if line.startswith("origin\t") and "(fetch)" in line:
            snap["origin_fetch_url"] = line.split()[1]
            break
    return snap


def run_script(script: str, args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    tail = (proc.stdout or proc.stderr or "").strip()
    if len(tail) > 800:
        tail = "…" + tail[-800:]
    return proc.returncode if proc.returncode is not None else 1, tail


def execute_script_action(action: str, *, confirm: bool = False) -> dict:
    spec = SCRIPT_ACTIONS.get(action)
    if not spec:
        raise ValueError(f"Unknown action: {action}")
    script, args, needs_confirm = spec
    if needs_confirm and not confirm:
        raise ValueError(f"Action '{action}' requires confirm=true.")
    code, tail = run_script(script, args)
    return {
        "action": action,
        "lane": "cassy" if action in CASSY_ACTION_IDS else "monorepo",
        "exit_code": code,
        "ok": code == 0,
        "tail": tail,
    }


def execute_git_action(action: str, *, confirm: bool = False) -> dict:
    git_args = GIT_ACTIONS.get(action)
    if not git_args:
        raise ValueError(f"Unknown git action: {action}")
    if action == "git_push" and not confirm:
        raise ValueError("git_push requires confirm=true.")
    code, out = git_run(git_args)
    return {
        "action": action,
        "lane": "git",
        "exit_code": code,
        "ok": code == 0,
        "output": out,
        "git": git_snapshot(),
    }


def capabilities_payload() -> dict:
    return {
        "schema": "kc_god_capabilities_v1",
        "persona": "Cassy (lead student) · Cassey (teacher) · KC (ledger)",
        "repo_root": str(REPO_ROOT),
        "script_actions": {
            k: {"requires_confirm": v[2], "cassy_lane": k in CASSY_ACTION_IDS}
            for k, v in SCRIPT_ACTIONS.items()
        },
        "git_actions": list(GIT_ACTIONS.keys()),
    }
