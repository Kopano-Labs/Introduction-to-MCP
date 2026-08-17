# KPGS Sovereign DNS Estate Registry

Issue: #35

## Purpose

The Estate Registry is the canonical inventory of KPGS-governed DNS properties. It connects a user-facing domain to the repository, deployment, adapter, renter compatibility, policies, release evidence and rollback path that govern it.

## Admission states

- `declared_pending_witness` — named as part of the estate but ownership/runtime evidence has not yet been attached.
- `witnessed` — ownership/control evidence exists.
- `registered` — canonical registry record is complete enough for governed integration.
- `staging` — adapter/renter integration is under verification.
- `production` — currently governed as a production estate member.
- `suspended` — temporarily blocked from privileged KPGS actions.
- `decommissioned` — retained for historical evidence but no longer active.

A property MUST NOT move from `declared_pending_witness` to `witnessed` solely because its DNS name appears in documentation. Witnessing requires evidence from an explicitly authorized source such as registrar/DNS, deployment, repository or domain-control verification.

## Canonical linkage

Each production record should answer:

`DNS -> ownership evidence -> repo -> deployment -> adapter -> governance policy -> live release -> evidence bundle -> rollback target`

## Rules

1. Unknown discovered properties enter a review queue; KPGS does not automatically take control of them.
2. Raw secrets are forbidden in registry records.
3. Release and rollback references are versioned and inspectable.
4. Frontend technology is descriptive metadata, not a governance requirement.
5. The .NET reference adapter is a control-plane boundary; it does not require rewriting an existing frontend.
6. A property can remain partially registered while unknown fields are explicitly represented as `null`; unknown truth must not be fabricated.
