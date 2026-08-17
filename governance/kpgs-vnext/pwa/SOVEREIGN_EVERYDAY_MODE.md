# Sovereign Everyday Mode

Issue: #41

## Goal

Expose KPGS capabilities to ordinary users through a mobile-first Adaptive PWA that feels warm, responsive and simple while keeping authority, evidence and recovery explicit underneath.

## Experience contract

The default surface should answer four questions without infrastructure jargon:

1. **What can I do here?**
2. **What is happening now?**
3. **Why does the system need my approval or information?**
4. **What can I do if this fails or I change my mind?**

## Interaction profile

KPGS may adapt bounded presentation characteristics:

- warmth
- formality
- detail density
- pace
- initiative
- explanation style

These settings affect prompts, message composition, progressive disclosure and—where supported by the selected model gateway—bounded inference parameters such as temperature/top-p.

### Critical terminology boundary

This is **runtime interaction adaptation**, not model-weight fine-tuning.

Actual fine-tuning/training requires a separate governed pipeline with datasets, consent/privacy rules, evaluation, provenance and promotion gates. The PWA must never claim that a user's preference slider is retraining the model.

## Warm adaptive target

Desired interaction qualities:

- warm without flattery dependence;
- direct without sounding bureaucratic;
- context-aware without silently importing unrelated history;
- proactive within leased authority;
- concise by default with expandable detail;
- clear about uncertainty and verification state.

## Progressive disclosure

### Everyday view

Show:
- one primary next action;
- simple task status;
- permissions in plain language;
- recovery/undo when available;
- a short reason when KPGS blocks an action.

### Technical detail view

Optionally expose:
- governing specification;
- capability scope;
- renter/skill versions;
- evidence references;
- connection/transport state;
- release/rollback metadata.

## Offline and reconnection

A network interruption should not look like task failure when canonical work is still recoverable. Use the realtime user states defined by KPGS:

`ready | working | waiting-for-approval | offline | reconnecting | done | failed`

On reconnect, refresh from canonical workflow state before trusting client-only state.

## Preference sovereignty

Interaction preferences should be:

- inspectable;
- editable;
- resettable;
- stored locally by default when practical;
- synced to an account only with explicit policy/consent;
- separate from protected identity/authorization state.

A user profile must not become hidden authority.

## Non-technical usability gate

A pilot workflow is not ready for everyday release unless a user can complete it without needing to understand MCP, KPGS, renters, .NET, WebSockets, schema validation or model serving terminology.
