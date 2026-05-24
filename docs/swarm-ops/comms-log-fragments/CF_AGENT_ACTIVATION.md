## 2026-05-24 — CF LPM — swarm agent activation (BlackMass v2.0)

**Operator:** `CF_cloud` (Main Brain roadmap) · **Lead student:** `cassy`  
**Status:** ACTIVATE — Cassy-runnable agents seeded; doctrine slots registered for CF orchestration.  
**Git:** `f6a4324d8562` · **UTC:** `2026-05-24T13:14:27Z`

### Counts (honest)

| Metric | Number |
|--------|--------|
| Registry agents (`SWARM_AGENTS.json`) | **13** |
| Triad (Cassy / Cassey / KC) | **3** |
| Swarm slots 001–004 | **4** |
| Mesh (claude, grok, gemini, copilot) | **4** |
| Cassy-runnable (`cassy_agents.seed.json`) | **7** |
| Doctrine-only (KC ledger + slots + CF) | **6** |
| Cassy WIT diaspora band | **25** tasks |

External Kimi 300 swarm remains **manual-execution-required** — no fake `kimi_ack`.

### Agent roster (send to CF)

| # | id | slot | role | Cassy seed | CF path |
|---|-----|------|------|------------|---------|
| 1 | `cassy` | — | student_primary | yes | cassy_agents.seed.json |
| 2 | `cassey` | — | teacher | yes | cassy_agents.seed.json |
| 3 | `kc` | — | brain | no | doctrine_registry |
| 4 | `kopano` | — | student_studio_alias | yes | cassy_agents.seed.json |
| 5 | `mirror_warden` | 001 | orchestrator_parity | no | doctrine_registry |
| 6 | `kc_apprentice` | 002 | student_audit | no | doctrine_registry |
| 7 | `operational_general` | 003 | teacher_swarm | no | doctrine_registry |
| 8 | `pipeline_drone` | 004 | mesh_worker | no | doctrine_registry |
| 9 | `claude` | — | mesh | yes | cassy_agents.seed.json |
| 10 | `grok` | — | mesh | yes | cassy_agents.seed.json |
| 11 | `gemini` | — | mesh | yes | cassy_agents.seed.json |
| 12 | `copilot` | — | mesh | yes | cassy_agents.seed.json |
| 13 | `cf_cloud` | — | lpm_operator | no | comms_lpm |

### CF activation commands (repo)

```bash
python scripts/kc_swarm_agents_bootstrap.py
python scripts/kc_cassy_activate.py --seed-wit
python scripts/kc_cf_comms_activate.py --emit-only
python scripts/kc_log_append.py mainbrain --kind cf_swarm_activation --summary "CF LPM: Cassy agents activated" ...
```

**Canonical paths:** `docs/swarm-ops/agents/SWARM_AGENTS.json`, `kopano-core/config/cassy_agents.seed.json`, JSONL under `docs/swarm-ops/logs/`.  
**Legacy name:** Orch → Cassy — see `docs/swarm-ops/LEGACY_ORCH.md`.

---
