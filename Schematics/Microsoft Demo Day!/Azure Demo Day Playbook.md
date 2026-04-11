---
title: Azure Demo Day Playbook
created: 2026-04-06
updated: 2026-04-11
author: Robyn
tags:
  - azure
  - demo-day
  - playbook
  - kopano-labs
priority: critical
status: active
---

# Azure Demo Day Playbook

> Hub: [Microsoft Demo Day!](index.md)
> Owner actions: [Owner Must Handle - Microsoft Demo Day](Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)

```
┌──────────────────────────────────────────────────────┐
│          DEMO DAY READINESS DASHBOARD                │
│             (April 11 Evening Update)                │
├──────────────────────────────────────────────────────┤
│  Kopano-Only Safe Route .......... █████████████ 100%  │
│  Full KasiLink Story ........... ███████░░░░░░ 60%   │
│  Azure / Microsoft Surface ..... ██████████░░░ 85%   │
│  Demo Narrative & Script ....... █████████░░░░ 75%   │
│  Schematics Documentation ...... ██████████░░░ 85%   │
└──────────────────────────────────────────────────────┘
```

## Current Position

We are executing Phase 8 expansion on top of the Phase 6 Kopano Labs foundation, with Phase 7 and Phase 9 still active in parallel.

## Current Readiness

- local Azure CLI `az` is installed and working
- local Azure Developer CLI `azd` is installed and working
- Kopano Labs exposes `/api/labs/microsoft-readiness`
- the vault contains strong Azure-readiness proof, but current session truth should stay conservative unless the full check set is re-verified again live
- remaining blockers still include owner-side sign-in, environment truth, and broader KasiLink connectivity where applicable

## Azure Readiness Story

- Host the Labs API and GUI on Azure app surfaces that can demo reliably.
- Use Azure identity, observability, and AI services as the public buyer-facing readiness story.
- Keep AWS parity visible, but do not let it dilute the Demo Day message.
- Azure is a strong demo story, but current live claims must remain evidence-bound to the latest verified session state.

## Execution Tracks

### Track 1: Application Surface

- Verify the FastAPI control plane can run cleanly as the main demo backend.
- Verify the Kopano Labs GUI is buildable and deployable from the current GUI workspace.
- Keep Forge, Kopano Code, and MCP Console as the demo centerpiece.

### Track 2: Azure Services

- Azure OpenAI for model-backed orchestration and multilingual upgrades
- Azure App Service or Container Apps for the API and Labs surface
- Azure AI Search for future knowledge and connector indexing
- Application Insights for observability and demo telemetry
- RBAC and managed identity for clean enterprise posture

### Track 3: Demo Narrative

- Show Kopano Labs as the command center
- Show Forge as the creator execution surface
- Show MCP Console as the install, connector, and orchestration layer
- Show Azure as the deployment and buyer-readiness backbone

## Suggested Commands

```bash
az login
az account show
azd auth login
pip install -e .
kopano serve api
cd orch/gui
npm run build
```

## Ready-Next Items

- Replace deterministic connector execution with live Azure provisioning helpers
- Add Azure environment validation and playbook completion tracking
- Add App Insights or Azure Monitor telemetry for Forge and MCP Console usage

## Honest Microsoft Claim Today

> The strongest **truthful** claim you can make:
>
> *"Kopano has a strong Azure-backed demo story with local tooling, readiness instrumentation, and documented cloud proof. We should only claim the full connected path after the live check set is re-verified in the current session."*

## Bottom Line

| Dimension | Grade | Notes |
|-----------|-------|-------|
| **Kopano demo shell** | **A+** | Hardened, timed, 100% ready |
| **Engineering quality** | **A** | Azure SDK, Mongo drivers, and Telemetry all landed |
| **Documentation** | **A** | Schematics vault is current as of April 11 midnight |
| **Azure / Microsoft story** | **A-** | Strong documented readiness story; live claims should stay conservative until re-verified in-session. |
| **Full KasiLink story** | **C** | Still blocked by Atlas Mongo connectivity |
| **Narrative readiness** | **B-** | Safe route exists; full KasiLink narrative is the remaining gap |
| **Overall Demo Day readiness** | **A** | **Ready to demo Kopano shell and Azure story now.** |

> [!IMPORTANT]
> Azure is a strong part of the demo story, but the full live claim should stay evidence-bound. The broader risk stack still includes owner-side auth, Atlas MongoDB connectivity, and wider KasiLink proof.
