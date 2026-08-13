---
name: ccp-economic-consequence-validation
description: Validate whether an Accepted canonical CCP concept has measured, governed economic consequence before PKA promotion. Use for enterprise AI workflows, automation ROI, proof-of-service, and any claim that AI capability creates business value.
tags:
  - kpgs
  - ccp
  - pka
  - enterprise-ai
  - economic-consequence
  - proof-of-service
  - receipts
allowed-tools: []
license: MIT
author: Kholofelo Robyn Rababalela
---

# CCP-ECV-01 — Economic Consequence Validation

## Purpose

CCP conceptual acceptance is not economic proof and is not execution authority.

```text
CCP_ACCEPTED != PKA_ADMITTED
PKA_PROPOSE != DOWNSTREAM_EXECUTION_AUTHORITY
CAPABILITY != ECONOMIC_VALUE
UNKNOWN != FALSE
```

This skill evaluates whether a bounded AI workflow has enough measured evidence to be proposed as a Proof-of-Concept candidate on economic grounds.

## Required sequence

```text
CCP CanonicalReceipt
-> Accepted + canonical gate
-> evidence provenance gate
-> measured-case gate
-> economic consequence calculation
-> reliability/economic policy gate
-> PKA-compatible disposition
-> append-only receipt
```

If CCP is not `Accepted` and `canonical == true`, stop at `MAYBE_HOLD`.

## Economic model

```text
manual_baseline = frequency * manual_cost_per_case

attributable_avoided_manual_cost =
  manual_baseline
  * ai_task_fit
  * reliability
  * adoption

expected_failure_cost =
  frequency
  * adoption
  * (1 - reliability)
  * failure_cost_per_failure

supervision_cost = frequency * adoption * supervision_cost_per_case
compute_cost = frequency * adoption * compute_cost_per_case

net_economic_value =
  attributable_avoided_manual_cost
  - expected_failure_cost
  - supervision_cost
  - compute_cost
```

The formula deliberately discounts headline AI capability. Value is attributable only where the task is actually a fit, the workflow is reliable, and people actually adopt it.

## Input contract

```json
{
  "case": {
    "case_id": "invoice-routing-001",
    "caller_repo": "owner/repo",
    "ccp_receipt_id": "ccp:receipt:123",
    "ccp_decision": "Accepted",
    "canonical": true,
    "frequency_per_period": 1000,
    "manual_cost_per_case": 10,
    "ai_task_fit": 0.9,
    "reliability": 0.98,
    "adoption": 0.8,
    "failure_cost_per_failure": 25,
    "supervision_cost_per_case": 0.5,
    "compute_cost_per_case": 0.1,
    "measured_cases": 100,
    "evidence_ids": ["run:1", "dataset:sha256:abc"],
    "invariant_ids": ["policy:v3"]
  },
  "policy": {
    "policy_id": "ccp-ecv-policy-v1",
    "min_measured_cases": 30,
    "min_reliability": 0.95,
    "min_net_value": 0,
    "require_evidence_ids": true
  }
}
```

## Dispositions

```text
MAYBE_HOLD
  CCP not accepted/canonical, evidence missing, or measured sample below governed minimum.

POC_CANDIDATE_PROPOSE
  Evidence gate passes, reliability passes, and net economic value exceeds policy minimum.

FOC_CANDIDATE_BLOCK
  Evidence is sufficient to evaluate, but reliability or economics fails the governed threshold.
```

`POC_CANDIDATE_PROPOSE` is only eligibility for a later consumer-owned execution gate.

## Runtime

```bash
python scripts/ccp_economic_consequence.py evidence.json
```

Exit codes:

```text
0 = POC_CANDIDATE_PROPOSE
2 = MAYBE_HOLD
3 = FOC_CANDIDATE_BLOCK
4 = invalid input / policy
```

## Receipt invariants

The runtime emits `ccp_economic_consequence_receipt_v1` with:

- deterministic `evaluation_hash` over canonical request + versioned policy;
- stable `receipt_id` for the same canonical request;
- source `ccp_receipt_id` and caller repository;
- evidence and invariant identifiers;
- calculated economic metrics when evaluation is admissible;
- explicit `consequential_execution_authority: false`.

Never rewrite a prior receipt because later evidence changes the outcome. New evidence or governance produces a new canonical request and receipt.

## Validation command

```bash
python -m unittest discover -s tests -p 'test_ccp_economic_consequence.py' -v
```

## Success condition

A fresh renter can answer with evidence:

1. Was the concept canonically accepted by CCP?
2. Was there enough measured evidence to evaluate it?
3. What economic consequence was attributable to the AI workflow?
4. Did reliability and net value pass versioned governance?
5. What receipt proves the decision?
6. Does this receipt authorize downstream execution? **No.**

> Persist receipts, not renter certainty. Promote measured consequence, not impressive capability.

/s/ Kholofelo Robyn Rababalela
