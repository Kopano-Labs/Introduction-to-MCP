# Main Brain + vault audit (2026-05-19)

**Canonical machine logs:** `docs/swarm-ops/logs/` (tracked, CI-gated)  
**Vault mirror (Obsidian):** `Schematics/04-Updates/logs/` (gitignored with vault; sync via `kc_sync_vault_logs.py`)  
**KC store (teacher_review):** `kopano-core/.kc/context_store.json` (gitignored; 150 tasks)

## Gaps found and fixed

| Gap | Fix |
|-----|-----|
| Schematics JSONL stale (bootstrap only) | `python scripts/kc_sync_vault_logs.py` copies canonical logs after each append |
| `kc_apprenticeship_activate.py` used invalid `--note` / `--scope` on `mainbrain` | Uses `--kind apprenticeship_activate` + evidence URLs |
| Main Brain last row missing `evidence_urls` | Append `mainbrain` / `review` rows with compare URL + Actions |
| 948 tracked Schematics paths dirtied `git status` | `git rm --cached Schematics/` @ `35949aa` |
| Kimi ack | Still **manual-execution-required** — no fabricated `kimi_ack` |

## Apprenticeship state (local store)

- **150** tasks in manifest `kc_apprenticeship_150.json`
- **146** `promoted`, **4** `reviewed` (Watch — not promoted)
- KC opinion = `teacher_review` on each record (Save / Watch); not live chat

## Commands (end-to-end)

```bash
python scripts/kc_sync_vault_logs.py
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check
python scripts/kc_guard.py all
python -m pytest tests/test_kc_log_append.py tests/test_kc_guard.py tests/test_kc_apprenticeship.py tests/test_kc_training_api.py -q
```

## Doctrine

- **Cursor** executes and appends receipts.
- **KC** holds ledger + `teacher_review` text.
- **Chief Architect** graduates; automation does not replace Kimi external ack.
