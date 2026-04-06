# Braintrust Setup for Orch

## Environment keys

Add these to `.env`:

```env
# Phase 5 (Evals)
BRAINTRUST_API_KEY=bt-...
BRAINTRUST_PROJECT_ID=...
BRAINTRUST_DEFAULT_PROJECT=...  # optional, defaults to PROJECT_ID
BRAINTRUST_BASE_URL=https://api.braintrust.dev
BRAINTRUST_EVENTS_PATH=         # optional: set only if you have a valid ingest endpoint

# Phase 6 (Observations)
OBSERVATION_BRAINTRUST_API_KEY=bt-...
OBSERVATION_BRAINTRUST_PROJECT_ID=...
OBSERVATION_BRAINTRUST_BASE_URL=https://api.braintrust.dev
OBSERVATION_BRAINTRUST_EVENTS_PATH=
```

## CLI functions

```powershell
orch braintrust status
orch braintrust eval --name "quality-check" --input "prompt" --output "answer" --score 0.92
orch braintrust observe --event "session_started" --metadata "{\"source\":\"cli\"}"
```

## Behavior

- Local logging is always enabled (stored in `creator_analytics_events`).
- Remote posting is optional and only runs when a valid events path is configured.
