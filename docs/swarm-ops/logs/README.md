# KC execution logs (JSONL)

**Git-tracked paths** (repo root):

| File | Purpose |
|------|---------|
| `docs/swarm-ops/logs/KC Review Log.jsonl` | **Student / Teacher** apprenticeship loop — audits, commands run, exit codes, verdicts. |
| `docs/swarm-ops/logs/KC Main Brain Log.jsonl` | **Orchestrator / Chief** receipts — Kimi acknowledgements, swarm events, mirror checks, handoff summaries. |

## Line format

Each line is one JSON object (UTF-8). Required field: `schema` (`kc_review_log_v1` or `kc_main_brain_log_v1`) and ISO8601 UTC `ts`.

### `kc_review_log_v1`

| Field | Type | Notes |
|-------|------|-------|
| `role` | string | `student` \| `teacher` \| `system` (bootstrap rows) |
| `phase` | string | e.g. `propose`, `audit`, `review_decision`, `bootstrap` |
| `agent_id` | string? | e.g. `002` |
| `summary` | string | Human-readable outcome |
| `commands` | string[]? | Commands or job names executed |
| `exit_code` | int? | |
| `git_sha` | string? | |
| `branch` | string? | |
| `evidence_urls` | string[]? | CI run URLs |
| `ref_review_id` | string? | |
| `teacher_verdict` | string? | `approved` \| `rejected` |

### `kc_main_brain_log_v1`

| Field | Type | Notes |
|-------|------|-------|
| `kind` | string | `swarm_ack`, `swarm_event`, `mirror_warden`, `manual`, `bootstrap`, … |
| `summary` | string | |
| `commands` | string[]? | |
| `exit_code` | int? | |
| `git_sha` | string? | |
| `evidence_urls` | string[]? | |
| `payload_ref` | string? | e.g. `docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md` |
| `kimi_ack` | object? | Structured ACK (`timestamp`, `payload_ref`, `status`, optional `notes`); use `kimi-ack` subcommand |

Machine-readable schema sketches live under `docs/swarm-ops/schemas/` (`kc_review_log_v1`, `kc_main_brain_log_v1`).

## Validate & proof gate

```bash
# Structural validation (default: both KC logs)
python scripts/kc_log_append.py validate

# Demo / merge gate: validate + last student/audit row + last non-bootstrap main-brain row must carry exit_code + evidence_urls
python scripts/kc_log_append.py proof-check
```

## Append from CLI

Use **`--strict-proof`** on `review` / `mainbrain` / `kimi-ack` when you want the append to **fail** unless `exit_code` is set and at least one `--evidence-url` is present (stderr warns if `git_sha` is missing).

```bash
python scripts/kc_log_append.py review --strict-proof --role student --phase audit --summary "Smoke OK" \
  --commands python scripts/demo_day_smoke.py -- --strict --exit-code 0 \
  --evidence-url "https://ci.example/run/123"

python scripts/kc_log_append.py mainbrain --strict-proof --kind swarm_ack --summary "Kimi acknowledged ISIS activation" \
  --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md --exit-code 0 \
  --evidence-url "https://ci.example/run/124"

python scripts/kc_log_append.py kimi-ack --strict-proof --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md \
  --status acknowledged --notes "Paste Kimi thread id" --exit-code 0 --evidence-url "https://..."
```

## Obsidian mirror

If your vault lives under `Schematics/`, paste the snippet from [CHIEF_SEED_OBSIDIAN_COMMS.md](../CHIEF_SEED_OBSIDIAN_COMMS.md) into `Schematics/04-Updates/comms-log.md` when you want the ledger to reference this repo copy.
