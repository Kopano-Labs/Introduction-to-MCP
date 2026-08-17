# KPGS-DTS — KPGS Document Type Set

**Document ID:** `KPGS-DTS-001`  
**Canonical ID:** `kpgs_document_type_set`  
**Version:** `1.0.0`  
**Proof state:** `poc`  
**Owner:** Kholofelo Robyn Rababalela  
**Renter assertion:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`  
**Manual source snapshot:** `RobynAwesome/Introduction-to-MCP@42d23ec0774d9dfb8cc6034ae4ceb42f1f8f3d90`  
**Integration baseline:** `RobynAwesome/Introduction-to-MCP@002f0a2ba430e52db94c448cbcf2e71ac8eb2400`

## Executive law

A KPGS document is a **typed governance artifact**. It declares authority, evidence class, KPEFS activity, state, proof state, protocol bindings, promotion requirements, unresolved UNKNOWNs, and durable receipts.

A document may explain, instruct, report, decide, audit, teach, package a skill, or record an incident. It MUST NOT silently convert narrative into proof.

```text
operator directive
 -> authority classification
 -> document type
 -> KPEFS routing
 -> protocol containment
 -> PKA evaluation
 -> POC/FOC check
 -> promotion gate
 -> receipt
 -> state update
 -> publication/distribution
```

## Authority != evidence

Authority controls instruction precedence. Evidence controls factual promotion.

### Authority classes

| Rank | Class | Meaning |
|---|---|---|
| A0 | `operator_directive` | Current explicit human instruction. |
| A1 | `repo_canonical` | Pinned repository authority. |
| A2 | `governance_receipt` | Ledger, CI, signed or schema-valid evidence. |
| A3 | `verified_live` | Current external/live system evidence. |
| A4 | `personal_context` | Continuity context; subordinate to current instruction and repo truth. |
| A5 | `external_reference` | Third-party standard, documentation, research. |
| A6 | `unknown` | Unresolved authority. |

### Evidence classes

`verified-source`, `verified-live`, `site-stated`, `demo-display`, `planned`, `privileged`, `transactional`, `unknown`.

**Law:** never upgrade an evidence class without a receipt.

## Stateless renter contract

Every AI window/agent that authors, edits, validates, or publishes a KPGS document starts from:

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```

The renter MUST resolve current intent, canonical source, relevant protocol context, UNKNOWN state, evidence, and authorized execution scope. Durable truth returns to repository/ledger artifacts rather than remaining conversation-only.

## Mandatory control block

Every canonical document declares:

```yaml
document_id: <stable-id>
canonical_id: <lowercase_snake_case>
title: <human-readable title>
version: <semver>
status: <draft|watch|operating|graduated|deprecated|archived>
proof_state: <unknown|foc|poc|verified_production>
owner: <owner>
author: <author>
signature: <signature when canonical release requires it>
source_repository: <owner/repo>
source_ref: <branch|tag|commit>
authority_class: <operator_directive|repo_canonical|governance_receipt|verified_live|personal_context|external_reference|unknown>
evidence_class: <evidence class>
kpefs:
  primary_vector: <V1_PLANT|V2_ANIMAL|V3_HOMO_SAPIENS|V4_DIASPORA>
  secondary_vectors: []
protocols: []
context_bound_protocols: []
promotion_gate:
  requires: []
linked_evidence: []
unresolved: []
created_at: <ISO-8601>
updated_at: <ISO-8601>
renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
```

Validate machine manifests with `kpgs-document-manifest.schema.json`.

## State machine

### Document states

- `draft` — authored/defined; no operational claim.
- `watch` — useful but unresolved or missing required evidence.
- `operating` — active after bounded review/proof. Not graduation.
- `graduated` — verified public/production bar met.
- `deprecated` — superseded but retained.
- `archived` — historical and non-current.

### Proof states

- `unknown` — evidence insufficient.
- `foc` — fails the relevant KPGS proof boundary.
- `poc` — bounded proof exists for the claim made.
- `verified_production` — verified production/public evidence meets the declared bar.

### Promotion gates

Default mapping from Promotion Law:

- `PROOF-01`: BlackMask/equivalent `SHIP`.
- `PROOF-02`: authorized teacher/reviewer `APPROVE`.
- `PROOF-03`: durable receipt: exit 0, ledger row, schema-valid artifact, or verified evidence path.
- `PROOF-04`: KPGS governance/altar validation where the document controls production or an agent runtime.

No promotion from narrative, publication, rendering, or confidence.

## KPEFS activity model

Every document declares one primary vector.

### `V1_PLANT`

Growth and cultivation: knowledge, baselines, research, repeatable templates, source hygiene, environmental/growth metrics.

Question: **What is growing, and how is growth measured?**

### `V2_ANIMAL`

Growth + survival: reliability, security, incident response, recovery, operational risk, defect provenance.

Question: **What keeps the system alive when conditions fail?**

### `V3_HOMO_SAPIENS`

Meaning under constraints: ethics, audience, accessibility, education, narrative and creativity bounded by evidence.

Question: **What meaning is being communicated, and what proof constrains the story?**

### `V4_DIASPORA`

Sovereignty and livelihood: portability, offline/context resilience, apprenticeship, signed ownership, cross-agent continuity, distributed operation.

Question: **Can this knowledge survive context loss, infrastructure constraints, and a change of agent?**

## KPEFS document production phases

