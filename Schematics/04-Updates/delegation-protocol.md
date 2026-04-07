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
> Session governance is additionally defined in [[DEV_S Reward Program]].

## Roles

| Role | Identity | Responsibility |
|------|----------|----------------|
| **Owner** | Robyn | Final authority. Reviews status, direction, and structural changes. |
| **Lead** | Lead | Architecture, audits, reviews, shared infrastructure, delegation, and repo-wide decisions. |
| **DEV_1** | Assigned dev agent | Executes scoped implementation work, reports progress, and verifies deliverables. |
| **DEV_2** | Assigned dev agent | Executes scoped implementation work, reports progress, and verifies deliverables. |

## Session Reset And Reward Rule

1. Every new session starts with all DEV_S reset to full permissions.
2. Reward expands trust, scope, and role breadth inside the session.
3. Punishment removes permissions and applies stricter supervision.
4. If a DEV loses role standing, Lead takes over and informs Master.

## Rules

### What `DEV_1` and `DEV_2` can do

1. Edit only files explicitly listed in their assignment scope.
2. Read any file in the repo before writing code.
3. Create new files only inside their assigned directories.
4. Append status updates to [[comms-log]] when instructed.
5. Run verification commands for their assigned scope.
6. Stop immediately and report to Lead if a secret, token, or tracked vendor directory is found in git.

### What `DEV_1` and `DEV_2` cannot do

1. Edit shared infrastructure without Lead approval.
2. Rewrite or delete past comms entries.
3. Touch another dev's scoped files.
4. Change dependencies or global config without explicit approval.
5. Contact Owner directly about execution details.
6. Commit `node_modules/`, `.env`, secrets, or vendored config files.

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
- `SECURITY.md`

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
- Reward policy: [[DEV_S Reward Program]]

## Security Incident Rule

If any worker finds a credential in git or a tracked dependency/vendor directory:

1. Stop normal work.
2. Notify Lead in [[comms-log]].
3. Do not paste the raw secret into notes.
4. Remove the tracked exposure and update the prevention docs.
5. Require revoke/rotate outside the repo before calling the incident closed.

## Chain Of Command

```text
Owner
  -> Lead
      -> DEV_1
      -> DEV_2
```

`DEV_1` and `DEV_2` report to Lead only.
Lead updates Owner through the coordination docs.
