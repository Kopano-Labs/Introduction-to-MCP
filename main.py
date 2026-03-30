#!/usr/bin/env python
"""
Main entry point for the orch CLI application.
"""
from orch.orch.cli import app


def main():
    """
    This function serves as the main entry point for the orch CLI application.
    It calls the Typer application instance, which handles command-line argument
    parsing and execution.
    """
    app()

if __name__ == "__main__":
    main()
