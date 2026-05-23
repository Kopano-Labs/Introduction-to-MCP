#!/usr/bin/env python3
"""Bootstrap mesh + swarm agents from SWARM_AGENTS.json (Cassy on apprenticeship)."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
SEED_OUT = REPO_ROOT / "kopano-core" / "config" / "orch_agents.seed.json"
DEFAULT_ORCH = Path.home() / ".orch" / "agents.json"


def _persona(agent: dict) -> str:
    role = agent.get("role", "mesh")
    app = agent.get("apprenticeship") or {}
    student = app.get("student", "cassy")
    teacher = app.get("teacher", "cassey")
    base = agent.get("display_name", agent["id"])
    if role == "teacher":
        return (
            f"You are {base}, teacher lane. Guide student {student} on KC apprenticeship. "
            "Servitude Triad: Grit+Realism+Aesthetics together. Never hold the student back."
        )
    if role == "student_primary":
        return (
            f"You are {base}, lead student. Teacher {teacher}; KC brain stores teacher_review only. "
            "Women in Tech diaspora mission. Bounded proof only."
        )
    if role == "brain":
        return "KC brain ledger — do not roleplay live chat; opinions are stored teacher_review rows."
    return (
        f"You are {base} ({role}). Student apprenticeship binds to {student}; teacher {teacher}. "
        "Execute with receipts; no fake swarm ACK."
    )


def registry_to_orch_agents(registry: dict) -> dict:
    out: dict = {}
    for agent in registry.get("agents", []):
        aid = agent["id"]
        if aid in {"kc", "mirror_warden", "kc_apprentice", "operational_general", "pipeline_drone", "cf_cloud"}:
            continue
        provider = agent.get("provider", "openai")
        model = {
            "anthropic": "claude-3-5-sonnet-20241022",
            "google": "gemini/gemini-2.0-flash",
            "xai": "xai/grok-beta",
            "microsoft": "gpt-4o",
            "openai": "gpt-4o",
        }.get(provider, "gpt-4o")
        out[aid] = {
            "provider": provider if provider != "microsoft" else "openai",
            "model": model,
            "api_key": "ENV",
            "persona": _persona(agent),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help=f"Merge seed into {DEFAULT_ORCH}")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    seed = registry_to_orch_agents(registry)
    SEED_OUT.parent.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        print(json.dumps({"seed_path": str(SEED_OUT), "agents": list(seed.keys())}, indent=2))
        return 0
    SEED_OUT.write_text(json.dumps(seed, indent=2), encoding="utf-8")
    print(f"wrote {SEED_OUT} ({len(seed)} agents)")

    if args.install:
        DEFAULT_ORCH.parent.mkdir(parents=True, exist_ok=True)
        existing: dict = {}
        if DEFAULT_ORCH.exists():
            existing = json.loads(DEFAULT_ORCH.read_text(encoding="utf-8"))
        merged = {**existing, **seed}
        backup = DEFAULT_ORCH.with_suffix(".json.bak")
        if DEFAULT_ORCH.exists():
            shutil.copy2(DEFAULT_ORCH, backup)
        DEFAULT_ORCH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
        print(f"installed {DEFAULT_ORCH} (backup {backup.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
