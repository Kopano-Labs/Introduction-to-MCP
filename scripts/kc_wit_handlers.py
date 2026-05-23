"""Stewardship handlers for Cassy Women-in-Tech band (phase 11)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

Handler = Callable[[], tuple[str, str]]


def wit_handlers(root: Path, sha: str, store_path: Path) -> dict[str, Handler]:
    py = sys.executable
    compare = (
        "https://github.com/Kopano-Labs/Introduction-to-MCP/"
        "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
    )

    def h_note(note: str, teacher: str = "Save") -> Handler:
        return lambda: (f"{note}\nsha={sha}", teacher)

    def h_cmd(label: str, cmd: list[str]) -> tuple[str, str]:
        import subprocess

        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=120)
        out = (proc.stdout or proc.stderr or "")[:800]
        verdict = "Save" if proc.returncode == 0 else "Watch"
        return f"{label} exit={proc.returncode}\n{out}", f"{verdict} — Cassy WIT steward"

    def h_file(rel: str, note: str) -> Handler:
        p = root / rel
        if not p.is_file():
            return lambda: (f"missing {rel}", "Watch")
        return lambda: (f"{note}\npath={rel}\nbytes={p.stat().st_size}", "Save — Cassy WIT steward")

    return {
        "WIT-1101": h_note("WIT metrics: bounded proof rows + verified production count."),
        "WIT-1102": h_file("docs/swarm-ops/agents/SWARM_AGENTS.json", "Cassy lead_student; corporate roles not a ceiling."),
        "WIT-1103": h_file("docs/swarm-ops/SERVITUDE_TRIAD.md", "Triad unified: Grit+Realism+Aesthetics."),
        "WIT-1104": lambda: h_cmd("roadmap gate", [py, "scripts/kc_main_brain_roadmap.py", "gate"]),
        "WIT-1105": lambda: h_cmd("seed before", [py, "scripts/kc_main_brain_roadmap.py", "seed", "--phase", "before"]),
        "WIT-1106": lambda: h_cmd(
            "black mask receipt",
            [py, "scripts/kc_main_brain_roadmap.py", "receipt", "--milestone", "black_mask_v0_5"],
        ),
        "WIT-1107": h_file("docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md", "Kimi manual-execution-required."),
        "WIT-1108": lambda: h_cmd(
            "blackmass v2",
            [py, "scripts/kc_main_brain_roadmap.py", "receipt", "--milestone", "blackmass_v2_0"],
        ),
        "WIT-1109": h_file("docs/swarm-ops/agents/SWARM_AGENTS.json", "Mesh agents bind student=cassy."),
        "WIT-1110": lambda: h_cmd(
            "brain-opinion pytest",
            [py, "-m", "pytest", "tests/test_kc_training_api.py", "-q"],
        ),
        "WIT-1111": h_note("hold_back_student=false on cassey agent — Cassy not held back."),
        "WIT-1112": h_note("Cassey teacher turn: Console guides Cassy apprenticeship."),
        "WIT-1113": h_file("docs/swarm-ops/apprenticeship/KC_OPINION.md", "KC stores teacher_review; no live chat."),
        "WIT-1114": lambda: h_cmd(
            "guard production+roadmap",
            [
                py,
                "scripts/kc_guard.py",
                "all",
                "--require-verified-production",
                "10",
                "--require-roadmap-gate",
            ],
        ),
        "WIT-1115": lambda: h_cmd("seed after", [py, "scripts/kc_main_brain_roadmap.py", "seed", "--phase", "after"]),
        "WIT-1116": lambda: h_cmd("vault sync", [py, "scripts/kc_sync_vault_logs.py"]),
        "WIT-1117": h_note(f"CI compare: {compare}"),
        "WIT-1118": h_note("Forensic sociology: one claim, one JSONL receipt."),
        "WIT-1119": h_note("MAO loop: inspect → adapt → receipt."),
        "WIT-1120": h_note("Anti-bloat: checkpoint default 0; drill != diploma."),
        "WIT-1121": h_file("docs/swarm-ops/MAIN_BRAIN_ROADMAP.json", "Roadmap ties README phases to gate."),
        "WIT-1122": lambda: h_cmd("agents bootstrap", [py, "scripts/kc_swarm_agents_bootstrap.py", "--dry-run"]),
        "WIT-1123": h_file("docs/swarm-ops/apprenticeship/REALISM.md", "Drill labeled; verified production is bar."),
        "WIT-1124": lambda: (
            (
                json.dumps(
                    {
                        "lead": "cassy",
                        "agents_with_apprenticeship": sum(
                            1
                            for _ in json.loads(
                                (root / "docs/swarm-ops/agents/SWARM_AGENTS.json").read_text(encoding="utf-8")
                            )["agents"]
                            if _.get("apprenticeship")
                        ),
                    }
                ),
                "Save — Cassy WIT steward",
            )
            if (root / "docs/swarm-ops/agents/SWARM_AGENTS.json").is_file()
            else ("SWARM_AGENTS missing", "Watch")
        ),
        "WIT-1125": lambda: h_cmd(
            "phase 11 closure",
            [
                py,
                "-m",
                "pytest",
                "tests/test_kc_main_brain_roadmap.py",
                "tests/test_swarm_agents_api.py",
                "-q",
            ],
        ),
    }
