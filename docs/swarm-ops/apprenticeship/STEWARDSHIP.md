# KC Student Apprenticeship — Stewardship (150 tasks)

**Status:** ACTIVE  
**Stewards:** KC (memory + ledger) and Cursor (execution surface under AG)  
**Protocol:** `Schematics/18-PROTOCOLS/KC-Student-Teacher-Apprenticeship-Protocol.md`

## What “activate” means

Activation is **machine-checkable**, not narrative:

1. **Manifest** — `docs/swarm-ops/apprenticeship/kc_apprenticeship_150.json` (150 tasks, 10 phases × 15).
2. **Local store** — `kopano-core/.kc/context_store.json` (gitignored); one KC record per task, status `assigned`.
3. **API** — `GET /api/kc/training` when `python main.py serve api` (or equivalent) is running.
4. **Studio** — Training page shows the queue; student submits evidence; teacher reviews Save/Kill/Watch.

Kimi and external swarm ack are **out of scope** for activation. Do not fabricate `kimi_ack` rows.

## Commands

```bash
# Regenerate manifest (150 tasks)
python scripts/kc_apprenticeship_manifest.py

# Write manifest + seed store (first time)
python scripts/kc_apprenticeship_activate.py

# Reseed from scratch
python scripts/kc_apprenticeship_activate.py --replace

# Manifest only (no store write)
python scripts/kc_apprenticeship_activate.py --manifest-only
```

## Stewardship split

| Role | Responsibility |
|------|----------------|
| **KC** | Holds task ledger, context store, JSONL logs; does not execute |
| **Cursor** | Runs guard/pytest/CI, seeds store, implements API, reviews in Training UI |
| **Chief Architect** | Graduation sign-off (external to automation) |

## Proof for completed tasks

Accept only bounded evidence: pytest output, `kc_guard` pass, CI run URL, file paths, HTTP probe results. Reject demo-bypass URLs under `--strict-proof`.
