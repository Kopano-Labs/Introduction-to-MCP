---
title: Delegation Protocol
created: 2026-04-06
updated: 2026-04-10
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
> Session governance is additionally defined in [DEV_S Reward Program](DEV_S%20Reward%20Program.md).

## Roles

| Role | Identity | Responsibility |
|------|----------|----------------|
| **Owner** | Robyn | Final authority. Reviews status, direction, and structural changes. |
| **Lead** | `Codex`, `Claude`, or `Codex + Claude` | Architecture, audits, reviews, shared infrastructure, delegation, and repo-wide decisions. |
| **DEV_1** | `Germini (Google AI, external by Master)` | Executes scoped implementation work, reports progress, and verifies deliverables. |
| **DEV_2** | `Nother` | Executes scoped implementation work, reports progress, and verifies deliverables. |
| **DEV_3** | `Meither` | Executes scoped implementation work, reports progress, and verifies deliverables. |
| **DEV_4** | `Cicero` | Executes research, governance, and verification work within scoped boundaries. |

## Standing Session Startup Rule

1. In multi-dev sessions, the standing team is `Germini`, `Nother`, `Meither`, and `Cicero`.
2. Do not invent new ad-hoc spawn roles as the default vault model.
3. Start sessions with devs on standby and 20-task boards visible in [MASTER-TODO Session 3](MASTER-TODO%20Session%203.md).
4. Before any task starts, Lead checks:
   - current dev progress
   - current code and diff state
   - latest [comms-log](comms-log.md)
5. All current sessions are `pre-sessions` and training data for Orch.
6. Lead target is `60% management / 40% coding`.
7. Token-saving mode is mandatory outside Plan Mode and outside Lead-only sessions with Master.

## Session Reset And Reward Rule

1. Every new session starts with all DEV_S reset to full permissions.
2. Reward expands trust, scope, and role breadth inside the session.
3. Punishment removes permissions and applies stricter supervision.
4. If a DEV loses role standing, Lead takes over and informs Master.

## Rules

### Commit identity rule

1. All commits from this repo must use the Owner identity.
2. Commit as `RobynAwesome <rkholofelo@gmail.com>`.
3. Do not improvise a different author name or email.
4. Before committing, verify git identity if there is any doubt.
5. If a worker cannot commit under the Owner identity, stop and fix that first.

### What `DEV_1` through `DEV_4` can do

1. Edit only files explicitly listed in their assignment scope.
2. Read any file in the repo before writing code.
3. Create new files only inside their assigned directories.
4. Append status updates to [comms-log](comms-log.md) when instructed.
5. Run verification commands for their assigned scope.
6. Stop immediately and report to Lead if a secret, token, or tracked vendor directory is found in git.

### What `DEV_1` through `DEV_4` cannot do

1. Edit shared infrastructure without Lead approval.
2. Rewrite or delete past comms entries.
3. Touch another dev's scoped files.
4. Change dependencies or global config without explicit approval.
5. Contact Owner directly about execution details.
6. Commit `node_modules/`, `.env`, secrets, or vendored config files.
7. Commit under any name or email other than `RobynAwesome <rkholofelo@gmail.com>`.
8. Guess when vault evidence or official research is missing.

## Chain Of Command Rule

1. DEV_S report to Lead only.
2. If a DEV goes directly to Owner about execution details, that is a hierarchy breach.
3. A hierarchy breach is logged as a Lead-management failure in training notes and session-improvement notes.
4. Master should ultimately communicate only with Lead in multi-dev sessions.

## Pre-Session Training Rule

1. Treat current sessions as Orch training data, not only task execution.
2. Log dev successes, failures, hierarchy breaches, and token use into Orch training notes.
3. Capture management errors as training evidence for future Orch behavior.

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

- Live status: [comms-log](comms-log.md)
- Ownership and queue: [task-board](task-board.md)
- Detailed progress: [dev-tracker](dev-tracker.md)
- Phase truth: [Project Status](Project%20Status.md)
- Reward policy: [DEV_S Reward Program](DEV_S%20Reward%20Program.md)
- Session reconstruction: [07-Sessions By Day](../07-Sessions%20By%20Day/index.md)
- Lead/process doctrine: [10-SESSION IMPROVEMENTS](../10-SESSION%20IMPROVEMENTS/index.md)
- Hallucination governance: [11-AI HALLUCINATION - CRITICAL](../11-AI%20HALLUCINATION%20-%20CRITICAL/index.md)
- Orch training logs: [Orch Train Logs](../05-Training/Orch%20Train%20Logs/index.md)

## Security Incident Rule

If any worker finds a credential in git or a tracked dependency/vendor directory:

1. Stop normal work.
2. Notify Lead in [comms-log](comms-log.md).
3. Do not paste the raw secret into notes.
4. Remove the tracked exposure and update the prevention docs.
5. Require revoke/rotate outside the repo before calling the incident closed.

## Chain Of Command

```text
Owner
  -> Lead
      -> DEV_1
      -> DEV_2
      -> DEV_3
      -> DEV_4
```

`DEV_1`, `DEV_2`, `DEV_3`, and `DEV_4` report to Lead only.
Lead updates Owner through the coordination docs.
