"""Generic stewardship handlers for apprenticeship extension tasks (16–25 per phase)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

Handler = Callable[[], tuple[str, str]]

PHASE_ANCHOR_FILES: dict[int, str] = {
    1: "docs/swarm-ops/SWARM_OPERATIONS.md",
    2: "docs/swarm-ops/logs/README.md",
    3: "scripts/kc_guard.py",
    4: "kopano-core/kopano/kc_training_api.py",
    5: "docs/swarm-ops/VERIFIED_ENDPOINTS.md",
    6: ".github/workflows/swarm-proof.yml",
    7: "docs/swarm-ops/apprenticeship/STEWARDSHIP.md",
    8: "kopano-core/kopano/labs_api.py",
    9: "docs/swarm-ops/apprenticeship/KC_OPINION.md",
    10: "DEMO_DAY_RUNBOOK.md",
}


def fill_generic_handlers(
    hmap: dict[str, Handler],
    manifest_tasks: list[dict[str, Any]],
    *,
    root: Path,
    sha: str,
    h_file: Callable[[str, str], tuple[str, str]],
    h_cmd: Callable[[str, list[str]], tuple[str, str]],
    store_path: Path,
) -> None:
    """Add handlers for manifest codes not already in hmap (extension band)."""
    py = sys.executable

    def h_sync_vault() -> tuple[str, str]:
        return h_cmd(
            "kc_sync_vault_logs",
            [py, "scripts/kc_sync_vault_logs.py"],
        )

    def h_store_counts() -> tuple[str, str]:
        import json

        if not store_path.exists():
            return f"store missing: {store_path}", "Watch"
        payload = json.loads(store_path.read_text(encoding="utf-8"))
        counts: dict[str, int] = {}
        for rec in payload.get("records", {}).values():
            st = rec.get("status", "assigned")
            counts[st] = counts.get(st, 0) + 1
        return f"status_counts={counts}\nsha={sha}", "Save"

    for task in manifest_tasks:
        code = task["code"]
        if code in hmap:
            continue
        phase = int(task["phase"])
        task_num = int(code.split("-")[1][2:])
        anchor = PHASE_ANCHOR_FILES.get(phase, "docs/swarm-ops/NAVIGATION.md")
        title = task["title"]

        if task_num == 16:
            hmap[code] = h_sync_vault
        elif task_num == 17:
            hmap[code] = lambda a=anchor: h_file(
                "docs/swarm-ops/apprenticeship/KC_OPINION.md",
                "KC opinion = teacher_review on records.",
            )
        elif task_num == 18:
            hmap[code] = lambda: h_cmd(
                "checkpoint policy",
                [
                    py,
                    "-c",
                    "import json; p='docs/swarm-ops/apprenticeship/kc_apprenticeship_250.json'; "
                    "d=json.load(open(p)); print('checkpoint_every', d.get('checkpoint_every', 50))",
                ],
            )
        elif task_num == 19:
            hmap[code] = lambda: h_cmd(
                "kc_guard validate",
                [py, "scripts/kc_guard.py", "validate"],
            )
        elif task_num == 20:
            hmap[code] = h_store_counts
        elif task_num == 21:
            hmap[code] = lambda: h_cmd(
                "review append validate",
                [py, "scripts/kc_log_append.py", "validate"],
            )
        elif task_num == 22:
            hmap[code] = lambda: h_file("docs/swarm-ops/NAVIGATION.md", "Navigation links.")
        elif task_num == 23:
            hmap[code] = lambda: h_cmd(
                "git schematics tracked count",
                [py, "-c", "import subprocess; r=subprocess.run(['git','ls-files','Schematics'],"
                "capture_output=True,text=True); print(len(r.stdout.splitlines()))"],
            )
        elif task_num == 24:
            hmap[code] = lambda: h_file(
                "docs/swarm-ops/apprenticeship/progress.json",
                "Progress ledger status_counts.",
            )
        elif task_num == 25:
            hmap[code] = lambda p=phase: h_cmd(
                f"phase {p} extension closure",
                [
                    py,
                    "-m",
                    "pytest",
                    "tests/test_kc_log_append.py",
                    "tests/test_kc_guard.py",
                    "-q",
                ],
            )
        else:
            note = f"{title}\nphase={phase} anchor={anchor}\nsha={sha}"
            teacher = "Save — bounded extension evidence."
            hmap[code] = lambda n=note, t=teacher: (n, t)
