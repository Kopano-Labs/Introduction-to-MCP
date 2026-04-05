---
title: Delegation Protocol
created: 2026-04-06
updated: 2026-04-06
author: Lead
tags:
  - delegation
  - workflow
  - rules
  - agents
  - communication
priority: critical
audience:
  - lead
  - devs
  - owner
status: active
---

# Delegation Protocol

> Rules of engagement for multi-agent work on orch.
> All developers read this before touching code or updating `Schematics/04-Updates/`.

## Roles

| Role | Identity | Responsibility |
|------|----------|----------------|
| **Owner** | Robyn | Final authority. Reviews status, direction, and structural changes. |
| **Lead** | Lead | Architecture, audits, reviews, shared infrastructure, delegation, and repo-wide decisions. |
| **DEV_1** | Assigned dev agent | Executes scoped implementation work, reports progress, and verifies deliverables. |
| **DEV_2** | Assigned dev agent | Executes scoped implementation work, reports progress, and verifies deliverables. |

## Rules

### What `DEV_1` and `DEV_2` can do

1. Edit only files explicitly listed in their assignment scope.
2. Read any file in the repo before writing code.
3. Create new files only inside their assigned directories.
4. Append status updates to [[comms-log]] when instructed.
5. Run verification commands for their assigned scope.

### What `DEV_1` and `DEV_2` cannot do

1. Edit shared infrastructure without Lead approval.
2. Rewrite or delete past comms entries.
3. Touch another dev's scoped files.
4. Change dependencies or global config without explicit approval.
5. Contact Owner directly about execution details.

### Shared infrastructure owned by Lead

- `orch/orch/config.py`
- `orch/orch/api.py`
- `orch/orch/cli.py`
- `orch/orch/orchestration.py`
- `orch/orch/moderator.py`
- `orch/orch/agent_manager.py`
- `orch/gui/src/App.tsx`
- `pyproject.toml`
- `README.md`
- `Schematics/04-Updates/*`

## Task Assignment Format

```text
TASK: [ID] - [Short description]
SCOPE: [Exact file list]
OBJECTIVE: [Expected outcome]
CONSTRAINTS:
  - [Technical requirement]
  - [Out-of-scope warning]
DONE-WHEN:
  - [Acceptance criteria]
  - [Verification command or check]
REPORT: Append one update to [[comms-log]]
```

## Communication

- Live status: [[comms-log]]
- Ownership and queue: [[task-board]]
- Detailed progress: [[dev-tracker]]
- Phase truth: [[Project Status]]

## Chain Of Command

```text
Owner
  -> Lead
      -> DEV_1
      -> DEV_2
```

`DEV_1` and `DEV_2` report to Lead only.
Lead updates Owner through the coordination docs.
