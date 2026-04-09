---
title: Phase 1 Walkthrough
created: 2026-04-03
updated: 2026-04-05
author: Robyn
tags:
  - updates
  - phase-1
  - walkthrough
  - tutorial
priority: low
status: complete
---

# Phase 1 Walkthrough: orch Foundation

> The foundational CLI and orchestration logic.
> See also: [Project Status](Project%20Status.md), [CLI Specification](../03-Architecture/CLI%20Specification.md), [Implementation Plan](Implementation%20Plan.md)

## Status: COMPLETE

We have successfully established the foundational CLI and orchestration logic for orch. The system can now manage multiple AI agent configurations and run turn-based discussions in a terminal "Group Chat" simulation.

## How to Use orch (Test Mode)

### 1. Configure Your AI Team

```bash
# Add a Gemini agent
orch agents config gemini --api-key "MOCK_KEY" --provider google
# Add a Grok agent
orch agents config grok --api-key "MOCK_KEY" --provider xai
```

### 2. List Your Active Roster

```bash
orch agents list
```

### 3. Launch a Discussion

```bash
orch serve launch --topic "AI Ethics" --agents "gemini,grok" --max-rounds 2
```

> **Mock vs. Real:** Because we used `MOCK_KEY`, the system generates local responses. Add real API keys and orch automatically switches to calling real models through LiteLLM.

## Technical Highlights

- **CLI Engine:** Built with Typer and Rich for a premium, POSIX-compliant terminal experience
- **Unified Adapter:** Integrated LiteLLM, allowing communication with 100+ different AI models
- **Agent Orchestrator:** Round-robin scheduler in `simulator.py` maintaining 10 rounds of conversation context
- **Environment Isolation:** Dedicated virtual environment (`.venv`) for project stability
