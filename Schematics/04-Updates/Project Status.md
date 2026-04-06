---
title: Project Status
created: 2026-04-03
updated: 2026-04-06
author: Robyn
tags:
  - updates
  - status
  - capabilities
  - roadmap
priority: critical
status: active
---

# orch Project Status & Capabilities

> Current state of the orch project as of 2026-04-06.
> See also: [[Implementation Plan]], [[Orch Blueprint]], [[KasiLink Integration Plan]]

## Current Phase

**Phase 6: Orch Labs** (Google-Labs-style SA impact layer)

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | COMPLETE | Core Multi-Agent Orchestration |
| Phase 2 | COMPLETE | Advanced Moderator + Memory |
| Phase 3 | COMPLETE | Full Tool Use via MCP & WebSocket |
| Phase 4 | COMPLETE | Optimization, Scale, Security, and KasiLink integration layer |
| Phase 5 | COMPLETE | Reliability hardening, CI modernization, and adoption readiness baseline |
| Phase 6 | IN PROGRESS | Orch Labs layer, SA tool registry, Labs API, and GUI gallery |
| Phase 7 | IN PROGRESS | All SA languages, SASL coverage, and speech-impairment-aware access |
| Phase 8 | IN PROGRESS | Cowork surface, Orch Code track, and public-impact studio scaffolding |
| Phase 9 | IN PROGRESS | Research and refinement loop with product-readiness mapping |

## Phase 6 Progress

- [x] CLI simulation history flow corrected
- [x] CLI database test fixture stabilized
- [x] GitHub Actions updated to Python 3.11/3.12
- [x] CI compile check added
- [x] Full suite stabilization
- [x] Labs registry added
- [x] Labs API endpoints added
- [x] Labs GUI mode added
- [x] Criticality model added for Labs tools and phases
- [x] SA language and access API scaffolding added
- [x] Cowork and Orch Code surface scaffolding added
- [x] Product-readiness research map added
- [ ] Additional Labs tools beyond initial registry
- [ ] Deeper accessibility and multilingual runtime implementation

## What orch Can Do

### Multi-Agent Discussions
Orchestrates intelligent, turn-based simulations between agents from various providers (Anthropic, Google, OpenAI, xAI, etc.) using LiteLLM.

### Smart Moderation
Uses a Moderator AI to summarize rounds, prevent tangents, and guide agents toward a specific goal.

### Extensible Tool Use (MCP)
Agents can perform real-world tasks using 20+ registered tools:
- **Filesystem:** `read_file`, `write_file`, `list_directory`, `delete_file`
- **Development:** `execute_code` (Python), Git integration
- **Research:** `search` (Tavily), `search_arxiv`, `scrape_page`
- **Security:** `scan_code_security` (Bandit), `scan_dependencies` (Safety), SecurityAuditor agent
- **Analytics:** `analyze_sentiment`, `detect_anomalies`, `forecast_series`, `ab_test_analysis`
- **Reporting:** `generate_report` (Markdown), `monitor_brand` (Social Media)
- **Data:** `clean_spreadsheet`, `compare_datasets`, `generate_plot`

### Persistent Memory
Logs all discussions to SQLite Data Lake. Uses associative memory to recall context across sessions.

### Real-time Monitoring
Broadcasts to React GUI (Neural Link) via WebSockets. Real-time updates via WhatsApp Gateway, including `/ws/kasilink/live` for KasiLink consumers.

### KasiLink Integration Layer
`/api/kasilink/*` now exposes health, gig matching, sentiment, forecasting, loadshedding, moderation, dashboard, and notification endpoints for the KasiLink frontend/backend bridge.

### Reliability Baseline
CLI simulation tests now operate against a shared in-memory database fixture, and CI validates the package on modern Python versions with both pytest and compile checks.

### Orch Labs Layer
`/api/labs/*` now exposes a Labs registry with categories, tool portfolio, roadmap phases, and criticality labels. The GUI now includes an Orch Labs view for South African public-impact experiments.

### South Africa Language And Accessibility Direction
orch now has explicit roadmap commitment for all official South African languages and speech-impairment-aware support as critical future phases, not optional enhancements.

### Phase 7 Backbone
`/api/labs/languages` and `/api/labs/language-plan` now expose the 12 official South African languages, SASL coverage, AAC-aware access modes, and accessibility-first planning logic.

### Phase 8 Backbone
`/api/labs/cowork` and `/api/labs/launch-config` now expose Cowork Room, Stitch-like canvas direction, Orch Code tracks, and the 50/50 Anthropic/Codex launch-surface mix.

## Capabilities Roadmap

The "100 Capabilities" vision maps to the engineering phases:
- **Phase 1** unlocked: CLI foundation, agent management, basic simulation
- **Phase 2** unlocked: Multi-step reasoning (#91), self-correction (#92), transparent audit trails (#98)
- **Phase 3** unlocked: File/code tools (#1), web research (#11), API access (#31), app connections (#71)
- **Phase 4** unlocked: Fine-tuning data, learning extraction, and KasiLink integration
- **Phase 5** unlocked: external adoption readiness, CI reliability, and release hardening
- **Phase 6** unlocking: Labs catalog, experiment visibility, and SA tool packaging
- **Phase 7** unlocking: multilingual routing, SASL coverage, AAC-aware access, voice/text accessibility
- **Phase 8** unlocking: cowork execution, Orch Code teaching tracks, and creator surfaces
- **Phase 9** unlocking: continuous research, free-vs-premium stack decisions, and roadmap refinement

> Detailed breakdown: see `100_Capabilities_TODO.md` in the repo root.

## Running orch

Currently, `main.exe` (in `dist/`) is a minimal stub. Use the Python CLI:

```bash
pip install -e .
orch --help
```
