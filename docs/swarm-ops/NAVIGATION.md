# Swarm ops — source of truth (navigation)

**Authoritative index:** this file. Other entry points (`index.md`, runbook) should link here to avoid drift.

| Artifact | Path | Role |
|----------|------|------|
| Doctrine (proof bar, Kimi vs Cursor, handoff) | [SWARM_OPERATIONS.md](./SWARM_OPERATIONS.md) | Rules |
| Git + proof notebook (commands aligned to repo) | [GIT_AND_PROOF_NOTEBOOK.md](./GIT_AND_PROOF_NOTEBOOK.md) | Reference |
| Kimi activation payload | [PAYLOAD_KIMI_300_ACTIVATION.md](./PAYLOAD_KIMI_300_ACTIVATION.md) | External paste |
| Kimi ACK capture format | [KIMI_ACK_FORMAT.md](./KIMI_ACK_FORMAT.md) | Standard receipt text |
| JSONL schema + CLI | [logs/README.md](./logs/README.md) | Append + validate |
| Obsidian comms seed snippet | [CHIEF_SEED_OBSIDIAN_COMMS.md](./CHIEF_SEED_OBSIDIAN_COMMS.md) | Vault mirror |
| Review log (machine) | [logs/KC Review Log.jsonl](./logs/KC%20Review%20Log.jsonl) | Student / teacher |
| Main brain log (machine) | [logs/KC Main Brain Log.jsonl](./logs/KC%20Main%20Brain%20Log.jsonl) | Orchestrator / Kimi ACK |
| Append / validate CLI | `scripts/kc_log_append.py` | Enforcement surface |
| Git sync monitor (static HTML) | [tools/git-sync-monitor.html](./tools/git-sync-monitor.html) | Open in browser; pairs with `scripts/git_sync_monitor.py` |
| KC Swarm Console (wireframe HTML) | [tools/kc-swarm-console-wireframe.html](./tools/kc-swarm-console-wireframe.html) | Studio or Next shell: KC→Cassey, BFF, proof strip; aligns CI with `swarm-proof.yml` |
| KC Swarm Console (architecture prose) | [KC_SWARM_CONSOLE_ARCHITECTURE.md](./KC_SWARM_CONSOLE_ARCHITECTURE.md) | BFF model, flow, CI vs optional `proof_gate`, citations |
| KC Swarm Console (GUI IA spec) | [KC_SWARM_CONSOLE_WIREFRAME_SPEC.md](./KC_SWARM_CONSOLE_WIREFRAME_SPEC.md) | Four-column layout, flows, branch protection notes |
| Unified guard CLI | `scripts/kc_guard.py` | `status` / `validate` / `proof` / `all` / `watch`; delegates to `git_sync_monitor` + `kc_log_append` |

**CLI quick reference**

```bash
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check   # review last student/audit + main last non-bootstrap receipt
python scripts/kc_guard.py all                 # git sync monitor + validate + proof-check (one entrypoint)
python scripts/kc_guard.py all --require-swarm-ack   # stricter: at least one swarm_ack + evidence_urls in Main Brain log
python scripts/kc_log_append.py review --strict-proof --role student --phase audit --summary "..." --commands ... --exit-code 0 --evidence-url https://...
python scripts/kc_log_append.py kimi-ack --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md --status acknowledged --notes "Swarm initiated" --evidence-url https://...
```
