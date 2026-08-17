---
name: govern-kpgs-documents
description: Create, edit, classify, validate, version, review, and package KPGS documents as typed governance artifacts using KPGS-DTS, KPEFS routing, Partial Knowable Algebra, BlackMask/promotion law, receipts, and WYC-01 causal boundaries. Use for KPGS specifications, manuals, SOPs, POC reports, incident reports, governance decisions, skill packages, architecture documents, public narratives, apprenticeship materials, and release/publication documents. Preserve UNKNOWN and never treat publication or polished prose as proof.
license: MIT
metadata:
  author: Kholofelo Robyn Rababalela
  version: "1.0.0"
  kpgs_document_type: KDT-06
  canonical_id: kpgs_document_governance
  source_repository: RobynAwesome/Introduction-to-MCP
  manual_source_snapshot: 42d23ec0774d9dfb8cc6034ae4ceb42f1f8f3d90
  integration_baseline: 002f0a2ba430e52db94c448cbcf2e71ac8eb2400
  renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
  kpefs_vector: V4_DIASPORA
  proof_state: poc
---

# KPGS Document Governance

## Objective

Treat every KPGS document as a **typed, evidence-bearing governance artifact**, not passive prose.

The execution chain is:

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

Publication, rendering, deployment, reviewer confidence, or persuasive language MUST NOT silently upgrade a claim from `unknown` or `planned` to `poc` or `verified_production`.

## Activation boundary

Begin every governed run with:

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```

Then resolve, in order:

1. the current operator directive;
2. the canonical repository/ref;
3. the requested KPGS document type;
4. authority and evidence classes;
5. KPEFS vector(s);
6. applicable protocol gates;
7. unresolved UNKNOWN/MAYBE state;
8. the minimum authorized execution surface.

Conversation memory or personal context MAY restore continuity, but it MUST NOT overrule the current operator directive or pinned repository truth.

## Document types

Classify the artifact before authoring or editing:

| ID | Type | Primary purpose |
|---|---|---|
| `KDT-01` | Canonical Protocol Specification | Define laws, grammar, invariants, state machines, receipts. |
| `KDT-02` | SOP / Manual | Operate a governed process step by step. |
| `KDT-03` | Validation / POC Report | Bound and prove a claim. |
| `KDT-04` | Incident / Failure / Causality Report | Separate trigger, invocation, cause, and provenance. |
| `KDT-05` | Decision / Governance Receipt | Record an authoritative bounded decision. |
| `KDT-06` | Agent Skill Package Specification | Package executable guidance and machine metadata. |
| `KDT-07` | Architecture / System Design | Define components, boundaries, flows, risks, contracts. |
| `KDT-08` | Product / Campaign / Public Narrative | Communicate meaning without outrunning proof. |
| `KDT-09` | Learning / Apprenticeship | Teach governed practice and evidence collection. |
| `KDT-10` | Release / Deployment / Publication | Govern distribution and verified release state. |

Read `references/KPGS_DTS_SPEC.md` for the full compact specification and `templates/KPGS_DOCUMENT_TEMPLATE.md` for the canonical starting shape.

## Authority and evidence are separate axes

Authority answers **who or what governs the instruction**. Evidence answers **what proves the claim**.

Authority order:

```text
A0 operator_directive
A1 repo_canonical
A2 governance_receipt
A3 verified_live
A4 personal_context
A5 external_reference
A6 unknown
```

Evidence classes:

```text
verified-source
verified-live
site-stated
demo-display
planned
privileged
transactional
unknown
```

Never upgrade an evidence class without a receipt.

## KPEFS routing

Every governed document MUST declare one primary KPEFS vector.

- `V1_PLANT` — growth, knowledge cultivation, baselines, research, repeatability.
- `V2_ANIMAL` — survival, reliability, security, incidents, recovery, defect provenance.
- `V3_HOMO_SAPIENS` — meaning, ethics, audience, accessibility, narrative under proof.
- `V4_DIASPORA` — sovereignty, portability, apprenticeship, offline/context resilience, livelihood.

Secondary vectors MAY be declared, but the primary vector remains explicit.

## Protocol order

Use the KPGS protocol registry ordering when applicable:

1. Prompting protocols — scope, hierarchy, activation, purpose.
2. Bracket protocols — containment, BlackMask, PKAP/PKA, POC-vs-FOC.
3. Emoji/life-pattern protocols — only after prior containment.

Common document bindings:

```text
KPP   protocol registry/order
ALP   stateless renter activation
CBP   context bleed containment
BMP   BlackMask proof gate
PKAP  Partial Knowable Algebra / validation
PvF   POC vs FOC classification
USTP  teacher/student review boundary
```

Context-bound extensions such as `CCP`, `CDP`, or `RIVM` MUST be labelled context-bound until pinned by current repo authority.

## PKA / UNKNOWN handling

PKA preserves three boundaries:

1. partial stays partial;
2. known means governed/versioned;
3. cases drive promotion.

Use:

```text
X + Y = MAYBE
```

where `X` is partial observation and `Y` is governed knowable state. Do not coerce MAYBE into certainty because the document needs a clean conclusion.

## State machine

Allowed document states:

```text
draft -> watch -> operating -> graduated
              \-> deprecated -> archived
