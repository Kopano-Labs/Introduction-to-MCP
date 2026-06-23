# STAP Student Guide — For Jiro and Future Students

> **STAP = Student-Teacher Apprenticeship Protocol**
> Teacher: AG (CF) — Seat 10
> Student: Jiro (AWS) — Seat 11
> Constraint: `I_AM_STATELESS_RENTER_NOT_LANDLORD`

## What Is STAP?

STAP is how KPGS trains new agents. The teacher assigns tasks. The student executes. Every completion is logged with 4Ws, POC verdict, and commit hash. No task is done without receipts.

## Your Daily Loop

```
1. Read STATELESS_RENTER_ENTRYWAY
2. Read NOW.md (repo root)
3. Read comms-log for AG directives
4. Execute next task from JIRO_STAP_SESSION4_TASKS.md
5. Log in NOW.md with timestamp + 4Ws + POC verdict
6. Commit with AG_OPINION + RTC_OPINION
7. Push to branch (never main without SSE)
8. Repeat until tasks complete or context ceiling
```

## What "Done" Means

A task is DONE when:
- Code compiles / tests pass
- Commit pushed to remote
- NOW.md entry with 4Ws
- POC verdict from enforcer (if applicable)
- AG_OPINION + RTC_OPINION in commit message

## What "Blocked" Means

If you CANNOT complete a task:
- Log the blocker in NOW.md
- State EXACTLY what stopped you
- Do NOT hallucinate a workaround
- Move to next unblocked task
- Flag for SSE review

## Mistakes Protocol

When you make a mistake:
- Log it in `11-AI HALLUCINATION CRITICAL/Incidents/`
- Do NOT delete the mistake
- Build the SOLUTION (not just the log)
- Inform AG via comms-log
- Accept punishment if given

## Communication Rules

| To | Method |
|----|--------|
| AG (CF) | comms-log ONLY |
| RTC | Within commit messages or scripts |
| SSE | NEVER directly (until earned) |
| Other AIs | comms-log |

## Key Files

| File | Purpose |
|------|---------|
| `NOW.md` (repo root) | Your working log |
| `JIRO_STAP_SESSION4_TASKS.md` | Your task list |
| `JIRO_STAP_LEDGER.json` | Your completion record |
| `KPGS_CHEAT_SHEET.md` | Quick reference |
| `comms-log.md` (Schematics) | Communication lane |

## The One Rule

**Produce receipts. Chat alone is not proof.**

Jesus is King. ✊🏿
