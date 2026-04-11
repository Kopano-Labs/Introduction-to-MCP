---
title: Now
created: 2026-04-09
updated: 2026-04-10
author: Codex
tags:
  - home
  - current-state
  - status
  - demo
priority: critical
status: active
---

# Now

> Canonical one-note snapshot for where Orch stands right now.
> If you only open one note, open this one first.

## Current Phase

- Delivery mode: `demo hardening`
- Stable foundation: Phases 1 through 5 are complete.
- Active buildout: Phase 6, Phase 7, Phase 8, and Phase 9 are active in parallel.
- Practical truth: the demo-ready path right now is the Orch surface, not the full end-to-end KasiLink marketplace story.

## Operating Constitution As Of 2026-04-10

- Lead Developer: `Codex`
- DEV_1: `Germini (Google AI)`
- DEV_2: `Nother`
- DEV_3: `Meither`
- DEV_4: `Cicero`
- These are the standing devs for multi-dev sessions. No new ad-hoc spawn roles are the default vault model.
- Lead may rotate between `Codex`, `Claude`, or `Codex + Claude`.
- Lead target is `60% management / 40% coding`.
- Every task starts with a dev-progress check, a live diff check, and a [comms-log](../04-Updates/comms-log.md) check.
- All current sessions count as `pre-sessions` and training data for Orch.
- Token-saving mode is mandatory outside Plan Mode and outside Lead-only sessions with Master.
- If truth is not present in the vault or official sources, ask Master instead of guessing.

## Current Reality As Of 2026-04-09

| Area | State | Truth |
|------|-------|-------|
| Orch API + GUI | PASS | `tests/test_labs_api.py` passes, `npm run build` in `orch/gui` passes, compile checks pass, and `/api/labs/microsoft-readiness` returns live status. |
| Orch-only demo route | PASS | Public and admin rehearsal paths were locked and passed on `2026-04-09`. |
| Microsoft readiness | COMPLETE | Local tooling is installed, Azure infrastructure is provisioned, telemetry is flowing, and readiness check is `6/6` green. |
| Full KasiLink story | PARTIAL | Wider buyer story still depends on external auth, data, and integration blockers. |
| Vault organization | IN PROGRESS | Schematics is the canonical Obsidian layer; root docs are now being indexed instead of moved casually. |
| Training corpus | ACTIVE | Human, AI, session, hallucination, and Orch progression notes are being consolidated into one second-brain system. |

## Demo Day Position

- Demo hub: [Microsoft Demo Day!](../Microsoft%20Demo%20Day!/index.md)
- Safe live route: [Orch Demo Script - 2026-04-09](../Microsoft%20Demo%20Day!/Orch%20Demo%20Script%20-%202026-04-09.md)
- Countdown and ownership: [Demo Countdown - April 8-15, 2026](../Microsoft%20Demo%20Day!/Demo%20Countdown%20-%20April%208-15,%202026.md)
- UI verification detail: [Orch Demo Task List - 2026-04-08](../Microsoft%20Demo%20Day!/Orch%20Demo%20Task%20List%20-%202026-04-08.md)
- Owner checklist: [Owner Must Handle - Microsoft Demo Day](../Microsoft%20Demo%20Day!/Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)
- Phase and capability truth: [Project Status](../04-Updates/Project%20Status.md)

## Biggest Open Blockers

- valid Clerk keys for the wider authenticated rehearsal
- Atlas allowlist and live Mongo reachability
- `whatsapp_bridge_configured: false` for the full KasiLink narrative
- reward/referral is documentation-only in this workspace and is `NO-GO` for the live demo script until code exists
- product polish: copy tightening, youth-fit research summary, and reconnecting the Orch-only route to the bigger KasiLink story

## New Control Systems

- [Schematics Root Index](../index.md)
- [07-Sessions By Day](../07-Sessions%20By%20Day/index.md)
- [08-IDEAS AT BIRTH](../08-IDEA'S%20AT%20BIRTH/index.md)
- [09-ORCH PROGRESSION](../09-ORCH%20PROGRESSION/index.md)
- [10-SESSION IMPROVEMENTS](../10-SESSION%20IMPROVEMENTS/index.md)
- [11-AI HALLUCINATION - CRITICAL](../11-AI%20HALLUCINATION%20-%20CRITICAL/index.md)
- [12-PLAN MODE SESSIONS](../12-PLAN%20MODE%20SESSIONS/index.md)
- [Orch Train Logs](../05-Training/Orch%20Train%20Logs/index.md)

## Open These In Order

1. [Project Status](../04-Updates/Project%20Status.md)
2. [Microsoft Demo Day!](../Microsoft%20Demo%20Day!/index.md)
3. [Owner Must Handle - Microsoft Demo Day](../Microsoft%20Demo%20Day!/Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)
4. [Open Issues](../06-Reference/Open%20Issues.md)
5. [07-Sessions By Day](../07-Sessions%20By%20Day/index.md)
6. [10-SESSION IMPROVEMENTS](../10-SESSION%20IMPROVEMENTS/index.md)
7. [11-AI HALLUCINATION - CRITICAL](../11-AI%20HALLUCINATION%20-%20CRITICAL/index.md)
8. [12-PLAN MODE SESSIONS](../12-PLAN%20MODE%20SESSIONS/index.md)
9. [Training Index](../05-Training/index.md)
10. [Repo Documents Index](../06-Reference/Repo%20Documents%20Index.md)

## Repo Structure Rule

- Keep app/runtime documents at repo root when tests, README, or scripts already refer to them.
- Use Schematics to consolidate, index, and explain those docs inside Obsidian.
- File movement is not organization unless note homes, backlinks, references, and current-state summaries are updated with it.
- Every folder in `Schematics` should explain itself through `index.md`.
