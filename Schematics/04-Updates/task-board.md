---
title: Task Board
created: 2026-04-06
updated: 2026-04-11
author: Lead
tags:
  - tasks
  - ownership
  - roadmap
  - coordination
priority: high
audience:
  - lead
  - devs
  - owner
status: active
---

# Task Board

> Live ownership board for Kopano Context.
> Current source of truth is the audit completed on 2026-04-06 against `Schematics`, `README.md`, and the active codebase layout.

## Session Roster

- Creator: `RobynAwesome`
- Observer: `Kopano Context`
- Lead Developer: `Codex`
- DEV_1: `Germini (Google AI)`

## Current Delivery State

| Area | Status | Notes |
|------|--------|-------|
| Phase 1 | DONE | Core CLI orchestration foundation is documented and implemented. |
| Phase 2 | DONE | Moderator, memory, and structured logging are in place. |
| Phase 3 | DONE | MCP tools, API layer, GUI bridge, and WhatsApp flow exist. |
| Phase 4 | DONE | Optimization, security, and KasiLink integration layer implemented. |
| Phase 5 | DONE | Reliability baseline and CI hardening completed. |
| Phase 6 | IN PROGRESS | Kopano Labs layer is being built and exposed in product surfaces. |
| Phase 7 | IN PROGRESS | SA languages, SASL, and accessibility scaffolding are in code. |
| Phase 8 | IN PROGRESS | Cowork and Kopano Studio Code surfaces are now defined in code and launch config. |
| Phase 9 | IN PROGRESS | Research and refinement loop has started with the product Top 50 map. |

## Live Priorities

| ID | Priority | Owner | Status | Scope |
|----|----------|-------|--------|-------|
| S1 | Critical | Lead | DONE | Reframe current control notes around the RobynAwesome / Kopano Context session model |
| S2 | Critical | Lead | DONE | Rename active session-control taxonomy from `Orch` to `Kopano` where feasible in the vault |
| S3 | Critical | Lead | DONE | Create a session command pack for today’s run |
| S4 | Critical | Lead | IN PROGRESS | Keep dated evidence flowing into `comms-log` and `07-Sessions By Day/2026-04-11.md` |
| O1 | Critical | Lead | DONE | Audit `Schematics` and align docs with actual repo state |
| O2 | Critical | Lead | DONE | Create KasiLink-style comms and group-work format in `Schematics/04-Updates/` |
| O3 | High | Lead | DONE | Keep project status and coordination docs synchronized |
| O4 | High | Lead | DONE | Implement Phase 4 KasiLink gateway, loadshedding, and gig matching layer |
| O5 | High | Lead | DONE | Add test coverage for Phase 4 gateway behavior |
| O6 | Critical | Lead | DONE | Begin next roadmap slice after post-implementation stabilization |
| O7 | Critical | Lead | DONE | Repair CLI simulation reliability path |
| O8 | High | Lead | DONE | Modernize CI workflow for supported Python versions |
| O9 | High | Lead | DONE | Establish reliability and adoption baseline |
| O10 | Critical | Lead | DONE | Add Kopano Labs registry, API surface, and GUI mode |
| O11 | Critical | Lead | DONE | Define SA languages and speech-access phases with criticality |
| O12 | High | Lead | IN PROGRESS | Expand Labs tools into runnable impact slices |
| O13 | Critical | Lead | DONE | Add SA language planning, access modes, and launch config APIs |
| O14 | Critical | Lead | DONE | Add Top 50 product-readiness research note with free vs premium framing |
| O15 | Critical | Lead | IN PROGRESS | Remove tracked vendor directories, contain secret exposure, and document mandatory prevention rules |

## Active Phase 6 Work

| Item | Status | Candidate Owner |
|------|--------|-----------------|
| Labs registry and API | COMPLETE | Lead |
| Labs GUI mode | COMPLETE | Lead |
| SA tool catalog | COMPLETE | Lead |
| SA language phase definition | COMPLETE | Lead |
| Speech-access phase definition | COMPLETE | Lead |
| Language-plan API | COMPLETE | Lead |
| Multilingual runtime routing + translation | COMPLETE | Lead |
| Multilingual response packaging | COMPLETE | Lead |
| Accessibility execution flow | COMPLETE | Lead |
| Cowork + Kopano Studio Code API scaffolding | COMPLETE | Lead |
| Runnable Kopano Studio Forge flow | COMPLETE | Lead |
| Cowork reassignment + dispatch summary | COMPLETE | Lead |
| First Kopano Studio Code teaching loop | COMPLETE | Lead |
| Kopano Studio Code lesson progression | COMPLETE | Lead |
| Secret-exposure containment and doc hardening | IN PROGRESS | Lead |
| Runnable Labs feature expansion | OPEN | DEV_1 |
| Accessibility implementation prep | OPEN | DEV_2 |
| Research backlog ranking | OPEN | Lead |

## Rules For Next Dispatch

1. Phase 6 owns the additive Labs layer and must not break Kopano Context core.
2. Phase 7 is critical and must treat all SA languages and accessibility as first-class scope.
3. `DEV_1` and `DEV_2` should take bounded Labs or accessibility tasks only.
4. Lead owns final review and any cross-cutting infrastructure edits.
5. Security incidents override feature work until tracked exposure is removed and documented.
6. The Observer learns from notes, logs, and contradictions; the Observer does not own execution.

## Task Addendum - 2026-04-09

- create one canonical current-state note for Obsidian navigation
- add a repo-doc index so root markdown files are organized without breaking tests or README references
- add an open-issues note that consolidates current blockers and demo gaps
- add current-session training notes for Codex, Robyn, multi-agent profiling, and Claude/Codex/Gemini role analysis
- remove stale `STRUCTURE/...` references from active Schematics notes
- reduce VS Code Explorer clutter through editor nesting instead of moving root repo files
- complete `az login` and `azd auth login` in the live demo shell
- populate Azure OpenAI, App Insights, and hosting values in the local env before claiming the Microsoft path is demo-ready
- decide explicitly whether Azure AI Search and managed identity are `IN DEMO` or `DEFERRED`
- keep Microsoft-facing claims at readiness/proof level until required checks move from `2/6` to `6/6`
