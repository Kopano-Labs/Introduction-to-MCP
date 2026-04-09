# Azure Deployment Plan

## Status

In Progress

## Date

2026-04-09

## Mode

MODIFY

## Objective

Prepare Orch and the local demo stack to show a real Microsoft-backed story for Demo Day:
- working local Azure CLI and Azure Developer CLI
- Azure environment readiness checks inside Orch Labs
- Azure Monitor / Application Insights instrumentation hooks for the FastAPI backend and demo GUI
- explicit environment examples for required Azure resources

## Current Workspace

- Backend: FastAPI app in `orch/orch`
- Frontend: Vite React app in `orch/gui`
- Related web app: Next.js app in `KasiLink`
- Existing Azure story currently lives mostly in playbooks, registry metadata, and deterministic connector actions

## Constraints

- Current shell is non-admin, so Windows MSI installs are not the preferred path
- Demo must remain locally runnable on `127.0.0.1:8000`
- No destructive changes to existing user files or directories
- Validation and deployment to Azure are separate follow-up phases

## Recipe

AZCLI + app-level wiring

## Planned Steps

1. Install Azure CLI and Azure Developer CLI in a non-admin, per-user way.
2. Add Microsoft readiness inspection to Orch Labs.
3. Add Azure Monitor / Application Insights telemetry hooks to the FastAPI backend.
4. Add browser-side Application Insights support to the Orch GUI.
5. Add `.env.example` guidance for required Azure resources and keys.
6. Replace the deterministic Azure connector playbook execution with a live readiness report.
7. Verify builds, local API responses, and GUI rendering.
8. Update Schematics with exact readiness status and remaining blockers.

## Azure Resources Expected

- Azure subscription
- Azure OpenAI resource and deployment
- Application Insights resource
- App Service or Container Apps target
- Optional: Azure AI Search
- Optional: Entra app registration / managed identity

## Validation Handoff

After preparation is complete, update this plan to `Ready for Validation` and run the Azure validation pass.
