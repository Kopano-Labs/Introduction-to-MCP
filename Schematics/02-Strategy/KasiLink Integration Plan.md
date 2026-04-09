---
title: KasiLink Integration Plan
created: 2026-04-05
updated: 2026-04-05
author: Robyn
tags:
  - strategy
  - kasilink
  - integration
  - orch
  - township
priority: critical
status: active
---

# KasiLink + Orch Integration Plan

> Orch as a subsidiary AI feature within KasiLink — powering AI capabilities without replacing KasiLink's objective.
> See also: [Orch Blueprint](../01-Mission/Orch%20Blueprint.md), [Microsoft Contract Strategy](Microsoft%20Contract%20Strategy.md), [SA Startup Week Demo](../Microsoft%20Demo%20Day!/SA%20Startup%20Week%20Demo.md)

## Context

**Problem:** South Africa's youth unemployment is critically high, and the informal township economy (R1 trillion annually) lacks digital infrastructure.

**KasiLink** (kasi-link.vercel.app) — Next.js/TypeScript PWA connecting township youth with local gigs. Clerk auth, MongoDB Atlas, Vercel deployment. MVP target: end of April 2026.

**Orch** (this repo) — Python multi-agent orchestration framework with FastAPI, 20+ tools, MCP, WhatsApp bridge. Phase 4 in progress.

## Strategic Focus

1. **Youth Unemployment** (Skills-Based Services) — via KasiLink gig marketplace
2. **Load Shedding Impact** on Business Operations — via KasiLink scheduling intelligence
3. **Township Services + Youth Gig Economy** — as the market vertical

## Architecture

```
KasiLink (Next.js on Vercel)
    |
    |--- /api/orch/[...proxy]/route.ts (forwards Clerk JWT)
    |
    v
Orch FastAPI (Railway / Azure)
    |--- /api/kasilink/match        -> AI gig matching
    |--- /api/kasilink/sentiment    -> Review scoring
    |--- /api/kasilink/forecast     -> Demand forecasting
    |--- /api/kasilink/loadshedding -> Schedule + gig safety
    |--- /api/kasilink/moderate     -> Content moderation
    |--- /api/kasilink/dashboard    -> AI activity data
    |--- /ws/kasilink/live          -> Real-time reasoning
    |--- /api/kasilink/notify       -> WhatsApp notifications
```

## Tool Mapping

| Orch Tool | KasiLink Feature | Hack Day? |
|-----------|-----------------|-----------|
| sentiment_analyzer | Review sentiment scoring | YES |
| forecaster | Demand forecasting per area | YES |
| web_scraper | Loadshedding schedule | YES |
| anomaly_detector | Suspicious booking patterns | NO |
| social_monitor | Community sentiment | NO |
| security | Content moderation | NO |
| Simulation engine | AI Council gig matching | YES |
| WhatsApp bridge | Gig notifications | YES |

## Phased Roadmap

### Phase 1: Hack Day + MVP (April 5-30, 2026)
- Orch KasiLink API gateway
- Deploy to Railway
- AI gig matching + loadshedding + WhatsApp notifications
- **Deliverable:** SA Startup Week demo

### Phase 2: Polish + Community (May 2026)
- Full AI Dashboard
- Demand forecasting
- Community moderation
- Personalized recommendations

### Phase 3: Scale + Microsoft (June-September 2026)
- Azure Container Apps migration
- Azure OpenAI Service
- POPIA compliance
- Case study publication

## Files to Create/Modify

| File | Action |
|------|--------|
| `orch/orch/kasilink_api.py` | CREATE |
| `orch/orch/tools/loadshedding.py` | CREATE |
| `orch/orch/tools/gig_matcher.py` | CREATE |
| `orch/orch/config.py` | MODIFY |
| `orch/orch/api.py` | MODIFY |
| `orch/orch/bridge.py` | MODIFY |
| `orch/orch/simulator.py` | MODIFY |
| `orch/orch/cli.py` | MODIFY |
