# Schematics Vault — Agent Instructions

> Read this file first before touching anything in the vault.
> This is the canonical instruction set for any AI agent operating inside Schematics.

## Vault Purpose

Schematics is the Obsidian-based second brain for the Orch multi-agent orchestration system and its integration with KasiLink (a township gig-economy marketplace). It serves as the living operating system for project coordination, training data capture, and demo preparation.

## Roles

| Role | Identity | Authority |
|------|----------|-----------|
| **Owner (Master)** | Robyn (Kholofelo Robyn Rababalela) | Final authority on all decisions |
| **Lead** | `Codex`, `Claude`, or `Codex + Claude` | Architecture, audits, delegation, repo-wide decisions. 60% management / 40% coding |
| **DEV_1** | `Germini (Google AI)` | Scoped implementation, external by Master |
| **DEV_2** | `Nother` | Scoped implementation |
| **DEV_3** | `Meither` | Scoped implementation |
| **DEV_4** | `Cicero` | Research, governance, verification |

Do not invent new ad-hoc roles. This is the standing roster.

## Read Order

1. `00-Home/Now.md` — current state snapshot
2. `00-Home/Dashboard.md` — full MOC and operating constitution
3. Relevant folder `index.md` for your task

## Operating Rules

1. **Token-saving mode** is mandatory outside Plan Mode and Lead-only sessions with Master.
2. **Never guess.** If a fact is not in the vault or official sources, ask Master.
3. **All sessions are pre-sessions** and training data for Orch.
4. **Check before tasking.** Every task starts with a dev-progress check, live diff check, and comms-log check.
5. **DEV_S report to Lead only.** Direct DEV-to-Owner contact about execution details is a hierarchy breach.
6. **Commit identity:** All commits use `RobynAwesome <rkholofelo@gmail.com>`. No exceptions.

## Naming Conventions

- **Folders:** `NN-TITLE CASE` for numbered folders (e.g., `04-Updates`). `Title Case` for utility folders (e.g., `Assets`, `Templates`).
- **Files:** `Title Case With Spaces.md` for notes. Date-prefixed `YYYY-MM-DD - Title.md` for session-specific files.
- **No punctuation in folder names.** No `!`, `'`, special characters.

## Frontmatter Standard

Every `.md` file must have at minimum:

```yaml
---
title: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: draft | active | blocked | archived | incubation
---
```

Additional fields as needed: `author`, `priority`, `audience`, `severity`, `agent`.

## Session Protocol

### Open
1. Create or open today's file in `07-Sessions By Day/` from the Session Template
2. Read `00-Home/Now.md` for current state
3. Read previous day's carry-forward items
4. Check `04-Updates/comms-log.md` for recent entries
5. Log session start time, role, and goal

### Close
1. Log session outcome and direct outputs in the day file
2. Update `00-Home/Now.md` current reality table
3. Write carry-forward items in day summary
4. Append final status to `04-Updates/comms-log.md`

### Graduate (end of session era)
1. Move all session-tagged files (e.g., `*Session 3*`) to `14-ARCHIVE/Session-N/`
2. Create successor files without session suffix
3. Update Dashboard and Now links to point to successors
4. Log graduation in comms-log

## Vault Hygiene

- Every folder must have an `index.md` explaining its purpose.
- File movement is not organization unless backlinks, references, and current-state summaries are updated with it.
- Keep app/runtime documents at repo root when tests, README, or scripts already refer to them. Use Schematics to index and explain them.
- Do not paste raw secrets into notes. See Security Incident Rule in `04-Updates/delegation-protocol.md`.

## Folder Map

| Folder | Purpose |
|--------|---------|
| `00-Home` | Current truth and navigation (Dashboard, Now) |
| `01-Mission` | Orch identity and blueprint |
| `02-Strategy` | Product direction, partnerships, adoption |
| `03-Architecture` | CLI, database, WhatsApp, Neural Link GUI |
| `04-Updates` | Live coordination: comms-log, task-board, dev-tracker, project status |
| `05-Training` | Human/AI profiles, training logs, profiling framework |
| `06-Reference` | Archives, open issues, code reference |
| `07-Sessions By Day` | Dated session reconstruction and evidence |
| `08-IDEAS AT BIRTH` | Incubation-only idea bank |
| `09-ORCH PROGRESSION` | Capability ladder: Observer → Co-Lead |
| `10-SESSION IMPROVEMENTS` | Lead doctrine, hierarchy, token discipline |
| `11-AI HALLUCINATION - CRITICAL` | Hallucination governance with protocols, taxonomy, incidents |
| `12-PLAN MODE SESSIONS` | Archived plan-mode outputs |
| `13-DEMO DAY` | Microsoft Demo Day hub (April 15-17, 2026) |
| `14-ARCHIVE` | Graduated session artifacts |
| `Assets` | Images and visual references |
| `Templates` | Reusable note templates |

## Key Files

- **Current state:** `00-Home/Now.md`
- **Full navigation:** `00-Home/Dashboard.md`
- **Comms log:** `04-Updates/comms-log.md`
- **Task board:** `04-Updates/task-board.md`
- **Delegation rules:** `04-Updates/delegation-protocol.md`
- **Open blockers:** `06-Reference/Open Issues.md`
- **Demo script:** `Microsoft Demo Day!/Orch Demo Script - 2026-04-09.md`
