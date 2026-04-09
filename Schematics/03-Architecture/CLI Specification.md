---
title: CLI Specification
created: 2026-04-03
updated: 2026-04-05
author: Robyn
tags:
  - architecture
  - cli
  - specification
priority: high
status: active
---

# orch CLI Specification

> POSIX-style CLI for orchestrating multi-agent AI simulations.
> See also: [Orch Blueprint](../01-Mission/Orch%20Blueprint.md), [Implementation Plan](../04-Updates/Implementation%20Plan.md), [Phase 1 Walkthrough](../04-Updates/Phase%201%20Walkthrough.md)

## Usage

```bash
orch [command] [subcommand] [flags]
```

## Commands

### 1. serve (Simulation Control)

Starts and manages the AI discussion environment.

- `orch serve launch` — Starts a new simulation.
  - `--topic` — The subject of discussion.
  - `--agents` — Comma-separated list of IDs.
  - `--max-rounds` — Number of exchanges before stopping.
  - `--group-simulated` — (Boolean) Run in terminal only.
  - `--whatsapp` / `-w` — Enable WhatsApp bridge.

### 2. chat (Interactive Control)

Manage an ongoing discussion.

- `orch chat status` — Show current round and active participants.
- `orch chat post [text]` — Inject a user directive.
- `orch chat log` — View recent history.
- `orch chat stop` — Terminate the session.

### 3. agents (Management)

Configure the models.

- `orch agents list` — Show available/configured models.
- `orch agents config [id] --api-key [key]` — Set credentials.
- `orch agents inspect [id]` — Show model capabilities.

### 4. learn (Knowledge Base)

Access the captured reasoning data.

- `orch learn datasets list` — List saved simulations.
- `orch learn datasets inspect [id]` — View insights from a session.
- `orch learn generate-tuning-data` — Export for fine-tuning.

## Example

```bash
orch agents config gemini --api-key "AIza..."
orch serve launch --topic "Mars Colonization" --agents "gemini,grok" --max-rounds 10
```
