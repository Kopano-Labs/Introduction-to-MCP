# Cursor Research Notes — Abilities / Tools / Rules / MCP

Research date: 2026-08-29.

Purpose: ground the capability vocabulary used in the Forge failure analysis. These notes describe Cursor's documented capabilities; they are not proof that AntiGravity exposes every Cursor capability.

## Cursor Agent composition

Cursor's Agent overview describes an agent as the combination of:

- instructions/rules;
- tools;
- a selected model.

## Documented tool classes

Cursor documents agent tools for:

- searching files/folders;
- web search;
- retrieving rules;
- reading files, including supported images;
- editing files;
- running shell commands;
- browser interaction/testing;
- image generation;
- asking questions.

## Environment access

Cursor's terminal documentation states that shell commands are run directly in the terminal, subject to Cursor's run mode/sandbox configuration. This demonstrates the important architectural distinction between a coding agent wired into an execution environment and a remote conversational model without such access.

Cursor's browser documentation describes browser navigation, clicking, typing, scrolling, screenshots, console output, and network-traffic inspection.

## MCP

Cursor documents MCP as a protocol for connecting the agent to external tools and data sources. MCP capability is therefore an external-access mechanism, not intrinsic model knowledge.

## Rules

Cursor documents Project Rules, User Rules, Team Rules, and `AGENTS.md` as reusable instructions/context. Rules guide behavior but do not themselves grant physical/environment access.

## Official sources

- https://cursor.com/docs/agent/overview
- https://cursor.com/docs
- https://prod.cursor.com/help/ai-features/agent
- https://prod.cursor.com/docs/agent/tools/terminal
- https://prod.cursor.com/docs/agent/tools/browser
- https://prod.cursor.com/docs/mcp
- https://prod.cursor.com/docs/rules
