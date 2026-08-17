# Snowflake v0.2 — Governed Evidence Adapter

Status: **POC / live-capable / fail-closed**

This promotes the Frontier Harness Snowflake path from a prepared row to a **live-capable SQL API adapter** without transferring canonical state to Snowflake.

## Authority boundary

```text
KPGS governed telemetry row
        |
        v
short-lived capability lease
        |
        +-- snowflake.telemetry.append
        +-- KPGS_FRONTIER.EVIDENCE.FRONTIER_TELEMETRY
        +-- external secret reference
        |
        v
Snowflake SQL API adapter
        |
        v
analytical/evidence copy only
```

The adapter rejects semantic input, raw prompts, provider response text and private payload fields before request preparation.

## Authentication

The repository stores **no credential**. A lease contains only a secret-provider reference such as `env://KPGS_SNOWFLAKE_PAT`. Supported SQL API token declarations are `PROGRAMMATIC_ACCESS_TOKEN`, `OAUTH`, and `KEYPAIR_JWT`.

## Gate

```bash
python governance/kpgs-vnext/frontier-harness/snowflake/validate_snowflake_adapter.py
```

The gate performs no network request. It proves scoped-lease enforcement, expiry rejection, bind-variable request construction, semantic/private-field rejection, and secret-free receipts.

## Promotion boundary

A real Snowflake write is authorized only after `bootstrap.sql` has been applied, a least-privilege role can append to `FRONTIER_TELEMETRY`, KPGS issues a current short-lived lease bound to `kpgs-frontier-harness-snowflake-v0.2`, and the referenced external token resolves at runtime.

Snowflake remains an analytical copy; the local KPGS receipt remains authoritative.
