# Paste into Obsidian `Schematics/04-Updates/comms-log.md` (optional)

Prepend when you want the vault ledger to reference the **git-tracked** swarm doctrine and KC JSONL paths:

```markdown
## 2026-05-16 — KC JSONL + SWARM DOCTRINE (repo mirror)

**Repo paths:** `docs/swarm-ops/logs/KC Review Log.jsonl`, `docs/swarm-ops/logs/KC Main Brain Log.jsonl` — [logs README](docs/swarm-ops/logs/README.md); append: `python scripts/kc_log_append.py`. **SOP:** [Swarm Ops](docs/swarm-ops/SWARM_OPERATIONS.md). **Payload:** [Kimi 300](docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md).

---
```

Adjust relative links if your Obsidian root is not the Kopano repo root.

## CF LPM — activate created agents

Generate the roster block and Main Brain receipt:

```bash
python scripts/kc_cf_comms_activate.py --prepend-vault
```

Canonical copy (always git-tracked): `docs/swarm-ops/comms-log-fragments/CF_AGENT_ACTIVATION.md`

**Counts:** 13 registry · 7 orch-runnable · 4 swarm slots (001–004) · 4 mesh · CF receives comms to orchestrate doctrine slots + autonomic flows.
