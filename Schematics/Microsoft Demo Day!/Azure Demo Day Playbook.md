---
title: Azure Demo Day Playbook
created: 2026-04-06
updated: 2026-04-09
author: Robyn
tags:
  - azure
  - demo-day
  - playbook
  - orch-labs
priority: critical
status: active
---

# Azure Demo Day Playbook

> Hub: [Microsoft Demo Day!](index.md)
> Owner actions: [Owner Must Handle - Microsoft Demo Day](Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)

## Current Position

We are executing Phase 8 expansion on top of the Phase 6 Orch Labs foundation, with Phase 7 and Phase 9 still active in parallel.

## Current Readiness

- local Azure CLI `az` is installed and working
- local Azure Developer CLI `azd` is installed and working
- Orch Labs exposes `/api/labs/microsoft-readiness`
- current readiness is `2/6` required checks and `1/3` optional checks ready
- remaining blockers are Azure sign-in plus real Azure OpenAI, App Insights, and hosting env values

## Azure Readiness Story

- Host the Labs API and GUI on Azure app surfaces that can demo reliably.
- Use Azure identity, observability, and AI services as the public buyer-facing readiness story.
- Keep AWS parity visible, but do not let it dilute the Demo Day message.
- Do not claim a fully connected Azure production stack until the owner steps in the checklist are complete.

## Execution Tracks

### Track 1: Application Surface

- Verify the FastAPI control plane can run cleanly as the main demo backend.
- Verify the Orch Labs GUI is buildable and deployable from `orch/gui`.
- Keep Forge, Orch Code, and MCP Console as the demo centerpiece.

### Track 2: Azure Services

- Azure OpenAI for model-backed orchestration and multilingual upgrades
- Azure App Service or Container Apps for the API and Labs surface
- Azure AI Search for future knowledge and connector indexing
- Application Insights for observability and demo telemetry
- RBAC and managed identity for clean enterprise posture

### Track 3: Demo Narrative

- Show Orch Labs as the command center
- Show Forge as the creator execution surface
- Show MCP Console as the install, connector, and orchestration layer
- Show Azure as the deployment and buyer-readiness backbone

## Suggested Commands

```bash
az login
az account show
azd auth login
pip install -e .
orch serve api
cd orch/gui
npm run build
```

## Ready-Next Items

- Replace deterministic connector execution with live Azure provisioning helpers
- Add Azure environment validation and playbook completion tracking
- Add App Insights or Azure Monitor telemetry for Forge and MCP Console usage
