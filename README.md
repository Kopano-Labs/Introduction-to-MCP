<div align="center">
  <img src="README-bannner.jpg" alt="Introduction to MCP Banner" width="100%" style="border-radius: 12px;"/>
  
  <h1>Introduction to MCP</h1>
  
  <p><strong>Multi-LLM Model Context Protocol (MCP) Servers & Clients</strong></p>
  <p><strong>Claude • Grok • Gemini • Copilot</strong></p>

  <p>
    <a href="https://www.python.org">
      <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge" alt="Python"/>
    </a>
    <a href="https://github.com/astral-sh/uv">
      <img src="https://img.shields.io/badge/uv-Astral-000000?logo=python&logoColor=ffdd54&style=for-the-badge" alt="uv"/>
    </a>
    <a href="https://anthropic.com">
      <img src="https://img.shields.io/badge/Anthropic-191919?logo=anthropic&logoColor=white&style=for-the-badge" alt="Anthropic"/>
    </a>
    <a href="https://claude.ai">
      <img src="https://img.shields.io/badge/Claude-FF6B00?logo=claude&logoColor=white&style=for-the-badge" alt="Claude"/>
    </a>
  </p>

  <a href="https://github.com/RobynAwesome/Introduction-to-MCP/stargazers">
    <img src="https://img.shields.io/github/stars/RobynAwesome/Introduction-to-MCP?style=social" alt="GitHub stars"/>
  </a>
</div>

<br>

## 👋 About the Project

This repository is a **practical, production-ready introduction** to **Anthropic’s Model Context Protocol (MCP)**.

It now features **full multi-LLM support**:
- **Claude** (native Anthropic SDK)
- **Grok** (xAI)
- **Gemini** (Google)
- **Copilot** (GitHub)

The `orch/` layer uses these LLMs together to **train and improve orchestration logic**, making the MCP implementation even more powerful and flexible.

You’ll learn how to build **MCP servers + clients** while leveraging the three core primitives:
- **🛠️ Tools** – Expose functions to any LLM
- **📦 Resources** – Share files, data & context
- **📝 Prompts** – Structured, high-quality interactions

Perfect for creating **AI-augmented apps with minimal code**.

---

## 🛠️ Tech Stack

<div align="center">
  <img src="https://skillicons.dev/icons?i=python,anthropic,claude,fastapi,grok,gemini,copilot,git,vscode,markdown&perline=8" alt="Tech Stack"/>
</div>

**Core technologies:**
- **Python** + **`uv`** (modern dependency management)
- **Anthropic MCP SDK** + **multi-LLM orchestration**
- Claude, Grok, Gemini & Copilot integration ready

---

## ✨ Features

- ⚡ Full MCP server + client with **multi-LLM support**
- 🌐 Grok • Gemini • Copilot added to train `orch/` layer
- 🚀 Ultra-modern Python setup (`uv`, `pyproject.toml`)
- 🤖 Seamless switching between LLMs
- 📁 Clean, well-documented structure
- 🔧 Runs in minutes
- 🇿🇦 Built in South Africa

---

📊 MCP Architecture
<img src="MCP%20DIAGRAM.png" alt="MCP Diagram">

👩‍💻 About Me
Kholofelo Robyn Rababalela
Freelance Web Developer · Computer Engineering Student
📍 Cape Town, Western Cape, South Africa

🔗 Connect With Me

LinkedIn
Ko-fi (Support my open-source work)
PayPal


Made with ❤️ in South Africa 🇿🇦
Star ⭐ this repo if you found it useful!

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/RobynAwesome/Introduction-to-MCP.git
cd Introduction-to-MCP

# 2. Install dependencies with uv
uv pip install -e .

# 3. Activate the virtual environment (Windows)
.\.CLI_Project\Scripts\activate
# or if using the default venv:
# .\.venv\Scripts\activate

# 4. Run the example
python main.py
