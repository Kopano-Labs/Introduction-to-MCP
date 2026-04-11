

![Kopano Context Banner](README-bannner.jpg)

   ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
    ![LiteLLM](https://img.shields.io/badge/LiteLLM-FF6F00?logo=star&logoColor=white)
    ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
    ![Typer](https://img.shields.io/badge/Typer-000000?logo=fastapi&logoColor=white)
    ![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6B46C1)
    ![SafeSkill](https://img.shields.io/badge/SafeSkill-Verified-10B981)
    ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
    [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 🌍 Kopano Context

**Multi-Agent Orchestration Framework**
**Official Reference Implementation for the Model Context Protocol (MCP)**

> *Orchestrate intelligent discussions between AI agents from any provider — guided by a Smart Moderator AI.*
>
> **Kopano** — from Sesotho & Setswana: *"gathering"* or *"meeting together."*
> Named for what it does: bring intelligence together in one place.

---

## 🛡️ Kopano SafeSkill — Trust Layer for AI Tools

**Kopano Context is SafeSkill verified.**

SafeSkill is the leading **trust layer for AI tools**. It automatically scans every MCP server and AI skill for code exploits, prompt injection, data exfiltration, and hidden backdoors **before** you install or run it.

- ✅ Scanned & protected by SafeSkill
- ✅ Listed in the SafeSkill registry
- ✅ Safe to use in production

[![SafeSkill](https://safeskill.dev/api/badge/robynawesome-introduction-to-mcp)](https://safeskill.dev/scan/robynawesome-introduction-to-mcp)

---

## 🌐 The Kopano Ecosystem

| Product | Role |
|---------|------|
| **Kopano Context** | Core multi-agent orchestration framework — this repo |
| **Kopano CLI** | Terminal command-line interface (`kopano serve`, `kopano agents`, `kopano learn`) |
| **Kopano Studio** | Next.js + WebSocket real-time agent visualization dashboard |
| **Kopano Mesh** | Multi-agent network layer — Gemini, Grok, Claude, and others running in parallel |
| **Kopano Labs** | Google-Labs-style South African impact tool gallery |
| **Kopano SafeSkill** | Audit-twice trust and verification layer |

---

## ✨ Features

- **Multi-Provider Agents** — Run agents from Anthropic, xAI (Grok), Google (Gemini), OpenAI, and 100+ others through LiteLLM
- **Smart Moderator Engine** — An intelligent Moderator AI keeps every discussion productive, on-topic, and goal-oriented
- **Turn-Based Group Chat** — Realistic think-tank simulation with configurable roles
- **Persistent Data Lake** — Every conversation is automatically logged to SQLite for auditing, replay, and analysis
- **Kopano Studio (WebSocket)** — Real-time broadcasting to the React GUI dashboard
- **Long-term Memory** — Persistent associative memory for agents across sessions
- **Parallel Execution** — Concurrent agent processing for high-speed Kopano Mesh simulations
- **Security Auditor** — Built-in automated scanning for prompt injection and sensitive data leaks
- **WhatsApp Gateway** — Real-time broadcast of agent responses to WhatsApp for mobile monitoring
- **Data Lake & Fine-Tuning** — Generate high-quality JSONL/Alpaca/ChatML training data from discussion history
- **Data Analysis Tools** — Built-in sentiment analysis, dataset comparison, and spreadsheet cleaning

---

## 📁 Repository Layout

- Root package install: `python -m pip install -e .`
  Exposes `kopano` (and legacy `orch`) via `orch.orch.cli:app`.
- CLI subproject install: `python -m pip install -e ./CLI`
  This is a separate MCP-focused terminal app exposed as `mcp-cli`.
- GUI project: `orch/gui` (Kopano Studio)
  Use `npm run dev`, `npm run lint`, and `npm run build` inside that directory.
- Obsidian vault: `Schematics`
  The canonical status, training, and strategy layer for repo-backed documentation.
- Demo runbook: [DEMO_DAY_RUNBOOK.md](DEMO_DAY_RUNBOOK.md)
- 10-phase task map: [DEMO_DAY_10_PHASES_50_TASKS.md](DEMO_DAY_10_PHASES_50_TASKS.md)

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/RobynAwesome/Introduction-to-MCP.git
cd Introduction-to-MCP
pip install -e .
```

### 2. Configure Your AI Team
```bash
# Configure agents
kopano agents config gemini-pro --provider google --model gemini-1.5-pro
kopano agents config grok-mod   --provider xai   --model grok-beta

# See your roster
kopano agents list
```

### 3. Launch a Discussion (Kopano Mesh)
```bash
kopano serve launch \
  --topic "The future of AI in South African fintech" \
  --agents "gemini-pro" \
  --moderator "grok-mod" \
  --max-rounds 8 \
  --parallel
```

### 4. Kopano Studio (Browser Interface)
```bash
# Start the AGI Control Plane (API + Kopano Studio GUI)
kopano serve api
```
The browser will automatically open at `http://127.0.0.1:8000`, where you can watch the agents' reasoning in real-time through **Kopano Studio**.

### 5. Security Audit & Monitoring
```bash
# Test WhatsApp integration
kopano whatsapp test --message "Kopano Studio — Stable"
```

> **Legacy command:** The `orch` command remains available as a backwards-compatible alias during the transition period.

---

## Demo Day

- Runbook: [DEMO_DAY_RUNBOOK.md](DEMO_DAY_RUNBOOK.md)
- 10 phases / 50 tasks: [DEMO_DAY_10_PHASES_50_TASKS.md](DEMO_DAY_10_PHASES_50_TASKS.md)
- Preflight script: `.\scripts\demo_day_preflight.ps1`
- Readiness check: `python .\scripts\demo_day_readiness.py --quick`
- Smoke check: `python .\scripts\demo_day_smoke.py --strict`
- Launch helper: `.\scripts\demo_day_launch.ps1`

---

## 📊 Architecture
![MCP Diagram](Schematics/Assets/visuals/MCP%20DIAGRAM.png)

---

## 🗺️ Roadmap

- **Phase 1**: Core Multi-Agent Orchestration (✅ Done)
- **Phase 2**: Advanced Moderator Strategies + Memory (✅ Done)
- **Phase 3**: Full Tool Use via MCP & WebSocket Link (✅ Done)
- **Phase 4**: Optimization, Scale & Security (✅ Complete - v0.1-alpha)
  - [x] Long-term Associative Memory
  - [x] Parallel Agent Execution
  - [x] WhatsApp Messaging Bridge
  - [x] Security Auditor Agent
  - [x] ChatML/JSONL Training Data Export
  - [x] Sentiment Analysis & Data Comparison Tools
  - [x] KasiLink API Gateway
  - [x] Loadshedding-aware scheduling
  - [x] Gig matching AI
- **Phase 5**: Kopano Labs Gallery (SA Impact Tools) — In Progress
- **Phase 6**: SA Language Engine (11 official languages) — Planned
- **Phase 7**: Speech Access & Accessibility-First — Planned
- **Phase 8**: Public-Impact Pilots & Metrics — Planned

---

## 🌍 Kopano Labs — South African Impact Tools

Kopano Labs is the experiment studio built on top of Kopano Context — a Google-Labs-style portfolio of practical AI tools for South African life.

| Tool | Focus |
|------|-------|
| Gig Matcher | Jobs and income for township workers |
| Loadshedding Planner | Utilities and resilience |
| Youth Opportunity Finder | Education and youth |
| Community Services Navigator | Civic access |
| SA Language Engine | All 11 official SA languages |
| Speech Access Assistant | Speech-impairment-aware workflows |
| Kopano Forge | Collaborative execution + canvas workflow |
| Kopano Code | Coding acceleration tool |

---

## 🎨 Brand

| Token | Value |
|-------|-------|
| Background | Karoo Night `#0D1117` |
| Primary | Savanna Gold `#F5A623` |
| Success | Terminal Mint `#00E676` |
| Text | Chalk Dust `#E2E8F0` |
| Tagline | *"Orchestrating intelligence. Unifying context."* |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and pull request guidance.

## Security Hygiene

- Never commit secrets, tokens, API keys, `.env` files, or vendor directories.
- `node_modules/` must remain untracked. Install dependencies locally instead of committing them.
- If a secret is ever exposed in git, treat it as compromised immediately: revoke or rotate it outside the repo, then remove the tracked source of exposure.
- Read [SECURITY.md](SECURITY.md) before handling any incident or sensitive credential.

## License

MIT © [RobynAwesome](https://github.com/RobynAwesome)
