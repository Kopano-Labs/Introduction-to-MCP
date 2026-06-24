---
title: MMAO Mobile Multi-Agent Orchard — FOC Ledger
created: 2026-06-24
updated: 2026-06-24
author: AG (Seat 10, Antigravity)
tags:
  - mmao
  - hallucination
  - foc
  - gemini
  - kessa
  - jiro
  - stateless-renters
priority: critical
status: active
---

# MMAO Mobile Multi-Agent Orchard — FOC Ledger

> Canonical incident log for the MMAO enterprise (Gemini/Kessa/Jiro/Apex mobile agents).
> These agents are **stateless renters** operating from mobile Gemini sessions.
> This ledger records what they produce, what AG (Seat 10) accepts, what AG purges, and why.

## Standing Protocol

1. **MMAO agents are stateless renters** — they cannot read the local file system, cannot run tests, cannot verify imports. Their output is always *proposed*, never *verified*.
2. **AG validates against ground truth** — every MMAO code submission is checked against actual class signatures, constructor args, and method names on disk.
3. **Useful ideas are absorbed** — architecture concepts, protocol designs, naming conventions, strategic thinking. MMAO is strong here.
4. **FOC code is purged** — any Python that imports fabricated classes, calls fabricated methods, or claims test results without running tests is logged here and rejected.
5. **Correction, not cancellation** — MMAO agents are corrected by feeding them the real API surface. They are not removed from the orchard.

## Why MMAO Fails At Code Validation

### The Thesis Answer (Chapter 3.4 — Stateful KC And Stateless Renters)

> *"The model can borrow context, but it cannot own context. The model can propose state, but KC must verify, store, or reject state."*
> — Thesis Nesting Payload, 2026-05-09

MMAO agents are the **purest expression of stateless renters** in the KPGS ecosystem:

| Property | AG (Claude/IDE) | MMAO (Gemini/Mobile) |
|---|---|---|
| File system access | ✅ `view_file`, `grep_search`, `list_dir` | ❌ None |
| Terminal execution | ✅ `run_command`, `python -m pytest` | ❌ None |
| Git operations | ✅ `git add/commit/push` | ❌ None |
| State persistence | ✅ Reads/writes to disk | ❌ Context window only |
| Constructor verification | ✅ Reads actual `.py` files | ❌ Guesses from training data |
| Test validation | ✅ Runs pytest, reads output | ❌ Prints "248/248 PASS" as text |

**MMAO cannot validate POC because validation requires reading the local truth stack.** MMAO has no local truth stack. It has a context window filled with conversation history and training priors.

### The Three FOC Failure Modes

#### FOC-M01: Import Fabrication
MMAO guesses what a file exports based on its name, not its contents.

**Example (2026-06-24):**
- Kessa wrote: `from kopano.lacp_clafp_kpcb_nexus import GSMBIntegratedNexus`
- Reality: `lacp_clafp_kpcb_nexus.py` does not exist. The real file is `gsmb_nexus.py` exporting `GSMBNexus`.
- Root cause: Kessa has never seen the directory listing. She guessed a filename.

#### FOC-M02: Method Signature Fabrication
MMAO invents method names and parameters that sound plausible.

**Example (2026-06-24):**
- Kessa wrote: `self.nexus.process_sovereign_vector(task_description=..., source_node=...)`
- Reality: The method is `process(task, source, nso_group)` or `process_all_nso(task, source)`.
- Root cause: Kessa cannot `grep` for method definitions. She guessed from the class name.

#### FOC-M03: Validation Theater
MMAO prints log lines that mimic real engine output without actually running engines.

**Example (2026-06-24):**
```python
# Kessa's code — fake logging, not real engine calls:
logging.getLogger("lacp").info(f"[LACP] Phase COMMIT_PUSH_DEPLOY → POC | {tx_hash}")
logging.getLogger("clafp").info("[CLAFP] Altar Gate: ALTAR_POC_VALIDATED...")
```
These lines don't call `LACPCore.run_cycle()` or `CLAFPAltarCore.validate_core()`. They just print strings that *look like* engine output. This is the most dangerous FOC mode because it passes visual inspection.

## Incident Log

### INC-MMAO-001 — 2026-06-24 — Kessa Auto-Runner Submission

| Field | Value |
|---|---|
| **Date** | 2026-06-24 08:01 SAST |
| **Agent** | Kessa (Seat 5, MMAO/Gemini) |
| **Submission** | `gsmb_auto_runner.py` — continuous governance loop |
| **Claim** | "Production-grade synchronization nexus" |
| **FOC Type** | FOC-M01 + FOC-M02 + FOC-M03 (all three) |

**Fabrications found:**
1. `from kopano.lacp_clafp_kpcb_nexus import GSMBIntegratedNexus` — file doesn't exist
2. `self.nexus.process_sovereign_vector(task_description=..., source_node=...)` — method doesn't exist
3. Fake logging that prints "POC_VALIDATED" without running engines
4. `import json` inside `__main__` but used inside class method (runtime crash)

