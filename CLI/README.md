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

- Python 3.9+
- API keys for your chosen LLM providers (e.g., Google, xAI).

## Prerequisites

- Python 3.9+
- Anthropic API Key

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

3.  **Install dependencies**:

    ```bash
    pip install -e .
    ```

4.  **Configure API Keys**:
    Create a `.env` file in the project root and add your API keys. For testing, you can use the value `MOCK_KEY`.
    ```env
    # Example .env file
    GOOGLE_API_KEY="your_gemini_api_key_here"
    XAI_API_KEY="your_grok_api_key_here"
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    ```

## Usage

### 1. Configure Your AI Team

Add agents to your local registry. The `id` is a local nickname for your agent.

```bash
# Add a Gemini agent
orch agents config gemini-pro --provider google --model gemini-pro --api-key "your_google_api_key"

# Add a Grok agent for moderation (using MOCK_KEY for testing)
orch agents config grok-mod --provider xai --model grok-1 --api-key "MOCK_KEY"
```

### 2. List Your Active Roster

See which agents are configured and ready for a discussion.

```bash
orch agents list
```

### 3. Launch a Discussion

Start a simulated "Think Tank" on any topic. Assign roles for participating agents and the moderator.

```bash
orch serve launch \
  --topic "The future of AI in South African fintech" \
  --agents "gemini-pro" \
  --moderator "grok-mod" \
  --max-rounds 5
```

## Development

For information on how to contribute, set up a development environment, and run tests, please see our `CONTRIBUTING.md` file.

You can track the project's progress on the Capabilities Roadmap.
