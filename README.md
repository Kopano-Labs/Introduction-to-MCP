
![Kopano Context Banner](README-bannner.jpg)

   ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
    ![LiteLLM](https://img.shields.io/badge/LiteLLM-FF6F00?logo=star&logoColor=white)
    ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
    ![Typer](https://img.shields.io/badge/Typer-000000?logo=fastapi&logoColor=white)
    ![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6B46C1)
    ![SafeSkill](https://img.shields.io/badge/SafeSkill-Verified-10B981)
    ![Microsoft Ready](https://img.shields.io/badge/Microsoft-Demo_Ready-blue?logo=microsoft)
    [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 🌍 Kopano Context

**Full-Stack Multi-Agent Orchestration & South African Impact Ecosystem**
**Official Reference Implementation for the Model Context Protocol (MCP)**

> *Orchestrating intelligent discussions. Unifying social context. Empowering South African innovation.*
>
> **Kopano** — from Sesotho & Setswana: *"gathering"* or *"meeting together."*
> **Status:** 🔥 **FULL STACK DEMO READY** (Verified 2026-04-11)

---

## 🛡️ Kopano SafeSkill — Trust Layer for AI Tools

**Kopano Context is SafeSkill verified.**

SafeSkill is the leading **trust layer for AI tools**. It automatically scans every MCP server and AI skill for code exploits, prompt injection, data exfiltration, and hidden backdoors **before** you install or run it.

- ✅ **Safety Score:** **89/100 passes** (Verified 2026-03-30)
- ✅ Scanned & protected by SafeSkill
- ✅ Listed in the SafeSkill registry
- ✅ Safe to use in production

[![SafeSkill](https://safeskill.dev/api/badge/robynawesome-introduction-to-mcp)](https://safeskill.dev/scan/robynawesome-introduction-to-mcp)

---

## 🌐 The Kopano Ecosystem

| Product | Role | State |
|---------|------|-------|
| **Kopano Context** | Core AGI orchestration framework | **PROVEN** |
| **Kopano Studio** | Real-time Next.js visualization dashboard | **PROVEN** |
| **Kopano Labs** | Google-Labs-style South African impact tool gallery | **RUNNABLE** |
| **KasiLink Bridge** | Full-stack marketplace connectivity (Clerk + Mongo) | **PROVEN** |
| **Microsoft Readiness** | Azure OpenAI + App Insights + Hosting Stack | **6/6 READY** |
| **Kopano SafeSkill** | Audit-twice trust and verification layer | **ACTIVE** |

---

## ✨ Key Capabilities

- **Multi-Provider Mesh** — Orchestrate Anthropic, Google (Gemini), xAI (Grok), and OpenAI in parallel.
- **Smart Moderation** — Intelligent Moderator AI keeps discussions filtered, focused, and goal-oriented.
- **KasiLink Bridge** — Verified integration with the KasiLink marketplace for gig-matching and utility notification.
- **WhatsApp Gateway** — Real-time mobile broadcast via `whin2` RapidAPI bridge (Success Verified).
- **Persistent Data Lake** — High-fidelity logging to SQLite for auditing, replay, and JSONL training data generation.
- **Microsoft Staging** — Native support for Azure OpenAI, application insights telemetry, and `azd` deployment.
- **Long-term Memory** — Persistent associative memory ensures agents recall context across sessions.

---

## 📁 Repository Layout

- **Core Engine:** `kopano-core/` (The primary Python package)
  - Install: `pip install -e ./kopano-core`
- **Studio Interface:** `kopano-core/studio/` (The Next.js visualization dashboard)
  - Run: `npm run dev` or `npm run build`
- **KasiLink Bridge:** `KasiLink/` (The Next.js marketplace integration)
  - Verified with real Auth (Clerk) and Persistence (MongoDB Atlas).
- **Orchestration Vault:** `Schematics/` (Obsidian 2nd Brain)
  - The canonical status, training, and session governance layer.

---

## 🚀 Quick Start

### 1. Environment Setup
Populate the root `.env` with your keys (Azure, Clerk, Atlas, etc.). Sync to targets:
```powershell
# Sync to frontend and backend targets
Copy-Item .env KasiLink/.env.local -Force
Copy-Item .env kopano-core/.env -Force
```

### 2. Install & Configure
```bash
cd kopano-core
pip install -e .
kopano agents config assistant --provider anthropic --model claude-3-5-sonnet-latest
```

### 3. Launch the Control Plane
```bash
# Start API & Studio (GUI)
kopano serve api
```
Access the dashboard at `http://127.0.0.1:8000`.

### 4. Verify Full Stack Connectivity
```bash
# Smoke test for demo readiness
python scripts/demo_day_smoke.py --json
# Test WhatsApp delivery
kopano whatsapp test --message "Ecosystem Online" --recipient "+27..."
```

---

## 🗺️ Roadmap: The 10 Phases

- **Phase 1-4**: Core Execution, Memory, Tool Use, and KasiLink Integration (✅ **COMPLETE**)
- **Phase 5**: Reliability, CI Hardening, and Microsoft Readiness (✅ **COMPLETE**)
- **Phase 6**: Labs Portfolio, SA Tool Packaging, and Forge Workspace (✅ **OPERATIONAL**)
- **Phase 7**: SA Language Engine & Speech-Access (In Progress)
- **Phase 8**: Cowork Creator Surfaces & Studio Code tracks (Active Buildout)
- **Phase 9**: Global Research, Free/Premium Mapping, and Feedback Loops (Planned)
- **Phase 10**: Scaled Release & Ecosystem Maturity (Planned)

---

## 🌍 Kopano Labs — South African Impact Tools

| Tool | Focus | State |
|------|-------|-------|
| Gig Matcher | Township jobs and income matching | **PROVEN** |
| Loadshedding Planner | National utility resilience | **PROVEN** |
| SA Language Engine | All 11+ official SA languages | **BETA** |
| Speech Access Assistant | Speech-impairment-aware AI access | **PLANNED** |
| Kopano Forge | Dynamic creation canvas + room persistence | **OPERATIONAL** |
| Kopano Studio Code | Native developer teaching tracks | **BETA** |

---

## 🎨 Design System

| Token | Value |
|-------|-------|
| **Background** | Karoo Night `#0D1117` |
| **Primary** | Savanna Gold `#F5A623` |
| **Success** | Terminal Mint `#00E676` |
| **Text** | Chalk Dust `#E2E8F0` |

---

## Security & Ethics

- **Zero-Secret Commit Policy:** Keys are never tracked. See `.gitignore`.
- **SafeSkill First:** All tools are audited for injection and exfiltration risks.
- **Privacy Policy:** Data Lake persistence is local-first by default.

## License

MIT © [RobynAwesome](https://github.com/RobynAwesome)
