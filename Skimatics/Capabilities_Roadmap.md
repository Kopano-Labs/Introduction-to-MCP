# `orch` Capabilities Roadmap

This document maps the high-level "100 Capabilities" vision to the concrete engineering phases of the `orch` project. The engineering TODO list contains the steps we must take to unlock these powerful features.

---

## ✅ Phase 1: Foundation (Complete)

The initial setup of the CLI, agent management, and basic simulation loop provides the bedrock for all future capabilities.

---

## ✅ Phase 2: Data Lake & Strategy Engine (Complete)

The core logic for the **Moderator AI** (Strategy Engine) and **Structured Logging** (Data Lake) is now implemented and tested. This provides a stable foundation for advanced reasoning, auditing, and context management.

**Capabilities Unlocked by this Phase:**

- **#91. Run multi-step reasoning chains:** The Moderator now guides the conversation, enabling complex, multi-step workflows.
- **#92. Self-correct when it makes a mistake:** The Moderator's analysis of agent output is the first step toward self-correction.
- **#95. Handle ambiguous requests by asking smart clarification questions:** The Moderator can identify ambiguity and prompt other agents for clarity.
- **#98. Explain its own reasoning and show you the exact tool calls it made:** The SQLite logging provides a transparent, auditable trail of every decision and interaction.

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

## 🌟 Phase 4: Community & Adoption

This phase focuses on fostering a vibrant community around `orch` and preparing for broader adoption.

**Example Capabilities to be Unlocked:**

- **#81. Facilitate community feedback:** Requires enabling GitHub Discussions and providing clear contribution guidelines.
- **#82. Publish project milestones:** Requires a public roadmap and versioned releases.
- **#83. Showcase example projects:** Requires creating and documenting practical demonstrations (e.g., ORCH apprenticeship protocol demo).
- **#84. Provide visual walkthroughs:** Requires recording short tutorial videos.
- **#85. Guide new contributors:** Requires `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

---

This roadmap will be updated as we complete items on the engineering TODO list, bringing us closer to realizing the full potential of the 100 capabilities.

**Connect with the Architect:**

- **LinkedIn:** Kholofelo Robyn Rababalela
- **GitHub:** RobynAwesome