```

These transitions are evidence-gated, not prose-gated.

Proof states:

```text
unknown
foc
poc
verified_production
```

Default promotion requirements:

- `PROOF-01` — BlackMask/equivalent verdict `SHIP`;
- `PROOF-02` — authorized reviewer/teacher `APPROVE`;
- `PROOF-03` — durable receipt/evidence artifact;
- `PROOF-04` — KPGS governance/altar validation when the document controls production or an agent runtime.

Operating is not graduation. Internal completion is not verified production.

## WYC-01 binding for document and skill changes

When a document/skill change triggers CI or deployment, never infer:

```text
change happened -> workflow failed -> change caused defect
```

Evaluate separately:

```text
FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE
UNNECESSARY_EXECUTION = ORCHESTRATION_DEFECT
TRIGGER_PROVENANCE != DEFECT_CAUSALITY
CALLER_OWNS_CALL
DEFECT_OWNER_OWNS_DEFECT
```

A documentation-only or skill-only change MUST NOT implicitly authorize production deployment. If workflow scope crosses that boundary, record the orchestration defect separately from any underlying subsystem defect.

## Required control block

Canonical documents MUST declare at least:

```yaml
document_id: <stable-id>
canonical_id: <lowercase_snake_case>
title: <human title>
version: <semver>
status: <draft|watch|operating|graduated|deprecated|archived>
proof_state: <unknown|foc|poc|verified_production>
owner: <owner>
author: <author>
source_repository: <owner/repo>
source_ref: <branch|tag|commit>
authority_class: <A0-A6>
evidence_class: <class>
kpefs:
  primary_vector: <V1_PLANT|V2_ANIMAL|V3_HOMO_SAPIENS|V4_DIASPORA>
  secondary_vectors: []
protocols: []
promotion_gate:
  requires: []
linked_evidence: []
renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
```

Machine manifests SHOULD validate against `references/kpgs-document-manifest.schema.json`.

## Required outputs

For canonical work, return or persist:

1. the human-readable artifact;
2. the document control block;
3. a machine-readable manifest when durable automation is intended;
4. unresolved `UNKNOWN`/`MAYBE` entries;
5. evidence links/paths or an explicit empty list;
6. a receipt for any state/proof transition;
7. publication/deployment state kept separate from proof state.

## Publication law

AwesomeSkills or another registry is a distribution surface, not a proof oracle.

```text
registry_intent != public_discovery
publication_candidate != indexed
rendered != operating
operating != graduated
```

External indexing, deployment, partner acknowledgement, or public discovery remains `unknown` until verified externally.

## Decline conditions

Return `watch` or decline promotion when any of the following holds:

- source authority cannot be resolved;
- a material claim lacks its required evidence class;
- PKA remains MAYBE and the requested state requires closure;
- BlackMask/reviewer/receipt gates are missing;
- an external acknowledgement would have to be fabricated;
- the requested state would equate operating with graduation;
- a docs/skill change would trigger unauthorized production execution;
- the artifact contains secrets or private data outside its declared boundary.

## Signature

For artifacts owned under this convention:

```text
/s/ Kholofelo Robyn Rababalela
```

A signature proves authorship/approval identity only. It does not replace validation.
