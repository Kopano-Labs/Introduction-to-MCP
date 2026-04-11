#!/usr/bin/env python
"""
Kopano Context — AGI Control Plane
Entry point for the Kopano CLI application.

Kopano Context is a multi-agent orchestration framework implementing
the Model Context Protocol (MCP). It coordinates intelligent discussions
between AI agents from any provider, guided by a Smart Moderator AI.

Usage:
    kopano serve launch --topic "..." --agents "agent-id" --moderator "mod-id"
    kopano serve api
    kopano agents list
    kopano agents config <id> --provider google --model gemini-1.5-pro

The legacy `orch` command is also available for backwards compatibility.
"""
from kopano.cli import app


def main():
    """
    Main entry point for the Kopano Context CLI application.
    Delegates to the Typer application instance, which handles
    command-line argument parsing and dispatches to the correct subcommand.
    """
    app()

if __name__ == "__main__":
    main()
