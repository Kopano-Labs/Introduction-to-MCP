# 🪐 orch

[![CI Pipeline](https://github.com/RobynAwesome/Introduction-to-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/RobynAwesome/Introduction-to-MCP/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-FF6F00?logo=star&logoColor=white)](https://litellm.ai)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)

**Multi-Agent Orchestration Framework**  
**Official Reference Implementation for the Model Context Protocol (MCP)**

> Orchestrate intelligent discussions between AI agents from any provider — guided by a smart Moderator AI.

![Orch Banner](README-bannner.jpg)

---

## 🛡️ SafeSkill — Trust Layer for AI Tools

**orch is SafeSkill verified.**

SafeSkill is the leading **trust layer for AI tools**. It automatically scans every MCP server and AI skill for code exploits, prompt injection, data exfiltration, and hidden backdoors **before** you install or run it.

- ✅ Scanned & protected by SafeSkill
- ✅ Listed in the SafeSkill registry
- ✅ Safe to use in production

---

## ✨ Features

- **Multi-Provider Agents** — Run agents from Anthropic, xAI (Grok), Google (Gemini), OpenAI, and 100+ others through LiteLLM
- **Smart Moderator Engine** — An intelligent Moderator AI keeps every discussion productive, on-topic, and goal-oriented
- **Turn-Based Group Chat** — Realistic “think-tank” simulation with configurable roles
- **Persistent Data Lake** — Every conversation is automatically logged to SQLite for auditing, replay, and analysis (Capability #98)
- **Full MCP Compliance** — Reference implementation of Tools, Resources, and Prompts
- **Local-First & Private** — Runs entirely on your machine with your own API keys
- **Extensible** — Built for Phase 3 tool integration and custom capabilities

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![LiteLLM](https://img.shields.io/badge/LiteLLM-FF6F00?logo=star&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Typer](https://img.shields.io/badge/Typer-000000?logo=fastapi&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6B46C1)
![SafeSkill](https://img.shields.io/badge/SafeSkill-Verified-10B981)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

---

## 🚀 Quick Start

### 1. Clone & Install

---

2. Add Your API Keys
Create .env in the project root:
envGOOGLE_API_KEY="your_gemini_api_key_here"
XAI_API_KEY="your_grok_api_key_here"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"
3. Configure Your AI Team
Bash# Add agents
orch agents config gemini-pro --provider google --model gemini-1.5-pro
orch agents config grok-mod   --provider xai   --model grok-beta

# See your roster
orch agents list
4. Launch a Discussion
Bashorch serve launch \
  --topic "The future of AI in South African fintech" \
  --agents "gemini-pro" \
  --moderator "grok-mod" \
  --max-rounds 8

📊 Architecture
<img src="MCP%20DIAGRAM.png" alt="MCP Diagram">

Roadmap

Phase 1: Core Multi-Agent Orchestration (Done)
Phase 2: Advanced Moderator Strategies + Memory
Phase 3: Full Tool Use via MCP
Phase 4: Distributed agents + Web UI dashboard


Contributing
See CONTRIBUTING.md — we welcome PRs!
License
MIT © RobynAwesome

Made with ❤️ for the AI agent ecosystem
Protected by SafeSkill
textJust paste the whole thing into your `README.md` and push. It will look **professional**, modern, and instantly communicate what `orch` + **SafeSkill** are all about.

Want me to also generate:
- A better banner image using Grok Imagine?
- Screenshots/GIFs section?
- Or a dark-mode friendly version?

Just say the word! 🚀

```bash
git clone https://github.com/RobynAwesome/Introduction-to-MCP.git
cd Introduction-to-MCP
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
