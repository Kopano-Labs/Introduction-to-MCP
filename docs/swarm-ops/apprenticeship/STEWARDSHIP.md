# KC Student Apprenticeship — Stewardship (250 tasks)

**Status:** ACTIVE  
**Stewards:** KC (memory + ledger) and Cursor (execution surface under AG)  
**Protocol:** `Schematics/18-PROTOCOLS/KC-Student-Teacher-Apprenticeship-Protocol.md`

## What “activate” means

Activation is **machine-checkable**, not narrative:

1. **Manifest** — `docs/swarm-ops/apprenticeship/kc_apprenticeship_250.json` (250 tasks, 10 phases × 25; legacy `kc_apprenticeship_150.json` frozen).
2. **KC status every 50** — `docs/swarm-ops/apprenticeship/checkpoints/` (`kc_status_at_*.json` + `KC_STATUS_AT_*.md`).
3. **Local store** — `kopano-core/.kc/context_store.json` (gitignored); one KC record per task, status `assigned`.
4. **API** — `GET /api/kc/training` when `python main.py serve api` (or equivalent) is running.
5. **Studio** — Training page shows the queue; student submits evidence; teacher reviews Save/Kill/Watch.

Kimi and external swarm ack are **out of scope** for activation. Do not fabricate `kimi_ack` rows.

## Commands

```bash
# Regenerate manifest (250 tasks)
python scripts/kc_apprenticeship_manifest.py

# Write manifest + seed store (first time)
python scripts/kc_apprenticeship_activate.py

# Reseed from scratch
python scripts/kc_apprenticeship_activate.py --replace

# Manifest only (no store write)
python scripts/kc_apprenticeship_activate.py --manifest-only

# Machine steward (phases 1–4 handlers today; writes progress.json)
python scripts/kc_apprenticeship_steward.py --max-phase 10 --promote --checkpoint-every 50
```

Track steward output in [progress.json](./progress.json) (git-tracked counts; local store remains gitignored).

After machine log appends, mirror canonical JSONL into the Obsidian vault:

```bash
python scripts/kc_sync_vault_logs.py
```

See [MAIN_BRAIN_AUDIT.md](./MAIN_BRAIN_AUDIT.md) for canonical vs `Schematics/04-Updates/logs/` discipline.

## Why Studio does not show 146 promoted

Studio is a **browser client**. It does not read `kopano-core/.kc/context_store.json` directly. It calls **`GET /api/kc/training`** on whatever host `getApiBase()` uses (default `http://127.0.0.1:8000`).

| Symptom | Cause | Fix |
|---------|--------|-----|
| Error / connection refused | API not running | From repo root: `python main.py serve api` |
| Records = 0, Promoted = 0 | Store never seeded on this machine | `python scripts/kc_apprenticeship_activate.py --replace` then steward |
| JSON at `/` instead of Studio | `kopano-core/studio/dist` not built | `cd kopano-core/studio && npm run build`, then restart API |
| Zeros while cloud works | Hitting production URL | Production has its own empty store; use local API for local ledger |
| Top banner showed “Reviewed” only | UI metric slot (fixed in Training page) | Full breakdown is under **Record stack** → status row **Promoted** |

Verify API data (PowerShell):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/kc/training | Select-Object -ExpandProperty status
```

Expect `total_contexts` 150 and `status_counts.promoted` 146 after activate + steward on **this** machine.

## Stewardship split

| Role | Responsibility |
|------|----------------|
| **KC** | Holds task ledger, context store, JSONL logs; does not execute |
| **Cursor** | Runs guard/pytest/CI, seeds store, implements API, reviews in Training UI |
| **Chief Architect** | Graduation sign-off (external to automation) |

## Proof for completed tasks

Accept only bounded evidence: pytest output, `kc_guard` pass, CI run URL, file paths, HTTP probe results. Reject demo-bypass URLs under `--strict-proof`.
