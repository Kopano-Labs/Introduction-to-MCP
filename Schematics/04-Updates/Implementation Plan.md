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

> Master engineering plan for building orch from core engine to Labs and accessibility phases.
> See also: [Project Status](Project%20Status.md), [CLI Specification](../03-Architecture/CLI%20Specification.md), [Phase 1 Walkthrough](Phase%201%20Walkthrough.md)

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

### Phase 5: Reliability, CI & Adoption Baseline — COMPLETE

- [x] Repair CLI simulation context/history handling for tests and auditability
- [x] Stabilize in-memory database testing for CLI discussion runs
- [x] Modernize GitHub Actions to supported Python versions
- [x] Add bytecode compile validation to CI
- [x] Bring the full legacy suite to green
- [x] Establish adoption-ready reliability baseline

## Phase 5 Verification Plan

1. `python -m pytest -q` — Verify the full suite is green
2. `python -m pytest tests/test_kasilink_phase4.py -q` — Verify Phase 4 gateway remains stable
3. `python -m compileall orch orch/orch` — Verify package compiles cleanly

### Phase 6: Orch Labs — IN PROGRESS — CRITICAL

- [x] Add Labs strategy doc into `Schematics`
- [x] Add Labs registry to the backend
- [x] Add `/api/labs/overview`, `/api/labs/tools`, `/api/labs/categories`, `/api/labs/phases`
- [x] Add Labs gallery mode to the GUI
- [x] Add criticality labels for tools and future phases
- [ ] Expand the initial Labs tool set into runnable feature slices

### Phase 7: SA Languages And Access — IN PROGRESS — CRITICAL

- [x] Add the 12 official South African languages to the Labs system model
- [x] Add language-plan API scaffolding
- [x] Add AAC, adaptive speech, and text-first access modes to the Labs system model
- [x] Add first multilingual routing runtime
- [x] Add deterministic translation execution for core phrases and handoff labels
- [x] Add multilingual response packaging with glossary assists
- [x] Add confirmation-aware accessibility execution flow
- [ ] Support all official South African languages in deeper model-backed response generation
- [ ] Add language-aware prompting and translation assist layers
- [ ] Add speech-impairment-aware interaction execution
- [ ] Add text-first, voice-assisted, and adaptive fallback flows end-to-end

### Phase 8: Public Impact Studio — IN PROGRESS — HIGH

- [x] Add Cowork and Orch Code surfaces to the Labs system model
- [x] Add launch config for 50/50 Anthropic/Codex visual direction with Stitch-inspired cowork support
- [x] Add persisted Orch Forge flow with rooms, lanes, tasks, and status updates
- [x] Add first Orch Code teaching loop against the current repo
- [x] Add cowork task reassignment and dispatch summary
- [x] Add Orch Code lesson-state progression
- [x] Add pilot analytics and impact metrics for Labs tools
- [x] Add installer and connector playbook execution cards for IDE, CLI, Azure, and AWS
- [x] Add MCP Console model selection and streaming surface
- [x] Add Forge create and edit flows for tasks and artifacts
- [ ] Add experiment graduation criteria
- [ ] Add community feedback loops
- [ ] Add public demo and partnership packaging

### Phase 9: Research And Refinement Engine — IN PROGRESS — CRITICAL

- [x] Create product-readiness research map with top 50 capabilities
- [x] Add free vs premium implementation framing
- [ ] Convert research findings into ranked execution backlog
- [ ] Add recurring benchmark and research review process

## Phase 6 Verification Plan

1. `python -m pytest tests/test_labs_api.py -q` — Verify Labs endpoints
2. `python -m pytest -q` — Verify the full suite remains green
3. `python -m compileall orch orch/orch` — Verify package compiles cleanly
4. `npm run build` from `orch/gui` — Verify the launch surface still builds
