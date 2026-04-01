# `orch` Capabilities Roadmap

This document maps the high-level "100 Capabilities" vision to the concrete engineering phases of the `orch` project. The engineering TODO list contains the steps we must take to unlock these powerful features.

A detailed breakdown of all 100 capabilities and their implementation status can be found in the `100_Capabilities_TODO.md` file.

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

## 🚀 Phase 3: The WhatsApp Gateway & Tool Integration (In Progress)

This phase focuses on bridging the gap between local CLI simulations and real-world deployment, giving agents "tools" (APIs, file system access, etc.) and connecting them to external interfaces.

**Key Milestones & Capabilities to be Unlocked:**

- **Gateway Bot:** Implement a single bot bridge (Twilio/WhatsApp Business API) for remote agent interactions.
- **CI/CD & Hardening:** Setup GitHub Actions, release management (PyPI/Docker), and audit logging.
- **#1. Write, debug, and test full features:** Requires file system and code execution tools.
- **#11. Run deep web research:** Requires a web browsing/search tool.
- **#31. Pull live data from any API:** The core of the tool-use paradigm.
- **#71. Connect any app that has an API:** The ultimate goal of the MCP architecture.

---

## 🌟 Phase 4: Data Analysis, Learning & UI (Upcoming)

This phase focuses on fine-tuning, reasoning extraction, UI dashboards, and fostering a vibrant community around `orch` for broader adoption.

**Key Milestones & Capabilities to be Unlocked:**

- **Reasoning Chains:** Extract and store logical structures from successful debates.
- **Fine-Tuning Prep:** Build `orch learn generate-tuning-data` to export reasoning into JSONL format.
- **#81. Facilitate community feedback:** Enable GitHub Discussions and Contribution guidelines.
- **#83. Showcase example projects:** Create and document practical demonstrations (e.g., ORCH apprenticeship protocol demo).

---

This roadmap will be updated as we complete items on the engineering TODO list, bringing us closer to realizing the full potential of the 100 capabilities.

**Connect with the Architect:**

- **LinkedIn:** www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
- **GitHub:** https://github.com/RobynAwesome/
