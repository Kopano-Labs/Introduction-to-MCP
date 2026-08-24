# KPGS Sovereign DNS Estate Registry

Issue: #35
Operational witness lane: #102

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

## Connected-provider witness law

A connected provider/account surface may support a `witnessed` admission when it directly exposes the domain binding, project/deployment identity, repository linkage or equivalent control evidence. The witness must be receipted; a public HTTP response by itself is not domain-control proof.

Canonical machine receipt contract: `live-provider-witness.schema.json`.

A witness receipt has **witness-only** authority:

```text
connected provider observation
  -> evidence receipt
  -> witnessed registry state
  != registered
  != staging
  != production promotion
```

The receipt must preserve exact provider/project/deployment/repository identifiers and any material contradiction or unknown. Missing adapter, renter, capability, policy, health, evaluation or rollback evidence stays missing; it must not be inferred merely because a provider reports `READY`.

When two public hostnames are attached to different provider projects, the registry should preserve the split explicitly rather than collapse it into a fictional single deployment target. A shared Git commit does not make two provider project identities the same deployment.

Provider mutation and witness admission are separate authorities. If the current tool surface cannot perform a domain cutover, the correct state is `HOLD`; do not guess DNS records or narrate a cutover that did not occur.

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
7. Connected-account evidence may admit `witnessed`, but provider availability/READY state never self-promotes the property to `registered`, `staging` or `production`.
8. A rollback target reference is not a rollback-drill receipt and does not grant rollback execution authority.
