# Contributing to `orch`

We welcome contributions to the `orch` project! By participating, you're helping to build a powerful Model Context Protocol (MCP) framework. This document outlines how you can contribute, from reporting bugs to submitting code.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project, you agree to abide by its terms.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please open an issue on our GitHub Issues page.

- Clearly describe the bug, including steps to reproduce it.
- Mention your operating system and Python version.
- If possible, include any error messages or stack traces.

### Suggesting Enhancements

Have an idea for a new feature or an improvement? We'd love to hear it!

- Open an issue on GitHub Issues.
- Describe your idea in detail, explaining why it would be valuable.
- Consider how it aligns with the project's roadmap.

### Your First Code Contribution

If you're looking to contribute code, start by checking our GitHub Issues for issues labeled `good first issue` or `help wanted`.

## Setting Up Your Development Environment

1.  **Fork and Clone**: Fork the `Introduction-to-MCP` repository on GitHub and clone your fork locally.
    ```bash
    git clone https://github.com/YOUR_USERNAME/Introduction-to-MCP.git
    cd Introduction-to-MCP
    ```
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -e .
    ```
4.  **Install Dev Tools**:
    ```bash
    python -m pip install pytest ruff
    ```
5.  **Configure API Keys**: `orch` uses `Pydantic-Settings` for configuration. Create a `.env` file in the root of your project and add your API keys for LLM providers (e.g., `GOOGLE_API_KEY`, `XAI_API_KEY`). For testing without real keys, you can use `MOCK_KEY`.
    ```env
    # Example .env content
    GOOGLE_API_KEY="your_gemini_api_key_here"
    XAI_API_KEY="your_grok_api_key_here"
    # WHATSAPP_API_KEY="your_evolution_api_key_here"
    # WHATSAPP_INSTANCE_URL="http://localhost:8080"
    # WHATSAPP_INSTANCE_NAME="main"
    # WHATSAPP_RECIPIENT="1234567890@s.whatsapp.net"
    ```
6.  **Run Quality Checks**: Ensure everything is set up correctly by running the same baseline checks used in CI.
    ```bash
    python -m pytest -q
    ruff check .
    ```

## Development Workflow

- **Branching**: Create a new branch for each feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b bugfix/issue-number`.
- **Coding Style**: Adhere to PEP 8 and keep `ruff check .` passing.
- **Testing**:
  - Add unit tests for new features and bug fixes, especially for orchestration logic, tools, resources, and prompts.
  - Include integration tests simulating multi-LLM workflows.
  - Automate coverage reporting.
- **Commit Messages**: Write clear and concise commit messages.

## Submitting a Pull Request (PR)

1.  Push your changes to your forked repository.
2.  Open a Pull Request from your branch to the `main` branch of the `Introduction-to-MCP` repository.
3.  Provide a clear description of your changes.
4.  Ensure your PR passes all CI/CD checks (linting, testing, build validation).

## Security Vulnerabilities

If you discover a security vulnerability, please report it responsibly as detailed in our SECURITY.md file.

## Roadmap

You can view the project's current and future capabilities on the Capabilities Roadmap.

## Connect with the Architect

For any questions or discussions, you can reach out to the project architect:

- **LinkedIn:** www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
- **GitHub:** https://github.com/RobynAwesome/

Thank you for your interest in contributing to `orch`!
