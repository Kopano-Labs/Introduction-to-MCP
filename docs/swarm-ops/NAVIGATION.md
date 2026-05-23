# Swarm ops — source of truth (navigation)

**Authoritative index:** this file. Other entry points (`index.md`, runbook) should link here to avoid drift.

| Artifact | Path | Role |
|----------|------|------|
| Doctrine (proof bar, Kimi vs Cursor, handoff) | [SWARM_OPERATIONS.md](./SWARM_OPERATIONS.md) | Rules |
| Verified prod hosts (DNS/HTTP probe) | [VERIFIED_ENDPOINTS.md](./VERIFIED_ENDPOINTS.md) | Use in proof rows; re-probe before demos |
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
| Servitude Triad (unified modes) | [SERVITUDE_TRIAD.md](./SERVITUDE_TRIAD.md) | Grit + Realism + Aesthetics — not split |
| Main Brain roadmap (production gate) | [MAIN_BRAIN_ROADMAP.json](./MAIN_BRAIN_ROADMAP.json) | Seed before/after; Black Mass line |
| Swarm agents + Cassy apprenticeship | [agents/SWARM_AGENTS.json](./agents/SWARM_AGENTS.json) | All agents bind student=cassy |
| Black Mass protocol versions | [BLACK_MASS_PROTOCOL.md](./BLACK_MASS_PROTOCOL.md) | Mask v0.5 → Mass v1.5 → v2.0 |
| Realism vs drill theater | [apprenticeship/REALISM.md](./apprenticeship/REALISM.md) | What counts; Cursor accountability |
| KC Apprenticeship 250 (stewardship) | [apprenticeship/STEWARDSHIP.md](./apprenticeship/STEWARDSHIP.md) | Machine drill — not public graduation |
| Apprenticeship task ledger | [apprenticeship/kc_apprenticeship_250.json](./apprenticeship/kc_apprenticeship_250.json) | 10×25 tasks; checkpoints in [apprenticeship/checkpoints/](./apprenticeship/checkpoints/) |
| KC status @ 50/100/150/200/250 | [apprenticeship/checkpoints/README.md](./apprenticeship/checkpoints/README.md) | `kc_status_at_*.json` + `KC_STATUS_AT_*.md` |
| KC opinion (memory voice) | [apprenticeship/KC_OPINION.md](./apprenticeship/KC_OPINION.md) | Where teacher_review lives; Save/Watch/Kill |
| Main Brain / vault audit | [apprenticeship/MAIN_BRAIN_AUDIT.md](./apprenticeship/MAIN_BRAIN_AUDIT.md) | Canonical vs Schematics mirror |
| Mirror logs to Schematics vault | `python scripts/kc_sync_vault_logs.py` | After JSONL append |

**CLI quick reference**

```bash
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check   # review last student/audit + main last non-bootstrap receipt
python scripts/kc_guard.py all                 # sync + validate + proof-check + doc host drift (default)
python scripts/kc_guard.py all --no-check-doc-hosts  # skip kopanolabs URL scan in swarm-ops docs
python scripts/kc_guard.py all --require-swarm-ack   # stricter: swarm_ack or kimi_ack + evidence_urls (after Kimi)
python scripts/kc_guard.py doctrine-doc-hosts  # host drift only
python scripts/kc_guard.py doctrine-swarm-ack  # swarm/kimi ack only
python scripts/kc_swarm_agents_bootstrap.py      # SWARM_AGENTS.json → orch_agents.seed.json
python scripts/kc_cassy_activate.py --seed-wit  # Cassy lead student + WIT 25 band
python scripts/kc_main_brain_roadmap.py gate    # production entry gate
python scripts/kc_apprenticeship_activate.py   # manifest + seed kopano-core/.kc/context_store.json
```

**Open PR:** https://github.com/Kopano-Labs/Introduction-to-MCP/compare/master...codex/kc-sovereign-gui-full-dev?expand=1
python scripts/kc_log_append.py review --strict-proof --role student --phase audit --summary "..." --commands ... --exit-code 0 --evidence-url https://...
python scripts/kc_log_append.py kimi-ack --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md --status acknowledged --notes "Swarm initiated" --evidence-url https://...
```
