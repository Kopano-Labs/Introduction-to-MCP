# Kimi acknowledgement (KIMI_ACK) — standard capture

Use this block when Kimi (or any external orchestrator) acknowledges a payload. Paste into vault comms and/or capture via CLI `kimi-ack` so JSONL stays machine-parseable.

## Bracket format (human paste)

```
[KIMI_ACK]
timestamp: 2026-05-16T14:30:00Z
payload_ref: docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md
status: acknowledged | rejected | partial
notes: <free text; include run id or URL if any>
```

## JSON (CLI `kimi-ack`)

The append tool writes `kc_main_brain_log_v1` with `kind: "kimi_ack"` and a `kimi_ack` object:

| Field | Required | Description |
|-------|----------|-------------|
| `timestamp` | yes | ISO8601 UTC (default: now) |
| `payload_ref` | yes | Path or URI to the payload |
| `status` | yes | e.g. `acknowledged`, `rejected`, `partial` |
| `notes` | no | Free text |

The `summary` field duplicates the bracket block for grep-friendly audits.
