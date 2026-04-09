---
title: Database Schema
created: 2026-04-03
updated: 2026-04-05
author: Robyn
tags:
  - architecture
  - database
  - sqlite
  - data-lake
priority: medium
status: active
---

# orch Data Lake Schema

> SQLite schema for audit logging and discussion persistence.
> See also: [Project Status](../04-Updates/Project%20Status.md), [Implementation Plan](../04-Updates/Implementation%20Plan.md)

## Tables

### discussions

Tracks simulation sessions.

```sql
CREATE TABLE IF NOT EXISTS discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### audit_logs

Captures model reasoning, execution, and messages with timestamps.

```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discussion_id INTEGER,
    model TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    message TEXT,
    prompt TEXT,
    log_type TEXT CHECK(log_type IN ('reasoning', 'execution', 'message')) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(discussion_id) REFERENCES discussions(id)
);
```

## Phase 4 Additions

Additional tables added in Phase 4 (see `orch/orch/database.py`):
- `messages` — Individual agent responses per round
- `long_term_memory` — Agent associative memory (topic, content, metadata)
