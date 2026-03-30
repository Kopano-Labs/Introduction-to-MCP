# `orch` Capabilities Roadmap

This document maps the high-level "100 Capabilities" vision to the concrete engineering phases of the `orch` project. The engineering TODO list contains the steps we must take to unlock these powerful features.

---

## ✅ Phase 1: Foundation (Complete)

The initial setup of the CLI, agent management, and basic simulation loop provides the bedrock for all future capabilities.

---

## 🏗️ Phase 2: Data Lake & Strategy Engine (In Progress)

The current focus on integrating the **Moderator AI** and implementing **Structured Logging** is critical for enabling advanced reasoning and auditing.

**Capabilities Unlocked by this Phase:**

- **#91. Run multi-step reasoning chains:** The Moderator is the engine for this.
- **#92. Self-correct when it makes a mistake:** The Moderator's analysis of agent output is the first step.
- **#95. Handle ambiguous requests by asking smart clarification questions:** The Moderator can identify ambiguity and prompt for clarity.
- **#98. Explain its own reasoning and show you the exact tool calls it made:** The SQLite logging provides the transparent audit trail for this.

---

## 🚀 Phase 3 & Beyond: Tool Integration & Autonomy

Once the core reasoning engine is stable, we will begin giving agents "tools" (APIs, file system access, etc.). This is where the majority of the 100 capabilities will come to life.

**Example Capabilities to be Unlocked:**

- **#1. Write, debug, and test full features:** Requires file system and code execution tools.
- **#11. Run deep web research:** Requires a web browsing/search tool.
- **#21. Manage your entire calendar:** Requires a calendar API tool (Google, Outlook).
- **#31. Pull live data from any API:** The core of the tool-use paradigm.
- **#41. Write full blog posts:** Requires file I/O tools.
- **#71. Connect any app that has an API:** The ultimate goal of the MCP architecture.

---

This roadmap will be updated as we complete items on the engineering TODO list, bringing us closer to realizing the full potential of the 100 capabilities.

**Connect with the Architect:**

- **LinkedIn:** www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
- **GitHub:** https://github.com/RobynAwesome/
