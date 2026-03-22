![Logo](/README-banner.jpg)

# Kholofelo Robyn Rababalela — Introduction to MCP

Freelance Web Developer · Computer Engineering Student 📍 Cape Town, Western Cape, South Africa

## Tech Stack
Python • uv • Anthropic MCP SDK • Claude AI

## About
A focused project demonstrating how to build both Model Context Protocol (MCP) servers and clients using the Python SDK. This repository explores MCP's three core primitives—tools, resources, and prompts—and shows how they integrate seamlessly with Claude AI to create powerful applications without writing extensive integration code.

## Sections
* **Servers** — Implementation of custom Python MCP servers
* **Clients** — Building client applications to communicate with the servers
* **Tools** — Exposing executable Python functions to Claude
* **Resources** — Providing contextual file and API data to the AI
* **Prompts** — Structuring interactions for optimal AI responses

## Features
⚡ Built with the official Anthropic Python SDK
🚀 Fast dependency management and resolution using `uv`
🤖 Direct integration with Claude AI capabilities
🔐 Secure local execution of AI-augmented tools
📱 Fully documented and structured codebase
🚀 Ready for immediate local deployment

## Setup

```bash
# Initialize the virtual environment and project
uv init

# Install the project and dependencies in editable mode
uv pip install -e .

# Activate the virtual environment (Windows PowerShell)
.\.venv\Scripts\activate
# OR if using your specific CLI environment
.\.CLI_Project\Scripts\activate
