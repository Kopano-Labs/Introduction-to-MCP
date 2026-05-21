# KC status checkpoints (every 50 tasks)

**Audit snapshots only** — not graduation. See [REALISM.md](../REALISM.md).

Steward writes machine-readable `teacher_review` counts here when run with `--checkpoint-every 50` (default for the 250-task **machine_drill** manifest).

| Milestone | Files |
|-----------|--------|
| 50 | `kc_status_at_050.json`, `KC_STATUS_AT_050.md` |
| 100 | `kc_status_at_100.json`, `KC_STATUS_AT_100.md` |
| 150 | `kc_status_at_150.json`, `KC_STATUS_AT_150.md` |
| 200 | `kc_status_at_200.json`, `KC_STATUS_AT_200.md` |
| 250 | `kc_status_at_250.json`, `KC_STATUS_AT_250.md` |

**KC does not chat.** Counts are derived from `teacher_review` on each record (`Save` / `Watch` / `Kill`). Studio: `GET /api/kc/brain-opinion` and Training page banner.

```bash
python scripts/kc_apprenticeship_activate.py --replace
python scripts/kc_apprenticeship_steward.py --max-phase 10 --promote --checkpoint-every 50
```
