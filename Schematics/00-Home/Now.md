---
title: Now
created: 2026-04-09
updated: 2026-04-09
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

## Current Reality As Of 2026-04-09

| Area | State | Truth |
|------|-------|-------|
| Orch API + GUI | PASS | `tests/test_labs_api.py` passes, `npm run build` in `orch/gui` passes, compile checks pass, and `/api/labs/microsoft-readiness` returns live status. |
| Orch-only demo route | PASS | Public and admin rehearsal paths were locked and passed on `2026-04-09`. |
| Microsoft readiness | PARTIAL | Local tooling is installed and the live readiness endpoint works, but only `2/6` required checks and `1/3` optional checks are ready. |
| Full KasiLink story | PARTIAL | Wider buyer story still depends on external auth, data, and integration blockers. |
| Vault organization | IN PROGRESS | Schematics is the canonical Obsidian layer; root docs are now being indexed instead of moved casually. |
| Training corpus | ACTIVE | Human, AI, and orchestration profiles are being consolidated into a current training index. |

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
- Azure sign-in is still incomplete in the local demo shell
- Azure OpenAI, App Insights, and hosting env/resource values are still missing
- product polish: copy tightening, youth-fit research summary, and reconnecting the Orch-only route to the bigger KasiLink story

## Open These In Order

1. [Project Status](../04-Updates/Project%20Status.md)
2. [Microsoft Demo Day!](../Microsoft%20Demo%20Day!/index.md)
3. [Owner Must Handle - Microsoft Demo Day](../Microsoft%20Demo%20Day!/Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)
4. [Open Issues](../06-Reference/Open%20Issues.md)
5. [Repo Documents Index](../06-Reference/Repo%20Documents%20Index.md)
6. [Training Index](../05-Training/index.md)

## Repo Structure Rule

- Keep app/runtime documents at repo root when tests, README, or scripts already refer to them.
- Use Schematics to consolidate, index, and explain those docs inside Obsidian.
- File movement is not organization unless note homes, backlinks, references, and current-state summaries are updated with it.
