---
title: "KPCB+ Analytical Projection Protocol — GROUP · PIVOT · ATTENTION"
created: 2026-08-28
updated: 2026-08-28
status: POC_CANDIDATE
tags:
  - kpcb-plus
  - gsmb
  - testimony-protocol
  - data-governance
  - data-science
  - groupby
  - pivot
  - heatmap
  - kc
source: "Commandment 15 testimony → existing Markdown governance → formal data-science vocabulary"
---

# KPCB+ Analytical Projection Protocol

## Testimony — where this came from

This architecture did **not** begin when the user learned Python `groupby()`, pivot tables or heatmaps.

KPGS/GSMB/KPCB+ already used governed Markdown, canonical `index.md` entry points, Bracket Protocol hierarchy, Prompting/Emoji/GIF/Sticker/.P/Image channels, KC Ledger receipts and explicit testimony to make knowledge recoverable by humans and stateless machines.

The user's original problem was **knowing**: if intelligence must resume work as though it never left, context must survive outside a single model/session in inspectable artifacts. Markdown became the governance substrate because one `.md` file can carry information, operating instruction, hierarchy, provenance, testimony, state and historical evidence in the same human-readable object.

The formal data-science lesson supplied names and executable analytical patterns for capabilities that can now **challenge, measure and strengthen** that existing design.

Do not rewrite this history as "KPGS invented Pandas" or "GSMB was secretly data science." The correct testimony is: independent governance pressure produced analogous information operations; formal statistics/programming now gives them a measurable implementation surface.

## KPCB+ remains seven-channel

The canonical channels remain:

- PP — Prompting / voice / intent
- BP — Bracket / structure / hierarchy
- EP — Emoji / semantic identity
- GP — GIF / motion / repeating visual instruction
- SP — Sticker / governance stamp
- .P — MP4 / evidence and testimony
- IP — Image / blueprint and visual context

Canonical algebra remains:

```text
[EP] + [BP] × [PP] + [GP] + [SP] + [.P] + [IP] = KPCB+
```

`GROUP`, `PIVOT` and `ATTENTION_MATRIX` are **analytical operators over protocol records**, not new communication channels.

## GROUP

`GROUP(records, dimensions...)` asks:

> What governed knowledge belongs together under the dimensions relevant to the current investigation?

Dimensions may include project, KPCB+ protocol channel, artifact type, authority, validation state, testimony state, sprint, ecosystem, canonical status or filesystem depth.

Sequence-valued dimensions such as `protocol_channels` may be exploded: one artifact may legitimately participate in multiple semantic groups.

The result must retain source `record_id` and `path` references.

## PIVOT

`PIVOT(records, row_dimension, column_dimension)` asks:

> How does the **same evidence** look when viewed from another governed projection?

A pivot does not create new source truth. It rotates/selects dimensions over existing testimony.

Every pivot cell must retain provenance identifying the source artifacts that contributed to the aggregate.

Examples:

```text
PROJECT × TESTIMONY_STATE
PROJECT × PROTOCOL_CHANNEL
SPRINT × VALIDATION_STATE
ECOSYSTEM × ARTIFACT_TYPE
AUTHORITY × CANONICAL_STATUS
```

## ATTENTION MATRIX / heatmap semantics

A heatmap is treated as a rendering of an **attention matrix**.

It answers:

> Where does something concentrate strongly enough that KC should consider deeper inspection?

Candidate attention metrics include evidence density, UNKNOWN testimony, contradiction density, activity, staleness and unresolved investigations.

Heat is not authority.

A visually hot cell cannot grant POC, FOC, causation, mutation permission or canonical status.

## GSMB folder-depth invariant

GSMB may contain folders inside folders inside folders and indefinite Markdown artifacts.

Therefore:

```text
deep_path != low_importance
shallow_path != high_authority
```

A deeply nested receipt may preserve a three-month sprint. A shallow random note may have no authority. Depth remains an observation, never an epistemic verdict.

Canonical indexes remain the deterministic boot/navigation surface. Analytical projections support selective discovery behind that boot surface; they do not flatten or replace GSMB.

## Commandment 15 — Testimony Protocol

Analytical code must preserve why a result exists and where it came from.

Missing testimony must not silently become failure:

```text
UNKNOWN != VIOLATED
absence of evidence != evidence of absence
```

An operational gate may still refuse action when state is UNKNOWN, but the epistemic record must remain UNKNOWN/HOLD rather than manufacturing negative proof.

## Reality ↔ cloud reflection

The human-readable artifact and machine projection must remain mutually inspectable.

Reality lane:

```text
human opens Markdown → sees title/context/testimony/evidence
```

Cloud/runtime lane:

```text
machine parses governed record → GROUP/PIVOT/ATTENTION → returns source IDs/paths
```

Validation requires that the machine view can be traced back to the human view. An opaque aggregate that cannot identify its contributing testimony violates this protocol.

## Runtime split

Introduction-to-MCP / KPCB+ owns the lightweight protocol-aware analytical contract:

```text
kopano-core/kopano/kpcb_analytics.py
```

KMEC owns scalable Python data-science execution with Pandas/NumPy/Dask.

PKA owns epistemic admission.

Smart Ledger / KC Ledger preserve governed receipts.

No one layer may silently absorb the authority of the others.

## POC flow

```text
canonical GSMB boot
        ↓
governed Markdown / KPCB+ records
        ↓
GROUP — belonging
        ↓
PIVOT — re-projection
        ↓
ATTENTION MATRIX — where to inspect
        ↓
trace cell → source record IDs / paths
        ↓
selective retrieval of testimony
        ↓
PKA / governance evaluation
        ↓
ALLOW | HOLD | DO-NOT-ALLOW
```

Remembering that knowledge exists remains separate from loading all knowledge into active context.

## Validation boundary

The protocol is not canonical merely because this document exists. Promotion requires executable tests proving deterministic grouping, provenance-preserving pivoting, UNKNOWN preservation, non-authoritative heatmaps, source immutability and KPCB+ protocol-channel integration.

Issue: `#108`

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
