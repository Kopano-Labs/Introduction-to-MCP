# Schematics Vault — Agent Instructions

> Read this file first before touching anything in the vault.
> This is the canonical instruction set for any AI agent operating inside Schematics.

## TOKEN CONSERVATION (MANDATORY — HIGHEST PRIORITY)

- **Zero preambles.** No "Let me...", "I'll...", "Great..." — act immediately.
- **Zero recaps.** No file lists, no summaries after completing work.
- **Zero narration.** Don't describe what tools you're calling.
- **Responses ≤5 lines** unless code, plans, or depth explicitly requested.
- **Targeted reads only.** offset/limit always. Never full read >150 lines unless required.
- **Batch all independent calls.** One message, parallel tool calls, always.
- **Warn at 50% context** — say "⚠ context ~50%" so user can checkpoint.
- **No skills** unless explicitly invoked by Master.
- **No agents** unless parallel work would otherwise exceed context.
- **No billing fabrication** — never invent token percentages.

## PC CONTROL RULE (ABSOLUTE)

- **NEVER take over the computer.** No clicks, no typing, no navigation on behalf of user.
- **Edge = read-only screenshots only.** Analyze tabs to understand Master's objectives. That is all.
- "Go to [app]" = screenshot + read. NOT request_access + navigate.
- PC control requires explicit "just do it" for that specific action.

## Vault Purpose

Schematics is the Obsidian-based second brain for the **Kopano Context** multi-agent orchestration system. It serves as the living operating system for project coordination, training data capture, and demo preparation.

**Kopano Ecosystem:** Kopano Context · Kopano CLI · Kopano Studio · Kopano Mesh · Kopano Labs · Kopano SafeSkill

## Roles

| Role | Identity | Authority |
|------|----------|-----------|
| **Owner (Master)** | Robyn (Kholofelo Robyn Rababalela) | Final authority |
| **Lead** | `Codex`, `Claude`, or `Codex + Claude` | Architecture, audits, delegation. 60% mgmt / 40% coding |
| **DEV_1** | `Germini (Google AI)` | Scoped implementation |
| **DEV_2** | `Nother` | Scoped implementation |
| **DEV_3** | `Meither` | Scoped implementation |
| **DEV_4** | `Cicero` | Research, governance, verification |

Do not invent new ad-hoc roles.

## Read Order

1. `00-Home/Now.md` — current state
2. `00-Home/Dashboard.md` — full MOC
3. Relevant folder `[FolderName] - Index.md` for your task

## Operating Rules

1. Token-saving mode is mandatory outside Plan Mode and Lead-only sessions with Master.
2. Never guess. If a fact is not in the vault or official sources, ask Master.
3. All sessions are pre-sessions and training data for Kopano Context.
4. Check before tasking: dev-progress check, live diff check, comms-log check.
5. DEV_S report to Lead only. Direct DEV-to-Owner contact is a hierarchy breach.
6. Commit identity: `RobynAwesome <rkholofelo@gmail.com>`. No exceptions.

## Naming Conventions

- **Folders:** `NN-TITLE CASE` numbered (e.g. `04-Updates`). `Title Case` for utility folders.
- **Files:** `Title Case With Spaces.md`. Date-prefixed `YYYY-MM-DD - Title.md` for session files.
- **Index files:** `[FolderName] - Index.md` (NOT `index.md`).
- **No punctuation in folder names.**

## Frontmatter Standard

```yaml
---
title: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: draft | active | blocked | archived | incubation
---
```

## Session Protocol

### Open
1. Open today's file in `07-Sessions By Day/`
2. Read `00-Home/Now.md`
3. Read previous carry-forward items
4. Check `04-Updates/comms-log.md`

### Close
1. Log outcome in day file
2. Update `00-Home/Now.md`
3. Write carry-forward items
4. Append to `04-Updates/comms-log.md`

## Key Files

- **Current state:** `00-Home/Now.md`
- **Navigation:** `00-Home/Dashboard.md`
- **Comms log:** `04-Updates/comms-log.md`
- **Domain registry:** `06-Reference/Domain Registry.md`
- **All projects:** `00-Home/All Projects Registry.md`
- **Open blockers:** `06-Reference/Open Issues.md`

## What NOT To Do

- Never hallucinate or fabricate — say "I don't know"
- Never ignore STOP commands
- Never revert to default behavior — read memory FIRST every session
- Never use legacy name `Orch` — correct name is `Kopano Context` / KC