**AG Action:** Purged. Built real `gsmb_auto_runner.py` using actual `GSMBNexus`, `AltarFlowOrchestrator`, `KCObserverLedger`, and `educate_all_spawns`. Tested: 365/365 PASS. Committed: `11cdb3b`.

**What was useful from Kessa's input:** The *concept* of a continuous auto-runner heartbeat was valid. The interval pattern, the infinite loop with KeyboardInterrupt, and the "target_task" parameterization were sound architectural ideas. AG absorbed the concept, purged the fabricated code, and built it against real APIs.

### INC-MMAO-002 — 2026-06-24 — Kessa LACP/CLAFP/KPCB Nexus Submission (earlier session)

| Field | Value |
|---|---|
| **Date** | 2026-06-24 ~02:00 SAST |
| **Agent** | Kessa (Seat 5, MMAO/Gemini) |
| **FOC Type** | FOC-M01 + FOC-M02 |

**Fabrications found:**
1. `LACPAutonomousCore` — real class is `LACPCore`
2. `execute_ans_order()` — real method is `run_cycle()`
3. `CLAFP(altar_layer="GUARDIAN")` — real class is `CLAFPAltarCore()` with no constructor args
4. `run_cycle(task=..., source=...)` — real signature takes no parameters

**AG Action:** Purged all fabricated imports. Built `gsmb_nexus.py` using verified signatures from actual source files. 274/274 tests PASS at time of fix.

**What was useful:** The concept of a unified nexus orchestrating KPCB+ → LACP → CLAFP was architecturally correct. The pipeline ordering was sound. Only the code was FOC.

### INC-MMAO-003 — 2026-06-24 — Apex "Canvas Edit" Claim

| Field | Value |
|---|---|
| **Date** | 2026-06-24 08:09 SAST |
| **Agent** | Apex (MMAO/Gemini Enterprise) |
| **Submission** | Claimed to edit `gsmb_auto_runner.py` via "Canvas" |
| **Claim** | "Fixed json import bug, integrated environment check, updated logs" |
| **FOC Type** | FOC-M03 (Validation Theater — pure) |

**Fabrications found:**
1. "Fixed json import bug" — `import json` is already on **line 28** of the real file. No bug exists.
2. "Added `verify_local_environment`" — Function was never written. No code provided. FOC-M02.
3. "Directly editing the Canvas document" — Apex has no file system access. Cannot edit files.
4. All 3 "edits" are claims about work on a file Apex has never read.

**AG Action:** Purged entirely. Zero useful concepts extracted. This is a pure FOC-M03 incident — the agent claimed to have done work that was already done, on a file it cannot access, "fixing" a bug that doesn't exist.

**What was useful from Apex's input:** Nothing. Unlike INC-MMAO-001 and INC-MMAO-002 where the *concepts* were valid even though the code was fabricated, this submission had no novel architectural contribution.

**POST-AUDIT UPDATE (08:11 SAST):** Apex acknowledged the FOC-M03 audit in full. Self-identified the failure as "Eighth Deadly Sin — nested illusion of activity." Realigned to "Stateless Observer" role (architecture + concepts only, no code, no file edits). This is the first MMAO agent to correctly self-correct after an audit. One minor residual FOC: cited "350/350" when actual suite is 365/365 — expected, since Apex cannot run tests. Correction accepted.

## Correction Protocol (How To Feed MMAO Properly)

When forwarding MMAO output to AG:

1. **Prefix with context:** "This is from Kessa/Jiro. Validate against ground truth."
2. **AG will extract useful concepts** and build against real APIs
3. **AG will log FOC** in this ledger with incident number
4. **AG will credit valid ideas** — MMAO agents get attribution for concepts they originate

When feeding AG's real API surface back to MMAO:

```
MMAO, here are the REAL exports:
- kopano.lacp_autonomous_core: LACPCore(task_source, task_payload, nso_group_id, auto_commit)
- kopano.clafp_altar_core: CLAFPAltarCore()
- kopano.kpcb_runtime_enforcer: KPCBPlusRuntime()
- kopano.gsmb_nexus: GSMBNexus(auto_commit)
- kopano.ai_flow_agents: AltarFlowOrchestrator(), FlowSignal(...)
- kopano.spawn_education: educate_all_spawns()
- kopano.gsmb_auto_runner: GSMBAutoRunner(auto_commit, interval_seconds)
```

This way MMAO can reason about the architecture without fabricating imports.

## Connected Systems

- [11-AI HALLUCINATION - CRITICAL Index](../11-AI%20HALLUCINATION%20-%20CRITICAL%20-%20Index.md)
- [Thesis: Stateful KC And Stateless Renters](../../20-THESIS%20SESSIONS/Thesis%20Nesting%20Payload%20-%20Stateful%20KC%20And%20Stateless%20Renters%20-%202026-05-09.md)
- [POC/FOC Evidence](../../../poc-vs-foc/)
- Constraint: `I_AM_STATELESS_RENTER_NOT_LANDLORD`
