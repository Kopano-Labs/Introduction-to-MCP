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

## CLI (strict proof)

```bash
python scripts/kc_log_append.py kimi-ack \
  --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md \
  --status acknowledged \
  --evidence-url "https://<durable-external-artifact-not-in-git>" \
  --strict-proof
```

`--evidence-url` must be a **real** Kimi (or external runner) artifact: share link, export, job URL, etc. Placeholder or in-repo-only URLs do not satisfy the proof bar.

**Do not use a “demo bypass” URL** (e.g. `demo-bypass-receipt-placeholder` on your own site). `--strict-proof` rejects obvious bypass markers. That keeps CI and auditors honest: either you have an external Kimi receipt, or swarm status stays `manual-execution-required`.

## Unlock strict gate

After a genuine external receipt exists:

```bash
python scripts/kc_guard.py all --require-swarm-ack
```

`--require-swarm-ack` accepts Main Brain rows with `kind` **`kimi_ack`** (this subcommand) or **`swarm_ack`** (`mainbrain --kind swarm_ack`), each with non-empty `evidence_urls`.
