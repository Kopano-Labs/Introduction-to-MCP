---
title: Demo Countdown - April 8-15, 2026
created: 2026-04-08
updated: 2026-04-10
author: Codex
tags:
  - demo
  - countdown
  - execution
  - startup-week
priority: critical
status: active
---

# Demo Countdown - April 8-15, 2026

> Hub: [Microsoft Demo Day!](index.md)
> Owner actions: [Owner Must Handle - Microsoft Demo Day](Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)
> Close state: [2026-04-09 Close State](2026-04-09%20Close%20State.md)

## Window

- Demo window: `2026-04-15` to `2026-04-17`
- Countdown plan owner: Lead
- Execution baseline: `Council -> Labs -> Console send -> Forge view -> Admin audit`; `KasiLink` remains owner-blocked until promoted

## Assumptions

- Demo success for the stabilization day means the Orch-only route is polished, rehearsed, and documented.
- The full flow in [SA Startup Week Demo](SA%20Startup%20Week%20Demo.md) remains the longer-term target: gig post, provider ranking, load-shedding safety, WhatsApp notification, and transparent reasoning.
- Azure remains the buyer-facing readiness story for Demo Day unless the owner explicitly promotes it further.
- Reward and referral work stays behind demo-path hardening unless the final live script requires it.

## Day-By-Day Plan

### 2026-04-08 | Today | Reality Check And Unblockers

**Owners**
- Lead
- Codex Terminal
- Owner

**Close state**
- Codex-owned April 8 work is closed as of `2026-04-09`.
- The only remaining gap to fully close this row is owner-supplied Clerk plus Atlas access so a real in-app KasiLink rehearsal can run.
- Until that is cleared, the safe live route remains the rehearsed Orch-only script in [Orch Demo Script - 2026-04-09](Orch%20Demo%20Script%20-%202026-04-09.md).

**Live status**
- countdown note created
- stale overlap handoff corrected against the current `KasiLink` repo
- `KasiLink` dependencies installed
- `KasiLink` lint passes
- `KasiLink` build passes
- Orch API is verified live on `/api/kasilink/health` and `/api/kasilink/dashboard`
- `KasiLink` bridge now forwards `/api/orch/*` to the mounted `/api/kasilink/*` upstream path
- public `GET` access for the home-page Orch dashboard and load-shedding widgets is no longer blocked by app-side sign-in checks
- Orch GUI public/admin split was started on `2026-04-08` and completed plus verified on `2026-04-09`, with public Labs limited to demo surfaces and internal boards moved behind `ADMIN PORTAL`
- `orch/gui` now builds cleanly after the public/admin split and live-feed log refactor
- local demo admin account `admin@orch.local` is registered and granted the `admin` role
- Orch was restarted on `127.0.0.1:8000` after the GUI rebuild and health still returns `200`
- a fresh `/broadcast` event now appears in `/updates`, which confirms live feed events are flowing into the runtime again
- Orch currently reports `whatsapp_bridge_configured: false`
- current runtime blocker is valid Clerk configuration, which fails before Atlas can be verified
- Azure tooling validation was blocked on `2026-04-08`, then resolved on `2026-04-09` when `az` and `azd` were installed locally in a non-admin path
- current repo confirms gig posting/apply/review plus load-shedding and Orch dashboard surfaces
- current repo does not yet show visible wiring for provider ranking in the gig flow or WhatsApp delivery in the notification flow

**Primary work**
- publish a corrected overlap handoff for the current repo reality
- confirm Atlas, Clerk, and authenticated QA prerequisites
- finish the Orch GUI split verification pass in the browser
- attempt the first local demo-path rehearsal
- verify Azure playbook readiness locally

**Exit criteria**
- [done] overlap note explicitly states what is safe to edit and what is stale
- [done] Atlas blocker is reduced to a concrete owner action, not a vague risk
- [done] Orch bridge path and upstream health are verified with evidence
- [owner-blocked] one rehearsal attempt is recorded with pass/fail evidence once valid Clerk keys are present
- [done] one Azure validation pass is recorded with next actions

**Closeout on `2026-04-09`**
- April 8 is closed for Codex-owned execution.
- Remaining closure items are now centralized in [Owner Must Handle - Microsoft Demo Day](Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md).
- Full end-to-end KasiLink rehearsal is still blocked by external auth and data access, not by an unknown engineering failure.

### 2026-04-09 | Stabilize Demo Path

**Owners**
- Lead
- Codex Terminal

**Close state**
- The day is closed when the Orch-only conservative route is polished, rehearsed, and documented as `Council -> Labs -> Console send -> Forge view -> Admin audit`.
- The full KasiLink route remains explicitly owner-blocked until valid Clerk access, Atlas reachability, and wider marketplace proof are supplied.
- Microsoft stays framed as `readiness story`, not as a fully connected live Azure stack.

