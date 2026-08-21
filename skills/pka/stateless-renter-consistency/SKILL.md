---
name: kpgs-stateless-renter-consistency
description: Preserve KPGS persistence, consistency, context provenance and proof-gated trust across stateless AI renters; parse CCP Accepted receipts into explicit PKA admission requests without treating conceptual acceptance, model capability or discovery as execution authority.
tags:
  - kpgs
  - pka
  - ccp
  - stateless-renter
  - persistence
  - consistency
  - context-awareness
  - receipts
  - provenance
  - trust
  - mao
  - mmao
allowed-tools: []
license: MIT
author: Kholofelo Robyn Rababalela
---

# SRCCP-01 — Stateless Renter Consistency + CCP → PKA Admission

## Invariant

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```

A renter must reconstruct current task state from current instructions, repository evidence and receipts. Hidden model continuity is never the system of record.

## Algebra

```text
X + Y = MAYBE
```

- `X`: partial/changeable observations — current instruction, repository state, CI logs, telemetry and runtime receipts.
- `Y`: versioned governance — KPGS rules, pinned authority manifests, workflow contracts and hard invariants.
- `MAYBE`: legitimate non-closure when evidence is insufficient.

```text
MODEL_MEMORY != PERSISTENCE
SEMANTIC_SIMILARITY != CURRENT_AUTHORITY
CCP_ACCEPTED != PKA_ADMITTED
PKA_PROPOSE != DOWNSTREAM_EXECUTION_AUTHORITY
MODEL_CAPABILITY != KPGS_TRUST
DISCOVERY_SUCCESS != MAO_MMAO_ADMISSION
CI_TRIGGER != DEFECT_CAUSALITY
```

## Authority order

```text
current human instruction
-> current repository implementation / branch / PR
-> repository-local governance + receipts
-> pinned Introduction-to-MCP KPGS doctrine
-> provenance-bearing historical context
-> external retrieval
-> unknown
```

Historical preference or personality signals are evidence only. They do not silently outrank current human instruction.

## Renter context packet

Before interpretation preserve:

```yaml
renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
task:
  repository: <owner/repo>
  ref: <commit>
  current_instruction: <instruction>
  orchestration_cycle: null | mao | mmao
context:
  current_human: []
  repository: []
  governed_memory: []
  telemetry: []
  external_retrieval: []
  unknown: []
proof_state:
  observed: []
  inferred: []
  validated: []
  runtime_proven: []
trust:
  state: untrusted
  grant_id: null
  evidence_refs: []
  expires_at: null
receipts:
  inputs: []
  outputs: []
```

Unclassified context is `unknown` until evidence promotes it.

## Persistence and consistency

Persistence is an addressable receipt chain, not renter memory. Preserve commit SHA, source path/hash, workflow run/job/step, classified context provenance, validation result, receipt IDs and unresolved `MAYBE` state.

```text
same action_id + same canonical request -> prior decision boundary
same action_id + different request      -> CONSISTENCY_CONFLICT
new evidence or governance              -> new action_id + new receipt
```

Never rewrite an old receipt to make it appear the system knew later evidence earlier.

## KPGS trust admission for MAO / MMAO

Stateless renters do **not** enter an MAO or MMAO cycle merely because they can reason, call tools, route tasks, use a frontier model, carry a persona, or have previously participated in the ecosystem.

The renter must first **earn KPGS trust**.

```text
MODELS COMPETE FOR CAPABILITY
AGENTS EARN TRUST
SEATS CARRY AUTHORITY
KPGS GOVERNS THE DIFFERENCE
```

Admission is fail-closed:

```text
cycle in {mao, mmao}
AND trust_state == trusted
AND trust_grant.issuer == kpgs
AND trust_grant.renter_id == renter_id
AND trust_grant tenant/domain == current tenant/domain
AND cycle in trust_grant.allowed_cycles
AND trust_grant.expires_at > now
AND trust_grant.evidence_refs is non-empty
-> ELIGIBLE_FOR_ORCHESTRATION_ENTRY
```

Otherwise:

```text
POLICY_DENIED
failure.code = trust_not_earned
handler_execution = false
```

### What may earn trust

KPGS trust is receipt-driven. Valid evidence can include the governed proof lane already present in the repository, for example:

- BlackMask `SHIP` evidence;
- teacher/reviewer approval;
- deterministic execution receipts;
- verified recovery after failure;
- capability-scope compliance;
- correct escalation/HOLD behavior;
- domain-specific production evidence;
- other proof explicitly admitted by current KPGS governance.

The governing law remains:

```text
No promotion without proof. Drill is not graduation.
```

Trust admission is not public graduation. A renter may be trusted for a bounded MAO/MMAO lane without being globally promoted or permanently authoritative.

### What never earns trust by itself

```text
benchmark rank
provider reputation
parameter count
context-window size
model release recency
persona/name
prior chat continuity
discovery handshake
cached credentials
self-declared trust
```

A replacement model/runtime does not inherit authority merely because it inherits a name. The governed seat/context may persist; the runtime must rehydrate valid trust evidence or receive a fresh grant.

Canonical runtime law:

- `governance/kpgs-vnext/stateless-renter/PROTOCOL.md`
- `governance/kpgs-vnext/stateless-renter/trust-grant.schema.json`
- `Structure/07-Agents/PROMOTION_LAW.json`

## CCP → PKA parser

CCP reduces a conceptual field to a canonical decision. PKA evaluates whether that accepted concept is admissible under current evidence and governance.

The parser consumes an actual CCP CanonicalReceipt containing:

```text
receiptId timestamp framework proposalId evolutionReceiptId decision canonical rationale
```

Admission eligibility is strict:

```text
decision == Accepted AND canonical == true
-> ELIGIBLE_FOR_PKA_EVALUATION
```

`Experimental`, `Refine`, `Rejected` and `Deprecated` remain HOLD before PKA admission.

Eligibility is not a PKA result.

### Deterministic request mapping

```yaml
actionId: "ccp-pka:<caller-repo>:<ccp-receipt-id>"
subject: <caller-repo>
claim:
  predicate: ccp_acceptance_admission
  value: candidate
