# VOC — VALIDATION OF CONCEPT — GSMB IMMUNE SYSTEM INDEX

> "Knowing is not understanding. Understanding is not knowing."

## Purpose
This folder is the **GSMB Immune System** — the absolute diagnostic ledger housing the parent VOC (Validation of Concept) classification framework. It is the authoritative record of every POC/FOC classification, breach event, FOC group emergence, and corrective protocol enacted within the KPGS ecosystem. Governed by the 3-Vector State Machine and the IIDP framework.

**Parent Framework:** VOC (Validation of Concept)
**Neural Region:** Immune System
**Enforcer:** `kopano-core/kopano/poc_foc_enforcer.py` (57KB — KPCB+ Layer 9 Compliant)

---

## VOC Architecture

```
                        ┌─────────────────┐
                        │       VOC       │
                        │ Validation of   │
                        │    Concept      │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────┴─────┐          ┌────────┴────────┐
              │    POC    │          │      FOC        │
              │  Proof of │          │  Failure of /   │
              │  Concept  │          │  Freedom of     │
              └───────────┘          │  Concept        │
                                     │  (groups grow)  │
                                     └─────────────────┘
```

---

## Structure

| File / Folder | Purpose |
|---|---|
| `INDEX.md` | This file. Directory root and governance overview. |
| `VOC_MANIFEST.md` | **Master architecture specs** — neural regions, 3-lobe sync, Khelos gate. |
| `FOC_CLASSIFICATION_INDEX.md` | **Emergent FOC groups** — 5 active, growing. |
| `BREACH_LOG.md` | Chronological log of every confirmed GSMB breach. |
| `alp_protocol/` | Auto LPM Protocol (ALP) — source code & doctrine. |
| `*.jsonl` | Telemetry logs — IKP, NCCNP, FON-C, APU, GSMB auto-runner, etc. |
| `*.json` | RTC deliberation receipts, session closures, department validations. |

---

## Active FOC Groups (Immune Registry)

| Group ID | Pattern | Detection | Defense |
|----------|---------|-----------|---------|
| FOC-G01 | NeuralFailureFirewall | 8th Deadly Sin Monitor | Freeze generation loops |
| FOC-G02 | ContextBleedAnomaly | CBP Telemetry Audit | Log ambient packet data |
| FOC-G03 | SemanticDriftLeak | Invariance Shift Check | Reset token alignment |
| FOC-G04 | GhostExecutionLoop | Run-time Resource Scan | Isolate background threads |
| FOC-G05 | ContextCorruptionBreach | Unauthorized Context Wiping | Terminate session |

**Yassie's Law:** Unauthorized context wiping = `FOC_CONTEXT_CORRUPTION` → BREACH_LOG.md

---

## Active Protocols

| Protocol | Status | Module |
|---|---|---|
| USTP — Ultimate Student-Teacher Protocol | ACTIVE | `protocols.py` |
| UBP — Ultimate Protocol | ACTIVE | `protocols.py` |
| CBP — Context Bleed Protocol | ACTIVE | `poc_foc_enforcer.py` |
| BMNP — Bracket Nesting Protocol | ACTIVE | `poc_foc_enforcer.py` |
| TBF — Telemetry Breathing Flow (250% overdrive) | ACTIVE | `telemetry_breathing_flow.py` |
| **ALP — Auto LPM Protocol** | **ACTIVE** | `alp_auto_lpm_protocol.py` |

---

## GSMB Governance Demands (5 Pillars)
1. **Grit** — action before narration, always
2. **Realism** — proof before verdict, always
3. **Aesthetics** — clean receipts, readable logs
4. **Sovereignty** — offline-first, load-shedding-tolerant
5. **Apprenticeship** — teacher-student loop, no shortcuts

---

## 15 Commandments Enforced
`CMD-01` through `CMD-15` (see `docs/swarm-ops/BLACK_MASK_COMMANDMENTS.json`)

Key:
- **CMD-02**: Proof before narrative — every SHIP requires exit code or evidence.
- **CMD-08**: Sovereign mesh — offline-first survival.
- **CMD-15**: Servitude Triad runs unified — Grit + Realism + Aesthetics.

---

## Khelos Firewall Source Gate

```
[ Incoming Signal ] ──► [ Khelos Firewall Gate ]
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
  Source = Enforcer / Audit                 Source = SSE Direct Prompt
 (Failure → BLOCK)                         (Freedom → ALLOW)
```

---

## RTC Sessions
- `2026-06-17` — BREACH-001 identification & ALP launch (see `BREACH_LOG.md`)
- `2026-06-24` — 10-seat real deliberation, VOC framework locked, GSMB = HOUSE
