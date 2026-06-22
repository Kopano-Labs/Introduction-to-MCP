---
title: Repo Documents Index
created: 2026-04-09
updated: 2026-04-09
author: Codex
tags:
  - reference
  - docs
  - repo-root
  - index
priority: high
status: active
---

# Repo Documents Index

> Map of the loose root markdown files.
> These files are intentionally indexed here instead of being casually moved, because some are referenced by README, tests, or operator workflows.

## Orientation And Governance

| File | Purpose | Keep At Root |
|------|---------|--------------|
| `README.md` | public overview and quick start | yes |
| `index.md` | repo-root Obsidian entry note | yes |
| `ORCH_USER_GUIDE.md` | local PowerShell operator guide | yes |
| `CONTRIBUTING.md` | contributor workflow | yes |
| `SECURITY.md` | security policy and incident hygiene | yes |
| `RELEASE.md` | release/process stub | yes |

## Demo And Delivery

| File | Purpose | Keep At Root |
|------|---------|--------------|
| `DEMO_DAY_RUNBOOK.md` | live operator runbook | yes |
| `DEMO_DAY_10_PHASES_50_TASKS.md` | demo execution checklist | yes |
| `BRAINTRUST_SETUP.md` | Braintrust env and CLI setup | yes |

## Roadmap And Capability Tracking

| File | Purpose | Keep At Root |
|------|---------|--------------|
| `100_Capabilities_TODO.md` | capability map and status tracker | yes |

## Historical Execution Snapshots

These files are useful reference, but they are not the current source of truth:

- `EXECUTION_20_TASKS.md`
- `EXECUTION_20_TASKS_PHASE6_PLUS.md`
- `EXECUTION_20_TASKS_LEAD_DEV2.md`
- `EXECUTION_20_TASKS_DEV2_DEV3.md`
- `EXECUTION_20_TASKS_DEV2_DEV3_CYCLE2.md`
- `EXECUTION_20_TASKS_DEV2_DEV3_LEAD_PHASE.md`
- `EXECUTION_20_TASKS_DEV2_DEV3_LEAD_PHASE_CYCLE2.md`

Use [Now](../00-Home/Now.md) and [Project Status](../04-Updates/Project%20Status.md) for current truth.

## Organization Rule

- If a root doc is referenced by tests, README, or scripts, do not move it just to make the tree look cleaner.
- Instead, give it a clear home inside Obsidian through this index and the dashboard notes.
- Only move root docs after a full reference audit and follow-up patch pass.
