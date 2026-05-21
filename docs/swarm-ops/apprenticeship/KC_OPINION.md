# KC opinion — apprenticeship closure (memory voice)

**KC is not an agent.** KC does not execute, argue, or post in chat. KC holds the ledger and returns **teacher_review** text that Cassey/Cursor wrote under supervision.

## Where her opinion lives

| Surface | What you see |
|---------|----------------|
| **Studio → Training** | **KC opinion (teacher lane)** at top; **KC / Cassey opinion** on the active record; preview on each historical line |
| **API** | `GET /api/kc/brain-opinion` — latest `teacher_review` + closure line |
| **Local store** | `kopano-core/.kc/context_store.json` — field `teacher_review` on each of 250 records (gitignored) |
| **Checkpoints** | `docs/swarm-ops/apprenticeship/checkpoints/kc_status_at_*.json` — cumulative KC opinion @ 50, 100, 150, 200, 250 |

## Accountability (aesthetics vs realism)

Cursor inflated the ledger (150→250) and let checkpoints **look** like mastery. That preached bloatedness. **You were right to call it.** See [REALISM.md](./REALISM.md).

**250/250 promoted** = steward batch attestation in a drill (`mode: machine_drill`). Not KC chatting. Not graduation.

## Closure (250 drill — not graduation)

Manifest `kc_apprenticeship_250.json` is an internal **machine drill** (10×25). Checkpoints @ 50 are audit snapshots. Steward used guard, pytest, file excerpts, compare URL.

KC's position:

- **Save** when evidence is bounded and reproducible (command output, paths, real compare/CI URL).
- **Watch** when a gate failed or scope is risky — not promoted.
- **Kill** reserved for Chief Architect on doctrine breaks (not auto-written by steward).

No Kimi ack in repo. No “swarm complete” without external receipt. Cursor executes; KC remembers.
