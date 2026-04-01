### Project Status and Capabilities of `orch`

Based on the current project state, here is the breakdown of the current phase, `orch`'s capabilities, and the status of `main.exe`.

#### 1. What Phase Are We On?
We are currently in **Phase 4: Optimization, Scale & Security** (v0.1-alpha).
- **Phase 1 (Done):** Core Multi-Agent Orchestration.
- **Phase 2 (Done):** Advanced Moderator Strategies + Memory.
- **Phase 3 (Done):** Full Tool Use via MCP & WebSocket Link.
- **Phase 4 (In Progress):**
    - [x] Long-term Associative Memory (SQLite-backed).
    - [x] Parallel Agent Execution.
    - [x] WhatsApp Messaging Bridge.
    - [x] Security Auditor Agent.
    - [x] ChatML/JSONL Training Data Export.

#### 2. What is `orch` Capable Of?
`orch` is a multi-agent orchestration framework designed for the Model Context Protocol (MCP). Its primary capabilities include:

- **Multi-Agent Discussions:** Orchestrates intelligent, turn-based "think-tank" simulations between agents from various providers (Anthropic, Google, OpenAI, xAI, etc.) using `LiteLLM`.
- **Smart Moderation:** Uses a Moderator AI to summarize rounds, prevent tangents, and guide agents toward a specific goal.
- **Extensible Tool Use (MCP):** Agents can perform real-world tasks using registered tools, including:
    - **Filesystem:** `read_file`, `write_file`, `list_directory`, `delete_file`.
    - **Development:** `execute_code` (Python), Git integration (`git_init`, `git_add`, `git_commit`, etc.).
    - **Research:** `search` (Tavily), `search_arxiv`, `scrape_page`.
    - **Security:** `scan_code_security` (Bandit), `scan_dependencies` (Safety), and a `SecurityAuditor` agent that monitors conversations for prompt injection.
    - **Reporting:** `generate_report` (Markdown) and `monitor_brand` (Social Media).
- **Persistent Memory:** Automatically logs all discussions to a SQLite "Data Lake" and uses associative memory to recall context across sessions.
- **Real-time Monitoring:** Supports broadcasting to a React GUI (Neural Link) via WebSockets and real-time updates via a WhatsApp Gateway.

#### 3. What Results is `main.exe` Producing?
Currently, running `main.exe` (found in the `dist` folder) produces a simple greeting:
```text
Hello from introduction-to-mcp!
```
**Why?**
The `main.exe` currently acts as a minimal entry-point stub. To access the full `orch` functionality, it is recommended to use the Python-based CLI.

**How to run the full `orch` CLI:**
1. Ensure you have the dependencies installed:
   ```bash
   pip install -e .
   ```
2. Run the tool directly:
   ```bash
   orch --help
   ```
   Or via the main script:
   ```bash
   python main.py --help
   ```
   *Note: If you encounter `ModuleNotFoundError` for `pydantic_core`, ensure your virtual environment is properly activated and the package is fully installed.*