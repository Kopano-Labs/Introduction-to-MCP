---
title: Implementation Plan
created: 2026-04-03
updated: 2026-04-06
author: Robyn
tags:
  - updates
  - implementation
  - phases
  - roadmap
priority: high
status: active
---

# orch Implementation Plan

> Master engineering plan for building orch across 4 phases.
> See also: [[Project Status]], [[CLI Specification]], [[Phase 1 Walkthrough]]

## Tech Stack

- **Python** with Typer (CLI), Rich (Terminal UI), LiteLLM (Unified AI Access), Pydantic-Settings (Configuration)
- **FastAPI** + Uvicorn for the API layer
- **React 19** + TypeScript + Vite for the Neural Link GUI
- **SQLite** for the Data Lake

## Build Phases

### Phase 1: The Foundation (Simulated CLI Chat) — COMPLETE

- **Entry Point:** `orch.py` with subcommand structure: `serve`, `chat`, `agents`, `learn`
- **Agent Manager:** `orch agents config` to securely store API keys
- **Simulation Engine:** `orch serve launch --group-simulated true` for round-robin terminal discussions

### Phase 2: Data Lake & Strategy Engine — COMPLETE

- **Structured Logging:** SQLite schema for (Model, Message, Topic, Prompt, Timestamp)
- **Moderator Logic:** AI Moderator (Claude/GPT-4o) to manage flow and summarize rounds
- **Context Handling:** Standardized history injection so all models share the same state

### Phase 3: The WhatsApp Gateway — COMPLETE

- **Gateway Bot:** Evolution API bridge for WhatsApp integration
- **Formatting:** `[Agent Name]: Message` format for group clarity
- **Tool Integration:** 20+ tools registered via MCP

### Phase 4: Optimization, Scale & Security — COMPLETE

- [x] Long-term Associative Memory (SQLite-backed)
- [x] Parallel Agent Execution
- [x] WhatsApp Messaging Bridge
- [x] Security Auditor Agent
- [x] ChatML/JSONL Training Data Export
- [x] Sentiment Analysis
- [x] KasiLink API Gateway integration
- [x] Loadshedding tool
- [x] Gig matching tool

## Verification Plan

1. `orch agents config gemini --api-key "..."` — Verify key is saved
2. `orch serve launch --topic "AGI Ethics" --agents "gemini,gpt4"` — Verify local debate begins
3. `orch chat log` — Verify discussion was correctly recorded in Data Lake
4. `python -m pytest tests/test_kasilink_phase4.py -q` — Verify KasiLink gateway, matching, and loadshedding behavior
