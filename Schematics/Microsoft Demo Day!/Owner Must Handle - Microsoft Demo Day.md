---
title: Owner Must Handle - Microsoft Demo Day
created: 2026-04-09
updated: 2026-04-10
author: Codex
tags:
  - owner
  - demo
  - microsoft
  - azure
  - checklist
priority: critical
status: active
---

# Owner Must Handle - Microsoft Demo Day

> Direct owner checklist for what cannot be closed by Codex alone.
> If a task needs credentials, platform access, account decisions, spend approval, or final narrative choice, it belongs here.

## Already Done For You

- Orch-only demo route is written and rehearsed in [Orch Demo Script - 2026-04-09](Orch%20Demo%20Script%20-%202026-04-09.md).
- The conservative live route is locked as `Council -> Labs -> Console send -> Forge view -> Admin audit`.
- Azure CLI `az` and Azure Developer CLI `azd` are installed locally in a non-admin path.
- `/api/labs/microsoft-readiness` exists and reports live readiness.
- Orch Labs already exposes the Microsoft readiness surface.
- App Insights wiring exists in both backend and GUI, but it is not active until real connection strings are supplied.

## Safe Default If You Do Nothing Else

- The demo can still run on the Orch-only safe route.
- If the full KasiLink path is not ready, present the Orch shell and say the wider marketplace path is still being connected with production credentials and live data access.
- If Azure is not fully wired, present Microsoft as `readiness and buyer narrative`, not as a fully connected live Azure stack.

## Minimum Needed To Close 2026-04-08

Without the items below, the April 8 countdown row stays owner-blocked even though the repo, Orch shell, and local rehearsal route are already working.

- [ ] provide valid Clerk publishable and secret keys
- [ ] allowlist the current machine in Atlas or otherwise provide live Mongo reachability
- [ ] approve whether Demo Day is `ORCH-ONLY SAFE ROUTE` or `FULL KASILINK STORY`
- [ ] if you want Microsoft presented as a live connected stack, complete Azure sign-in and real env/resource wiring

Use the existing backend and GUI `.env.example` files as the source for what values still need to be filled with real secrets and resource identifiers.

## Owner Blockers You Must Clear

### Access And Credentials

- [x] provide valid Clerk publishable and secret keys for live authenticated rehearsal ✅ 2026-04-10
- [ ] allowlist the current machine in Atlas or otherwise provide live Mongo reachability
- [ ] decide whether RapidAPI-backed WhatsApp and Google Search providers are required in the live story
- [ ] if WhatsApp is in the live story, ensure the needed provider subscriptions or keys are active

### Demo Decisions You Must Make

- [ ] decide whether Demo Day is `ORCH-ONLY SAFE ROUTE` or `FULL KASILINK STORY`
- [ ] decide whether WhatsApp is `IN SCRIPT` or `DEFERRED`
- [ ] decide whether reward/referral is `IN SCRIPT` or `DEFERRED`
- [ ] decide whether Azure AI Search is `IN DEMO` or `DEFERRED`
- [ ] decide whether managed identity plus RBAC is `IN DEMO` or `DEFERRED`
- [ ] approve the fallback line for any blocked full-stack dependency instead of leaving it vague on the day

## Azure Implemented Features You Still Must Handle

### 1. Azure Sign-In

- [ ] run `az login`
- [ ] confirm `az account show` returns the correct subscription
- [ ] run `azd auth login`
- [ ] lock the exact subscription that will back the demo story

### 2. Hosting Target

These checks already exist in the repo. What is missing is the real target choice and env values.

- [ ] choose `Azure App Service` or `Azure Container Apps` as the demo hosting claim
- [ ] set `AZURE_SUBSCRIPTION_ID`
- [ ] set `AZURE_RESOURCE_GROUP`
- [ ] set either `AZURE_APP_SERVICE_NAME` or `AZURE_CONTAINER_APP_NAME`
- [ ] confirm the chosen hosting target is the one you want to speak about on stage

### 3. Azure OpenAI

Support for this is already wired into the readiness check. It still needs real resource values.

- [ ] create or confirm the Azure OpenAI resource
- [ ] set `AZURE_OPENAI_ENDPOINT`
- [ ] set `AZURE_OPENAI_API_KEY`
- [ ] set `AZURE_OPENAI_DEPLOYMENT`
- [ ] decide whether you will claim live Azure OpenAI in the demo or keep it at readiness level only

### 4. Application Insights

The backend and frontend hooks already exist. They only become real once the connection strings are present.

- [ ] create or confirm the Application Insights resource
- [ ] set `AZURE_APP_INSIGHTS_CONNECTION_STRING`
- [ ] set `VITE_APPLICATIONINSIGHTS_CONNECTION_STRING`
- [ ] verify telemetry is actually arriving before you claim observability live

### 5. Azure AI Search

This is optional right now and should not be claimed unless you complete it.

- [ ] decide `IN DEMO` or `DEFERRED`
- [ ] if `IN DEMO`, set `AZURE_AI_SEARCH_ENDPOINT`
- [ ] if `IN DEMO`, set `AZURE_AI_SEARCH_KEY`
- [ ] if `IN DEMO`, set `AZURE_AI_SEARCH_INDEX_NAME`

### 6. Managed Identity And RBAC

This is also optional for the current state and should not be claimed unless you complete it.

- [ ] decide `IN DEMO` or `DEFERRED`
- [ ] if `IN DEMO`, set `AZURE_CLIENT_ID`
- [ ] if `IN DEMO`, verify the identity has the RBAC permissions you want to describe

## Minimum Demo Day Decisions Still Needed From You

- [ ] approve the final spoken story in [SA Startup Week Demo](SA%20Startup%20Week%20Demo.md)
- [ ] approve the safe route in [Orch Demo Script - 2026-04-09](Orch%20Demo%20Script%20-%202026-04-09.md)
- [ ] approve the owner-facing fallback line if the full KasiLink route is not ready
- [ ] choose whether to present Microsoft as `readiness and buyer narrative` or as `fully connected live Azure stack`

## Owner Fallback Wording

Use these lines if the wider stack is still partial:

- KasiLink fallback: `Today we are showing the Orch shell that powers the operating model while the wider KasiLink marketplace path finishes with production credentials and live data access.`
- Microsoft fallback: `Today Microsoft is shown as a real readiness path with live tooling and surfaced checks; we are not claiming the full Azure stack is connected until sign-in and resource wiring are complete.`

## Day-Of-Demo Owner Checklist

- [ ] open [Microsoft Demo Day!](index.md)
- [ ] open [Orch Demo Script - 2026-04-09](Orch%20Demo%20Script%20-%202026-04-09.md)
- [ ] open [Demo Countdown - April 8-15, 2026](Demo%20Countdown%20-%20April%208-15,%202026.md)
- [ ] confirm auth, database, and telemetry status before presenting
- [ ] run one short smoke test on the exact surface you will present
- [ ] keep the fallback route ready if the wider KasiLink path is still partial

## Current Honest Microsoft Claim

Right now the strongest truthful Microsoft claim is:

- the local Microsoft toolchain is installed
- the Orch Labs Microsoft readiness surface is live
- the repo already supports Azure OpenAI, hosting, and App Insights configuration
- the remaining gap is real subscription sign-in plus real env/resource wiring

Do not claim live Azure OpenAI, live App Insights observability, or live Azure hosting unless the missing owner steps above are actually completed.
