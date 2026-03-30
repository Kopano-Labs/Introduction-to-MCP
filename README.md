<div align="center">
  <img src="README-bannner.jpg" alt="Introduction to MCP Banner" width="100%" style="border-radius: 12px;"/>
  
  <h1>Introduction to MCP</h1>
  
  <p><strong>Multi-LLM Model Context Protocol (MCP) Servers & Clients</strong></p>

  <!-- LLM Badges -->
  <p>
    <a href="https://claude.ai">
      <img src="https://img.shields.io/badge/Claude-FF6B00?logo=claude&logoColor=white&style=for-the-badge" alt="Claude"/>
    </a>
    <a href="https://grok.x.ai">
      <img src="https://img.shields.io/badge/Grok-000000?logo=x&logoColor=white&style=for-the-badge" alt="Grok"/>
    </a>
    <a href="https://gemini.google.com">
      <img src="https://img.shields.io/badge/Gemini-8E75F5?logo=googlegemini&logoColor=white&style=for-the-badge" alt="Gemini"/>
    </a>
    <a href="https://github.com/features/copilot">
      <img src="https://img.shields.io/badge/Copilot-8957E5?logo=github-copilot&logoColor=white&style=for-the-badge" alt="GitHub Copilot"/>
    </a>
  </p>

  <!-- Core Tech Badges -->
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
  </p>

  <a href="https://github.com/RobynAwesome/Introduction-to-MCP/stargazers">
    <img src="https://img.shields.io/github/stars/RobynAwesome/Introduction-to-MCP?style=social" alt="GitHub stars"/>
  </a>
</div>

<br>

## 👋 About the Project
  <p>
    <a href="https://safeskill.dev/scan/robynawesome-introduction-to-mcp">
      <img src="https://img.shields.io/badge/SafeSkill-91%2F100_Verified%20Safe-brightgreen" alt="SafeSkill 91/100"/>
    </a>
  </p>

This repository is a **practical introduction** to **Anthropic’s Model Context Protocol (MCP)** with **full multi-LLM support**.

It demonstrates building MCP servers and clients while using:
- **Claude** (native Anthropic SDK)
- **Grok** (xAI)
- **Gemini** (Google)
- **Copilot** (GitHub)

The `orch/` layer uses all four LLMs together to **train and improve orchestration logic**.

---

## 🛠️ Tech Stack

<div align="center">
  <img src="https://skillicons.dev/icons?i=python,anthropic,claude,fastapi,grok,gemini,copilot,git,vscode,markdown&perline=8" alt="Tech Stack"/>
</div>

---

## ✨ Features

- ⚡ Full MCP server + client implementation  
- 🌐 Multi-LLM support (Claude • Grok • Gemini • Copilot)  
- 🚀 `orch/` layer trained with all four LLMs  
- 🧪 Ultra-modern Python setup with `uv`  
- 📁 Clean, well-documented structure  
- 🔧 Ready to run in minutes  
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

---

## ORCH Apprenticeship Training Loop

The diagram below shows how ORCH (the apprentice AI student) interacts with mentor agents (Claude, Gemini, Grok, Copilot) through MCP orchestration, while maintaining transparent audit logs of reasoning and execution.

![ORCH Apprenticeship Diagram](https://copilot.microsoft.com/th/id/BCO.8f58ca88-08bd-4ab3-adce-720cea93755c.png)

---

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
