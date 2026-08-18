# KPGS Sovereign Hub DNS Estate Registry

Issue: #35

The estate registry is canonical KPGS control-plane state for governed DNS properties. It does not discover authority by guessing, and it does not promote a repository, deployment or DNS name merely because a connector can see it.

## Canonical workflow

```text
discover
  -> unwitnessed review queue
  -> witness
  -> classify
  -> register
  -> adapt
  -> verify
  -> staging
  -> production
  -> observe
  -> rollback | suspend | decommission
```

The reference runtime is `registry.py`.

## Discovery law

Unknown assets discovered through authorized sources become **candidates**, not registry properties.

Accepted provenance kinds:

- registrar
- DNS
- deployment
- repository
- domain-control
- other explicitly governed evidence

A candidate is deduplicated case-insensitively by DNS name while preserving multiple provenance observations. Duplicate discovery never creates multiple registry identities.

Candidate states:

```text
unwitnessed -> witnessed -> classified -> registered
       \                         
        -> rejected
```

The machine contract is `discovery-candidate.schema.json`.

## Initial estate truth

`estate.json` intentionally keeps the six initial properties at `declared_pending_witness` until authoritative witness evidence is supplied:

- `KasiLink.com`
- `FivesArena.com`
- `starfallsalvage.kopanolabs.com`
- `crisisconnect.kopanolabs.com`
- `KopanoLabs.com`
- `KRRababalela.com`

The runtime does not silently enrich or promote these records from memory, public search or unrelated connector visibility.

## Capability-lease boundary

Every mutation consumes the executable Phase‑1 capability lease runtime from issue #42. Typical capabilities are:

- `estate.discovery.write` on `estate:<estate_id>`
- `estate.registry.witness` on `dns:<domain>`
- `estate.registry.classify` on `dns:<domain>`
- `estate.registry.write` on `dns:<domain>`
- `estate.release.transition` on `dns:<domain>`
- `estate.release.rollback` on `dns:<domain>`

Tenant, Hub domain, task, capability and resource scope must all match the lease. Each operation also requires a unique operation nonce.

## Registration completeness

A property cannot enter `registered` without:

- ownership witness evidence;
- owner reference;
- at least one repository;
- deployment provider + target;
- adapter declaration;
- Stateless Renter compatibility state;
- governance policy, risk class and tier;
- at least one granted capability;
- at least one health/evidence endpoint;
- secret-provider references represented as references only, never raw secrets.

The registry schema also supports skills and named staging/production deployment environments.

## Release state transitions

General admitted transitions:

```text
registered -> staging | suspended | decommissioned
staging    -> production | registered | suspended
production -> staging | suspended
suspended  -> registered | decommissioned
decommissioned -> terminal
```

`declared_pending_witness -> witnessed` and `witnessed -> registered` use dedicated witness/registration operations so the runtime can enforce their stronger evidence requirements.

### Production promotion

Promotion from staging to production requires all of:

- live release reference;
- deployment/evidence reference;
- rollback target reference;
- rollback procedure reference.

No release receipt means no production transition.

### Rollback

Rollback is an explicit governed action. A production property with a valid rollback target/procedure moves back to `staging` with its live reference set to the rollback target. It must be verified again before another production promotion.

## Realtime / SWFUS relationship

Registry mutation is canonical control-plane authority **after a valid capability lease admits the operation**.

A registry event may then be emitted to the realtime plane / SWFUS for projection alignment. If that transport is unavailable:

- the canonical registry commit remains valid;
- the event records `distribution_status=unavailable`;
- transport is explicitly marked `transport_grants_authority=false`.

This preserves the vNext law:

> **Availability and synchronization are not authority.**

The event plane may later replay the missed projection from canonical registry/evidence state.

## Plain-language Hub answers

`explain_property(domain)` answers the operational questions without requiring an operator to inspect raw JSON:

- what property is this and what lifecycle state is it in?
- which repositories back it?
- where is it deployed?
- what adapter version is declared?
- is it Stateless-Renter compatible?
- which governance policy applies?
- what live release is recorded?
- what rollback target is available?

Unknown values are stated as **not witnessed / not promoted / not recorded** rather than inferred.

## Proof

`tests/test_sovereign_estate_registry.py` proves:

- all six initial DNS names remain present and conservatively unpromoted;
- new discoveries enter an unwitnessed queue;
- duplicate discoveries deduplicate while preserving provenance;
- witness → classify → register ordering cannot be skipped;
- cross-tenant mutation is rejected by the real capability-lease runtime;
- declared properties cannot skip witness/registration;
- production promotion requires evidence + rollback receipts;
- rollback is an explicit state transition;
- plain-language answers expose unknowns instead of guessing;
- event-plane failure does not erase an authorized canonical registry commit.
