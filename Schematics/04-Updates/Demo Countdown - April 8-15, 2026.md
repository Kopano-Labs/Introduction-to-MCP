---
title: Demo Countdown - April 8-15, 2026
created: 2026-04-08
updated: 2026-04-08
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

## Window

- Demo window: `2026-04-15` to `2026-04-17`
- Countdown plan owner: Lead
- Execution baseline: `orch` plus `KasiLink`

## Assumptions

- Demo success still means the flow in `02-Strategy/SA Startup Week Demo.md` must work: gig post, provider ranking, load-shedding safety, WhatsApp notification, and transparent reasoning.
- Azure remains the buyer-facing story for Demo Day.
- Reward and referral work stays behind demo-path hardening unless the final live script requires it.

## Day-By-Day Plan

### 2026-04-08 | Today | Reality Check And Unblockers

**Owners**
- Lead
- Codex Terminal
- Owner

**Live status**
- countdown note created
- stale overlap handoff corrected against the current `KasiLink` repo
- `KasiLink` dependencies installed
- `KasiLink` lint passes
- `KasiLink` build passes
- Orch API is verified live on `/api/kasilink/health` and `/api/kasilink/dashboard`
- `KasiLink` bridge now forwards `/api/orch/*` to the mounted `/api/kasilink/*` upstream path
- public `GET` access for the home-page Orch dashboard and load-shedding widgets is no longer blocked by app-side sign-in checks
- Orch currently reports `whatsapp_bridge_configured: false`
- current runtime blocker is valid Clerk configuration, which fails before Atlas can be verified
- Azure tooling validation is currently blocked because `az` and `azd` are not installed in this environment
- current repo confirms gig posting/apply/review plus load-shedding and Orch dashboard surfaces
- current repo does not yet show visible wiring for provider ranking in the gig flow or WhatsApp delivery in the notification flow

**Primary work**
- publish a corrected overlap handoff for the current repo reality
- confirm Atlas, Clerk, and authenticated QA prerequisites
- attempt the first local demo-path rehearsal
- verify Azure playbook readiness locally

**Exit criteria**
- overlap note explicitly states what is safe to edit and what is stale
- Atlas blocker is reduced to a concrete owner action, not a vague risk
- Orch bridge path and upstream health are verified with evidence
- one rehearsal attempt is recorded with pass/fail evidence once valid Clerk keys are present
- one Azure validation pass is recorded with next actions

### 2026-04-09 | Stabilize Demo Path

**Owners**
- Lead
- Codex Terminal

**Primary work**
- fix the highest-severity blocker from the first rehearsal, which is currently valid Clerk configuration
- re-run gig creation, data loading, and reasoning visibility checks
- confirm protected routes and role-gated flows behave correctly

**Exit criteria**
- demo path completes locally without unknown blockers
- auth failures, empty-data failures, and missing env failures are either fixed or assigned with owner/date

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