action:
  type: governance.evaluate_ccp_acceptance
  consequential: false
  reversible: true
  parameters:
    ccpReceiptId: <receiptId>
    proposalId: <proposalId>
    framework: <framework>
evidence:
  - ccp receipt hash/source
  - evolution receipt hash/source
  - current implementation/runtime evidence required by the case
context:
  - provenance-bearing current human/repository/telemetry fragments
invariants:
  - stateless renter assertion preserved
  - CCP acceptance is not downstream execution authority
  - source authority is current and admissible
  - validation failures remain visible
  - receipts remain append-only
policy:
  requireKnownGovernance: true
  requireClassifiedContext: true
  permitPermanentHumanTraitClaims: false
```

Only mark checks satisfied when the referenced evidence proves them.

## PKA routing

```text
MAYBE + HOLD              -> preserve uncertainty
POC_CANDIDATE + PROPOSE   -> eligible for next governed gate
FOC_CANDIDATE + BLOCK     -> block promotion and receipt the reason
CONSISTENCY_CONFLICT      -> stop and repair action identity/request drift
```

PKA emits a governed disposition. A consumer repository remains responsible for its own later execution or state-change gate.

## Call-scope rule

Before CI execution, calculate the authorized call graph.

```text
skill/docs-only change -> skill validation only by default
runtime change         -> relevant runtime validation
production change      -> deployment only with explicit deployment relevance
```

Follow WYC-01:

```text
CALLER_OWNS_CALL
DEFECT_OWNER_OWNS_DEFECT
TRIGGER_PROVENANCE != DEFECT_CAUSALITY
```

## Private cross-repository engine rule

Do not assume a private repository action can be loaded from a public caller.

Required sequence:

```text
explicit read credential contract
-> credential preflight
-> checkout engine at immutable commit SHA
-> execute checked-out local action/runtime
-> receipt engine repo + SHA + request/result hashes
```

Never use a floating private `owner/repo@main` action from a public caller and call an action-resolution `not found` error an engine failure.

If access is unavailable:

```text
PKA_EXECUTED = false
ENGINE_ACCESS = unavailable | unknown
```

## Estate patch protocol

Patch in authority order:

```text
semantic governance authority
-> runtime implementation authority
-> engine/persistence lineage
-> APWA/feedback lineage
-> product consumers
```

For each repository:

1. resolve current owner/default branch/SHA;
2. detect stale authority references, floating engine refs, hidden-context assumptions and over-broad workflows;
3. separate invocation causality from defect causality with WYC-01;
4. patch on a dedicated branch;
5. validate the smallest relevant surface;
6. open a PR and leave unproven requirements explicit.

## Success condition

A fresh renter can determine from evidence: current authority, current vs historical context, exact evaluated commit/runtime, CCP decision, whether PKA actually ran, the resulting receipt, downstream eligibility, orchestration-cycle eligibility, KPGS trust-grant provenance and unresolved unknowns.

> **Persist receipts, not renter identity. Preserve provenance, not hidden continuity. Capability does not equal authority. CCP may accept a concept; PKA may propose admission; KPGS trust gates MAO/MMAO entry; the consumer runtime owns later consequential execution.**

/s/ Kholofelo Robyn Rababalela