**Live status**
- April 8 is now closed for Codex-owned work, and the remaining full-stack gap is explicitly tracked as owner-supplied Clerk plus Atlas access
- the conservative route is locked as `Council -> Labs -> Console send -> Forge view -> Admin audit`
- Orch GUI now passes browser QA for first-load stability, desktop/mobile layout, Labs launcher scrolling, public/admin boundary, and session-vault audit loading
- `/sessions` now prioritizes discussions with real audit data and exposes round plus audit-event counts in the vault
- admin login plus vault access now opens a real two-round forensic audit instead of landing on the empty latest session by default
- live-event rendering now passes across council, public console, and admin after the console relay patch
- Forge create/edit flows now survive live refresh, and lane movement is pressable through an explicit lane control instead of drag-only behavior
- MCP Console send and stream both return live replies in browser QA
- locked Orch-only public and admin rehearsal paths are now recorded with timing and presenter notes
- Azure CLI and Azure Developer CLI now work locally in a non-admin install path, and Orch Labs now exposes a live Microsoft readiness report
- current Microsoft readiness is `2/6` required checks and `1/3` optional checks on the local runtime; remaining blockers are Azure sign-in plus real Azure OpenAI, App Insights, and hosting env values
- the GUI shell is now split into routed pages for council, labs, forge, console, and admin with a persistent Framer Motion background and separate build chunks
- routed desktop renders are verified for `#/council`, `#/forge`, and `#/admin`, and a narrow mobile capture also renders cleanly
- next Orch blockers are no longer functional UI failures; they are demo-story polish, copy tightening, and reconnecting the Orch shell to the wider KasiLink story

**Core live route**
- `Council` opens with visible AI state and a seeded signal if the room is quiet
- `Labs` acts as the public launch pad and shows the honest Microsoft readiness card
- `Console send` is the main live answer path
- `Forge view` shows the active room, tasks, and artifacts without requiring edits
- `Admin audit` stays clearly internal and comes last

**Excluded from the core route**
- full KasiLink gig-post to provider-ranking story
- WhatsApp delivery
- reward and referral flows
- Azure AI Search
- managed identity plus RBAC storytelling

**Primary work**
- hold the full KasiLink rehearsal until valid Clerk configuration and Atlas reachability are supplied
- tighten public and admin copy so quiet states still read as intentional during the demo
- align the countdown, script, and owner checklist around the same safe-route truth
- reduce every remaining blocker to a named owner action with fallback wording
- finish the five-surface Orch verification pass without changing existing endpoints

**Exit criteria**
- demo path completes locally without unknown blockers, or the remaining blockers are reduced to named owner actions with a safe fallback route
- auth failures, empty-data failures, and missing env failures are either fixed or assigned with owner/date
- the five-task Orch browser checkpoint is recorded with evidence and the next blocker is explicit
- Orch GUI blocker list is reduced to zero functional UI failures
- one public path and one admin path are rehearsed and written down as the current safe demo route

### 2026-04-10 | Authenticated QA Day

**Owners**
- Lead
- Owner

**Primary work**
- run authenticated manager/admin QA if that repo is confirmed, otherwise run the current `KasiLink` seeker/provider authenticated marketplace QA
- verify production-style Clerk flows and MongoDB-backed writes
- confirm no route silently fails when signed in

**Exit criteria**
- the active authenticated QA checklist has a pass/fail result for each critical mutation flow
- every failing mutation has a named owner and next action

### 2026-04-11 | Azure Surface Hardening

**Owners**
- Lead
- Owner

**Primary work**
- validate Azure login, azd login, and deploy-story prerequisites
- verify API boot, GUI build, and telemetry hooks for the demo surface
- tighten the Azure-first narrative around identity, observability, and AI services

**Exit criteria**
- Azure playbook is executable without missing prerequisite ambiguity
- telemetry plan is defined for the demo surface
- public buyer story is reduced to one clean narrative

### 2026-04-12 | Demo Narrative Lock

**Owners**
- Lead
- Owner

**Primary work**
- lock the exact click path and speaking track for the demo
- remove non-essential branches, tabs, and distractions
- decide whether reward/referral is in or out of the live script

**Exit criteria**
- final live script is one page and ordered
- every screen in the demo has a purpose
- reward/referral is explicitly marked `IN SCRIPT` or `DEFERRED`

### 2026-04-13 | Full Dress Rehearsal

**Owners**
- Lead
- Owner

**Primary work**
- run the complete demo from start to finish on a clean environment
- time the flow
- capture every stumble, wait, missing seed, and fallback

**Exit criteria**
- one uninterrupted rehearsal completes
- runtime is acceptable for a live demo
- fallback plan exists for each risky dependency

### 2026-04-14 | Buffer And Fix Day

**Owners**
- Lead
- Codex Terminal

**Primary work**
- fix only the issues discovered in dress rehearsal
- avoid new feature work
- prepare backup data, screenshots, and a degraded demo route if needed

**Exit criteria**
- no open blocker remains without a fallback
- backup demo materials exist
- repo and Schematics are synchronized

### 2026-04-15 | Demo Start Day

**Owners**
- Lead
- Owner

**Primary work**
- verify env, auth, database, and telemetry before presenting
- run a short smoke test on the live surface
- present only the locked narrative

**Exit criteria**
- pre-demo smoke test passes
- the presenter has the exact script, fallback route, and links ready

## Today First

1. Reconcile the stale overlap note against the current repo.
2. Turn Atlas and authenticated QA into a concrete unblock plan.
3. Run the first strict demo rehearsal.
4. Validate Azure surface readiness.
5. Defer reward QA unless the live script still needs it.
