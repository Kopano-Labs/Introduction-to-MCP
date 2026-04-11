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

# Kopano Context CLI Specification

> POSIX-style CLI for orchestrating multi-agent AI simulations.
> See also: [Kopano Context Blueprint](../01-Mission/Kopano Context%20Blueprint.md), [Implementation Plan](../04-Updates/Implementation%20Plan.md), [Phase 1 Walkthrough](../04-Updates/Phase%201%20Walkthrough.md)

## Usage

```bash
Kopano Context [command] [subcommand] [flags]
```

## Commands

### 1. serve (Simulation Control)

Starts and manages the AI discussion environment.

- `Kopano Context serve launch` — Starts a new simulation.
  - `--topic` — The subject of discussion.
  - `--agents` — Comma-separated list of IDs.
  - `--max-rounds` — Number of exchanges before stopping.
  - `--group-simulated` — (Boolean) Run in terminal only.
  - `--whatsapp` / `-w` — Enable WhatsApp bridge.

### 2. chat (Interactive Control)

Manage an ongoing discussion.

- `Kopano Context chat status` — Show current round and active participants.
- `Kopano Context chat post [text]` — Inject a user directive.
- `Kopano Context chat log` — View recent history.
- `Kopano Context chat stop` — Terminate the session.

### 3. agents (Management)

Configure the models.

- `Kopano Context agents list` — Show available/configured models.
- `Kopano Context agents config [id] --api-key [key]` — Set credentials.
- `Kopano Context agents inspect [id]` — Show model capabilities.

### 4. learn (Knowledge Base)

Access the captured reasoning data.

- `Kopano Context learn datasets list` — List saved simulations.
- `Kopano Context learn datasets inspect [id]` — View insights from a session.
- `Kopano Context learn generate-tuning-data` — Export for fine-tuning.

## Example

```bash
Kopano Context agents config gemini --api-key "AIza..."
Kopano Context serve launch --topic "Mars Colonization" --agents "gemini,grok" --max-rounds 10
```
