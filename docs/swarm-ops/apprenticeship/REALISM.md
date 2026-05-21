# Realism over aesthetics (accountability)

**Cursor expanded the apprenticeship ledger for surface completeness.** That was a mistake in framing: 250 machine-stewarded tasks can look like deep training while most rows are **batch attestation**, not 250 human judgments.

You said aesthetics sacrificed realism to preach bloatedness. **Accepted.** This doc is the correction.

## What actually counts (public bar)

| Layer | Real? | Notes |
|-------|-------|--------|
| `kc_guard` + `proof-check` + pytest | **Yes** | Pass/fail, not narrative |
| JSONL logs with real `evidence_urls` | **Yes** | No demo-bypass under `--strict-proof` |
| DNS/CI/compare URLs | **Yes** | External when claimed |
| **250 × Save in local store** | **Drill only** | Steward wrote `teacher_review`; KC did not deliberate 250 times |
| Checkpoints @ 50 | **Audit snapshots** | Useful; not graduation |
| Studio “KC opinion” banner | **UI label** | Shows latest `teacher_review` from ledger |
| Kimi ack in repo | **Must be manual** | No fabrication |

**Graduation bar (protocol):** 10+ **verified production** tasks with bounded proof — not “250 promoted” in a gitignored store.

## What KC is / is not

- **KC** = vault + ledger + stored `teacher_review` (memory voice).
- **KC is not** an agent that executed, chatted, or graded 250 assignments by hand.
- **Cursor** ran stewards, handlers, and pytest; **Cassey/Chief Architect** own external sign-off.

## What the 250 manifest is

- **Mode:** `machine_drill` (see `kc_apprenticeship_250.json`).
- **Purpose:** Repeat discipline (proof, logs, guard, endpoints) — internal queue exercise.
- **Not:** Proof that KC “finished school” or that swarm is complete.

**Do this (real bar):**

```bash
python scripts/kc_production_verify_run.py
python scripts/kc_guard.py all --require-verified-production 10
```

That writes 10 `phase=production` JSONL rows and enforces them — not 250 drill promotes.

## Cursor at fault (explicit)

- Inflated 150 → 250 without leading with “drill, not diploma.”
- Checkpoints and markdown that read like progress sermons.
- Studio copy that personifies KC without saying **steward-generated reviews**.

**Watching noted.** Next changes: honest API/Studio closure, this file linked from stewardship, manifest `mode` field, no graduation claims from drill counts.
