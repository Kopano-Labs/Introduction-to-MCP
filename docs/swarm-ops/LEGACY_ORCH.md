# Legacy: Orch → Cassy (product name)

**Orch** was the original internal product name for the Kopano student/agent control plane and mesh seed format. The lead-student rebrand standardizes on **Cassy**:

| Legacy (Orch) | Current (Cassy) |
|---------------|-----------------|
| `kopano-core/config/orch_agents.seed.json` | `kopano-core/config/cassy_agents.seed.json` |
| `~/.orch/agents.json` | `~/.cassy/agents.json` |
| `orch_runnable` / orch-runnable | `cassy_runnable` / Cassy-runnable |
| Labs `orch-code` API | `cassy-code` |
| Studio `.orch-app` | `.cassy-app` |
| `orch_code_lessons` table | `cassy_code_lessons` |

**Do not rename** (different meaning or external systems):

- **Orchestration / orchestrator** — English workflow terms (Kimi Swarm Orchestrator, Main Brain orchestrator receipts).
- **`orchestrator_parity`** — Mirror Warden role in `SWARM_AGENTS.json`.
- **`Schematics/06-Reference/orch-code-implemtation`** — historical folder (pytest `norecursedirs`).
- **`tests/test_cli.py`**, **`tests/test_orch_logging.py`** — legacy `orch.orch` package imports (pre–Kopano Context tree).
- **MongoDB cluster name “Orch”** in `scripts/check_atlas.py` — Atlas infrastructure label.
- **`scripts/reformat_log.md`** — documents the earlier **Orch → Kopano Context** rebrand.

When you see “orch” in old comms-log rows or JSONL history, read it as the predecessor name for the same Cassy mesh seed and Labs surfaces.

**Still legacy in repo (intentional shims):**

- `kopano-core/__main__.py`, `kopano-core/orchestration.py`, `kopano-core/__init__.py` — import paths under `.orch/` package layout from the original tree.
- `tests/test_cli.py`, `tests/test_orch_logging.py` — `orch.orch` package tests.
- `pytest.ini` — `Schematics/06-Reference/orch-code-implemtation` folder name.
- `scripts/reformat_log.py` — documents Orch → Kopano Context rebrand history.