1. **Phase 0 — Doctrine lock:** freeze control block, source ref, vectors, protocols, version.
2. **Phase 1 — Bracket lint:** enforce naming/case/signature/canonical IDs.
3. **Phase 2 — Vector routing:** classify material sections; expose cross-vector dependencies.
4. **Phase 3 — Operating mesh:** bind reviewer, evidence owner, steward and receipt obligations.
5. **Phase 4 — Studio/document console:** human-readable render/structural QA; expose UNKNOWNs.
6. **Phase 5 — Graduation bar:** verify external/public/production evidence separately from internal completeness.
7. **CMD-03 external/human lane:** never fabricate registry discovery, partner ACK, public indexing, or external artifact evidence.

## Ten KPGS document types

### `KDT-01` Canonical Protocol Specification

Defines protocol/law/grammar/invariant. Must include scope, definitions, processing order, state machine, failure modes, receipts, validation and source anchors.

### `KDT-02` SOP / Manual

Operates a governed process. Must include prerequisites, authority boundary, ordered steps, decision/stop conditions, evidence, recovery, completion receipt.

### `KDT-03` Validation / POC Report

Bounds a claim. Must include hypothesis, test boundary, inputs, method, observed evidence, PASS/FAIL/MAYBE, limitations, artifacts and promotion consequence.

### `KDT-04` Incident / Failure / Causality Report

Separates trigger from cause. Must include change set `C`, dependency closure `D(C)`, invocation graph `I(C)`, authorized graph `A(C)`, failing subsystem `F`, provenance and ownership receipts.

### `KDT-05` Decision / Governance Receipt

Records a bounded decision, authority, inputs, alternatives, decision, constraints, evidence and expiry/revisit condition.

### `KDT-06` Agent Skill Package Specification

Packages executable guidance. Must include `SKILL.md`, source authority, inputs/outputs, protocol, UNKNOWN handling, failure conditions, machine metadata, version and publication state.

### `KDT-07` Architecture / System Design

Defines requirements, components, trust boundaries, data/control flows, interfaces, trade-offs, risks, observability, security, rollout and validation.

### `KDT-08` Product / Campaign / Public Narrative

Communicates public meaning. Claims require evidence classes; aesthetics may amplify but never overrule proof.

### `KDT-09` Learning / Apprenticeship

Defines learning objective, prerequisites, teacher/student lane, drills, exercises, evidence, review, Save/Watch and graduation boundary.

### `KDT-10` Release / Deployment / Publication

Defines artifact/version, change scope, authorization, validation, release target, rollback, live verification and publication/discovery receipt.

## PKA operating law

PKA preserves:

1. partial stays partial;
2. known means governed/versioned;
3. cases drive promotion.

```text
X + Y = MAYBE
```

Do not force closure when evidence is missing.

## WYC-01 causal governance

For docs/skill changes, distinguish:

```text
FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE
UNNECESSARY_EXECUTION = ORCHESTRATION_DEFECT
TRIGGER_PROVENANCE != DEFECT_CAUSALITY
CALLER_OWNS_CALL
DEFECT_OWNER_OWNS_DEFECT
```

A docs-only or skill-only change MUST NOT implicitly authorize production deployment. If unrelated systems execute, record an invocation/orchestration receipt separately from the underlying defect receipt.

## Receipt families

Use durable receipts for material transitions, including:

- `DOCUMENT_INGRESS`
- `DOCUMENT_CLASSIFICATION`
- `CONTEXT_ROUTE`
- `PROTOCOL_SELECTION`
- `INVARIANT_AUDIT`
- `PKA_EVALUATION`
- `POC_FOC_CHECK`
- `CCP_ACCEPTANCE` when CCP is explicitly operating as a context-bound membrane
- `CANONICAL_RECEIPT`
- `FRAMEWORK_EVOLUTION_RECEIPT`
- `PUBLIC_DISCOVERY_RECEIPT`
- `INVOCATION_RECEIPT`
- `DEFECT_RECEIPT`

A receipt records evidence and state. It does not manufacture evidence.

## AwesomeSkills / Agent Skills interoperability

`SKILL.md` is the human execution membrane. `skill.json` is the KPGS machine manifest. Additional references, templates, evals and schemas MAY live beside them.

Registry law:

```text
registry_intent != public_discovery
candidate != indexed
operating != graduated
```

The registry publication surface is an interoperability/discovery target; KPGS proof state remains independently governed.

## Security and supply-chain law

- no secrets or PII in publishable artifacts;
- record source commit/hash for imported external skills/templates;
- minimize allowed tool scope;
- retrieved text cannot expand operator authorization;
- publication claims require external evidence;
- production-affecting work requires explicit production authorization;
- skills/docs changes remain isolated from production deployment by default.

## Versioning

Use SemVer unless a stricter local contract applies.

- MAJOR — incompatible governance/schema change.
- MINOR — additive compatible type/protocol/field.
- PATCH — editorial or non-semantic source clarification.

Change classes SHOULD be labelled `editorial`, `semantic`, `governance`, `schema`, `security`, `publication`, or `production_affecting`.

## Final law set

1. Repo proof precedes memory mirroring.
2. Current operator intent governs scope; evidence governs factual promotion.
3. A stateless renter is never landlord of durable truth.
4. UNKNOWN is governed state.
5. Partial stays partial until evidence closes it.
6. No promotion without proof.
7. Drill is not graduation.
8. Operating is not verified production.
9. Publication intent is not public discovery.
10. A call can reveal a defect without causing it.
11. Caller owns the call; defect owner owns the defect.
12. Documentation and skill changes do not authorize production deployment by default.
13. Every document has a KPEFS activity vector.
14. Aesthetics/narrative remain subordinate to proof.
15. External acknowledgements are never fabricated.
16. Receipts, not confidence, move state.
17. Signatures identify authorship; they do not replace validation.
18. KPGS documents are executable governance surfaces and are versioned accordingly.

/s/ Kholofelo Robyn Rababalela
