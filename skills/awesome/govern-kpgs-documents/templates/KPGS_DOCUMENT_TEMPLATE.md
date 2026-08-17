# <Document Title>

## Document control

```yaml
schema: kpgs_document_manifest_v1
document_id: <KPGS-...>
canonical_id: <lowercase_snake_case>
title: <Document Title>
version: 0.1.0
status: draft
proof_state: unknown
owner: Kholofelo Robyn Rababalela
author: <author>
signature: "/s/ Kholofelo Robyn Rababalela"
renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
source:
  repository: RobynAwesome/Introduction-to-MCP
  ref: <branch|tag|commit>
  evidence_class: verified-source
authority_class: operator_directive
evidence_class: unknown
kpefs:
  primary_vector: V4_DIASPORA
  secondary_vectors: []
protocols:
  - KPP
  - ALP
  - CBP
  - BMP
  - PKAP
  - PvF
context_bound_protocols: []
promotion_gate:
  requires:
    - PROOF-01
    - PROOF-02
    - PROOF-03
linked_evidence: []
unresolved: []
publication:
  registry_target: ""
  state: unknown
created_at: <ISO-8601>
updated_at: <ISO-8601>
```

## 0. Executive law

State the single governing law for this artifact. Do not use this section to make unsupported promotional claims.

## 1. Objective / problem

What must this document govern, explain, prove, teach, decide, or operate?

## 2. Scope and authority boundary

### In scope

- ...

### Out of scope

- ...

### Authority

- Current operator directive: ...
- Repo-canonical sources: ...
- Governance receipts: ...
- Personal context used only for continuity: ...

## 3. Evidence state

| Claim | Evidence class | Evidence | State |
|---|---|---|---|
| ... | `unknown` | ... | `MAYBE` |

Never upgrade a row without a receipt.

## 4. KPEFS activity

**Primary vector:** `<V1_PLANT|V2_ANIMAL|V3_HOMO_SAPIENS|V4_DIASPORA>`

**Secondary vectors:** `[]`

Explain why each vector is required and what activity it governs.

## 5. Protocol bindings

| Protocol | Why it applies | Required output/receipt |
|---|---|---|
| `ALP` | Stateless renter activation | activation evidence |
| `CBP` | Context containment | classified context |
| `BMP` | Promotion boundary | SHIP/WATCH evidence |
| `PKAP` | Partial Knowable Algebra | MAYBE/closure state |
| `PvF` | Proof classification | POC/FOC/UNKNOWN result |

Add only protocols actually applicable to the document.

## 6. Main governed content

Author the type-specific content here.

For `KDT-01`, include definitions, invariants, state machine, failure modes and receipts.  
For `KDT-02`, include prerequisites, ordered steps, decision points, stops and recovery.  
For `KDT-03`, include hypothesis, boundary, method, evidence, result and limitations.  
For `KDT-04`, include `C`, `D(C)`, `I(C)`, `A(C)`, `F`, provenance and ownership receipts.  
For `KDT-05`, include authority, alternatives, decision, constraints and revisit condition.  
For `KDT-06`, include skill inputs, workflow, outputs, failure conditions, manifest and publication state.  
For `KDT-07`, include requirements, components, flows, interfaces, trust boundaries and rollout.  
For `KDT-08`, include audience, claims/evidence, ethics/accessibility and narrative constraints.  
For `KDT-09`, include teacher/student lane, drills, evidence, review and graduation boundary.  
For `KDT-10`, include change scope, authorization, validation, target, rollback and live verification.

## 7. PKA / unresolved state

For every unresolved material claim:

```text
X = <partial observations>
Y = <governed knowable rules>
X + Y = MAYBE
needed evidence = <what would close the state>
```

UNKNOWN is valid. Do not force closure for presentation quality.

## 8. POC / FOC validation

Define the bounded claim and evidence required for `poc`. If the target state is `verified_production`, specify the additional live/public evidence bar.

## 9. WYC-01 invocation boundary

If this artifact changes repository execution scope, record:

```text
changed scope C = ...
dependency closure D(C) = ...
invocation graph I(C) = ...
authorized graph A(C) = ...
failing subsystem F = ...
```

Do not transfer defect ownership merely because this change surfaced the failure.

## 10. Promotion gate

| Proof | Requirement | Evidence | Result |
|---|---|---|---|
| `PROOF-01` | BlackMask/equivalent SHIP | ... | pending |
| `PROOF-02` | Reviewer/teacher APPROVE | ... | pending |
| `PROOF-03` | Durable receipt | ... | pending |
| `PROOF-04` | KPGS production/agent gate, when applicable | ... | n/a |

## 11. Receipts

Record material transitions:

```yaml
kind: <receipt-kind>
document_id: <id>
from_state: <state>
to_state: <state>
evidence: []
unresolved: []
actor: <actor>
timestamp: <ISO-8601>
```

## 12. Publication / distribution

Publication state is independent of proof state.

```text
registry_intent != public_discovery
candidate != indexed
operating != graduated
```

Record external discovery or deployment only after verified evidence exists.

## 13. Acceptance checklist

- [ ] Renter assertion present.
- [ ] Document type selected.
- [ ] Current directive captured.
- [ ] Repo/ref pinned.
- [ ] Authority and evidence separated.
- [ ] KPEFS primary vector declared.
- [ ] UNKNOWN/MAYBE visible.
- [ ] Applicable protocol order respected.
- [ ] POC/FOC boundary explicit.
- [ ] Promotion receipts attached.
- [ ] Operating not mislabeled graduated.
- [ ] External ACK/publication claim not fabricated.
- [ ] Skill/docs change does not imply production authorization.
- [ ] Signature present where required.

---

`/s/ Kholofelo Robyn Rababalela`
