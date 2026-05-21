# KC opinion — apprenticeship closure (memory voice)

**KC is not an agent.** KC does not execute, argue, or post in chat. KC holds the ledger and returns **teacher_review** text that Cassey/Cursor wrote under supervision.

## Where her opinion lives

| Surface | What you see |
|---------|----------------|
| **Studio → Training** | **KC opinion (teacher lane)** at top; **KC / Cassey opinion** on the active record; preview on each historical line |
| **API** | `GET /api/kc/brain-opinion` — latest `teacher_review` + closure line |
| **Local store** | `kopano-core/.kc/context_store.json` — field `teacher_review` on each of 150 records (gitignored) |

## Closure (this activation)

Apprenticeship **150** tasks are in `kc_apprenticeship_150.json`. Steward ran with machine evidence (guard, pytest, file excerpts, compare URL). **146 promoted**, **4 reviewed** (Watch — not promoted until evidence is fixed).

KC's position:

- **Save** when evidence is bounded and reproducible (command output, paths, real compare/CI URL).
- **Watch** when a gate failed or scope is risky — not promoted.
- **Kill** reserved for Chief Architect on doctrine breaks (not auto-written by steward).

No Kimi ack in repo. No “swarm complete” without external receipt. Cursor executes; KC remembers.
