

![Orch Banner](README-bannner.jpg)

   ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
    ![LiteLLM](https://img.shields.io/badge/LiteLLM-FF6F00?logo=star&logoColor=white)
    ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
    ![Typer](https://img.shields.io/badge/Typer-000000?logo=fastapi&logoColor=white)
    ![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6B46C1)
    ![SafeSkill](https://img.shields.io/badge/SafeSkill-Verified-10B981)
    ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
    [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 🪐 orch

**Multi-Agent Orchestration Framework**  
**Official Reference Implementation for the Model Context Protocol (MCP)**

> Orchestrate intelligent discussions between AI agents from any provider — guided by a smart Moderator AI.

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
- **Neural Link WebSocket** — Real-time broadcasting to the React GUI (Neural Link Patch)
- **Long-term Memory** — Persistent associative memory for agents across sessions
- **Parallel Execution** — Concurrent agent processing for high-speed multi-agent simulations
- **Security Auditor** — Built-in automated scanning for prompt injection and sensitive data leaks
- **WhatsApp Gateway** — Real-time broadcast of agent responses to WhatsApp for mobile monitoring
- **Data Lake & Fine-Tuning** — Generate high-quality JSONL/Alpaca/ChatML training data from discussion history
- **Data Analysis Tools** — Built-in sentiment analysis, dataset comparison, and spreadsheet cleaning

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
orch agents config gemini-pro --provider google --model gemini-1.5-pro
orch agents config grok-mod   --provider xai   --model grok-beta

# See your roster
orch agents list
```

### 3. Launch a Discussion
```bash
orch serve launch \
  --topic "The future of AI in South African fintech" \
  --agents "gemini-pro" \
  --moderator "grok-mod" \
  --max-rounds 8 \
  --parallel
```

### 4. Neural Link (Browser Interface)
```bash
# Start the AGI Control Plane (API + Neural Link GUI)
orch serve api
```
The browser will automatically open at `http://127.0.0.1:8000`, where you can watch the agents' reasoning in real-time.

### 5. Security Audit & Monitoring
```bash
# Test WhatsApp integration
orch whatsapp test --message "Neural Link Stable"
```

---

## 📊 Architecture
![MCP Diagram](MCP%20DIAGRAM.png)

## 🗺️ Roadmap

- **Phase 1**: Core Multi-Agent Orchestration (✅ Done)
- **Phase 2**: Advanced Moderator Strategies + Memory (✅ Done)
- **Phase 3**: Full Tool Use via MCP & WebSocket Link (✅ Done)
- **Phase 4**: Optimization, Scale & Security (🚀 In Progress - v0.1-alpha)
  - [x] Long-term Associative Memory
  - [x] Parallel Agent Execution
  - [x] WhatsApp Messaging Bridge
  - [x] Security Auditor Agent
  - [x] ChatML/JSONL Training Data Export
  - [x] Sentiment Analysis & Data Comparison Tools


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
