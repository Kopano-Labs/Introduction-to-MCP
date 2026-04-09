---
title: Neural Link
created: 2026-04-03
updated: 2026-04-05
author: Robyn
tags:
  - architecture
  - gui
  - websocket
  - react
priority: medium
status: active
---

# Neural Link — Real-Time Agent Visualization

> The React GUI that shows AI agents thinking and responding in real-time.
> See also: [Project Status](../04-Updates/Project%20Status.md), [CLI Specification](CLI%20Specification.md)

## Overview

The Neural Link is orch's real-time visualization layer. It connects to the FastAPI backend via WebSocket and renders agent activity as it happens.

## Key Features

- **Live Council Room** — Real-time visualization of agent thinking/responding
- **Lesson Vault Sidebar** — Browse past discussion sessions
- **Audit Mode** — Forensic inspection of reasoning traces per round
- **Master Override** — Manually score agent quality (0-10 scale) with improvement hints
- **Value Meters** — Visual representation of response quality scores

## Technical Details

- **Stack:** React 19, TypeScript, Vite
- **WebSocket endpoints:** `/ws/live`, `/ws/neural-link`
- **Broadcast Protocol:** The `/broadcast` endpoint allows the simulator to push updates to all connected GUI clients

## Development Notes

- Strict `async def` syntax for all WebSocket handlers
- Rate-limited state history (max 100 updates in memory)
- GUI build served as static files from FastAPI when available

## KasiLink Integration

The Neural Link concept adapts into KasiLink's **AI Dashboard** — showing users how Orch agents process gig matching decisions transparently. See [KasiLink Integration Plan](../02-Strategy/KasiLink%20Integration%20Plan.md).
