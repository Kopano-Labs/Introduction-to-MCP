# KC opinion — apprenticeship closure (memory voice)

**KC is not an agent.** KC does not execute, argue, or post in chat. KC holds the ledger and returns **teacher_review** text that Cassey/Cursor wrote under supervision.

## Where her opinion lives

| Surface | What you see |
|---------|----------------|
| **Studio → Training** | **KC opinion (teacher lane)** at top; **KC / Cassey opinion** on the active record; preview on each historical line |
| **API** | `GET /api/kc/brain-opinion` — latest `teacher_review` + closure line |
| **Local store** | `kopano-core/.kc/context_store.json` — field `teacher_review` on each of 250 records (gitignored) |
| **Checkpoints** | `docs/swarm-ops/apprenticeship/checkpoints/kc_status_at_*.json` — cumulative KC opinion @ 50, 100, 150, 200, 250 |

## Closure (250 activation)

Apprenticeship **250** tasks are in `kc_apprenticeship_250.json` (10×25; checkpoint every 50). Steward runs with machine evidence (guard, pytest, file excerpts, compare URL). **250/250 promoted** after Watch repair on guard/proof flakes.

KC's position:

- **Save** when evidence is bounded and reproducible (command output, paths, real compare/CI URL).
- **Watch** when a gate failed or scope is risky — not promoted.
- **Kill** reserved for Chief Architect on doctrine breaks (not auto-written by steward).

No Kimi ack in repo. No “swarm complete” without external receipt. Cursor executes; KC remembers.
