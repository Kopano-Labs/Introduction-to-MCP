# orch

[![CI Pipeline](https://github.com/RobynAwesome/Introduction-to-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/RobynAwesome/Introduction-to-MCP/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`orch` is a command-line framework for orchestrating discussions between multiple AI agents. It provides a "Group Chat" simulation where you can configure a team of AI agents from different providers (like Google, xAI, Anthropic, etc.) and have them collaborate on a given topic, guided by a Moderator AI.

This project is the reference implementation for the Model Context Protocol (MCP).

## Features

- **Multi-Agent Orchestration**: Run turn-based discussions with a team of configured AI agents.
- **Strategy Engine**: A Moderator AI guides the conversation, ensuring it stays productive and on-topic.
- **Data Lake**: All discussions are logged to a local SQLite database for auditing and analysis (Capability #98).
- **Unified API**: Powered by LiteLLM to support over 100 LLM providers with a single interface.
- **Extensible**: Designed for tool integration (Phase 3) to unlock advanced capabilities.

## Prerequisites

- Python 3.11+
- Anthropic API key
- Optional additional provider keys if you extend the client beyond Anthropic-backed flows

## Setup

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/RobynAwesome/Introduction-to-MCP.git
    cd Introduction-to-MCP
    ```

2.  **Create and activate a virtual environment**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install the CLI subproject**:

    ```bash
    python -m pip install -e ./CLI
    ```

4.  **Configure API Keys**:
    Create a `.env` file in the project root and add your API keys. For testing, you can use the value `MOCK_KEY`.
    ```env
    # Example .env file
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    ```

## Usage

### 1. Configure Your AI Team

Add agents to your local registry. The `id` is a local nickname for your agent.

```bash
# Launch the MCP CLI
mcp-cli
```

Pass additional MCP server scripts as arguments when needed:

```bash
mcp-cli path/to/extra_server.py
```

## Development

This repository has multiple surfaces:

- `orch`: the main orchestration framework installed from repo root
- `mcp-cli`: the separate CLI app installed from `./CLI`

For shared contribution guidance, tests, and CI checks, see `CONTRIBUTING.md`.

You can track the project's progress on the Capabilities Roadmap.
