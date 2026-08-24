# KPGS Canonical DNS Estate Migration Playbook

Issue: #44
Operational witness continuation: #102

## Purpose

Move one bounded workflow at a time behind the canonical KPGS control plane without rewriting a working frontend or moving durable authority into a Stateless Renter.

The playbook is deliberately two-layered:

1. **readiness assessment** — pure, non-authoritative evaluation of currently witnessed registry/evidence state;
2. **registry transition** — separately capability-gated mutation performed only through the Sovereign Estate Registry runtime.

`migration.py` implements layer 1. It cannot promote DNS state.

## Canonical sequence

```text
baseline
  -> register
  -> adapter integration
  -> capability map
  -> renter integration
  -> realtime / reconnect verification
  -> evaluation
  -> staging eligibility
  -> rollback drill
  -> production promotion eligibility
  -> observe
```

This maps issue #44's operational flow:

```text
baseline -> register -> adapter integration -> capability map -> renter integration
-> realtime wiring -> eval -> staging -> rollback drill -> production promotion -> observe
```

## Truth boundary

A migration assessment is never an estate-registry mutation.

```text
MIGRATION ASSESSMENT != REGISTRY AUTHORITY
CI FIXTURE != DNS OWNERSHIP WITNESS
STAGING READY != STAGING TRANSITION
PRODUCTION READY != PRODUCTION TRANSITION
TRANSPORT SUCCESS != CANONICAL STATE
```

The output always carries:

```json
{
  "canonical_registry_changed": false,
  "authority_effect": "none"
}
```

## Baseline gate

Before migration, record at minimum:

- repository/ref;
- deployment provider + target;
- health/evidence endpoint;
- rollback target + procedure.

A real operator should additionally capture the critical user journey, auth/session boundary, APIs/data stores, offline/PWA behavior and known mobile defects in `migration-template.json`.

## Registration gate

The migration engine respects the canonical Estate Registry. `declared_pending_witness` is HOLD.

A property may not be considered registered from memory, public search, repository visibility, or an application screenshot. The canonical registry requires witnessed ownership/domain-control evidence and the registration completeness contract from `../estate-registry/`.

A `witnessed` property can still remain HOLD when registration completeness is missing. Connected provider evidence proves observed control/deployment facts; it does not manufacture owner/governance/capability/health/adapter/renter state.

## Adapter gate

A property must declare a versioned adapter implementation. The reference implementation is:

```text
Kopano.Kpgs.Adapter
```

Existing React/Next/Vite/MERN/PWA frontends remain in place. The adapter is a service/control-plane boundary, not a UI rewrite requirement.

## Capability gate

A migrated workflow must declare the bounded capabilities it needs. The migration planner only verifies that a capability map exists; actual authorization remains the responsibility of the capability-lease authority at execution time.

## Stateless Renter gate

`renter_compatibility.status` must be `conformant` with an explicit protocol version before staging eligibility.

A renter remains disposable. Migration must survive renter destruction/recreation from governed Hub/context state.

## Realtime gate

Realtime improves immersion and recovery. It is not canonical storage.

The planner requires at least one governed health/evidence endpoint so reconnect behavior can be verified against authoritative state.

## Evaluation gate

The migration planner accepts the exact-commit receipt produced by the canonical evaluation loop. It requires:

- exact 40-character commit SHA;
- zero hard-gate failures;
- governance-admitted evidence bundle;
- a valid promotion decision (`hold` or `promote`).

A `HOLD` caused only by missing high-risk human approval may still be sufficient to prove **software/evidence staging readiness**. It is never sufficient for production promotion.

## Staging eligibility

A property becomes `ELIGIBLE_FOR_STAGING_TRANSITION` only when all of these software/evidence gates pass:

- baseline;
- canonical registration completeness;
- adapter version;
- capability map;
- conformant Stateless Renter protocol;
- health/reconnect evidence endpoint;
- exact-commit evaluation evidence.

The actual transition still requires the Estate Registry's `estate.release.transition` capability.

## Rollback drill

Rollback proof uses `kpgs.estate-rollback-drill.v1`.

A passing drill must:

- explicitly record `passed=true`;
- preserve `automatic_execution=false`;
- include evidence references.

The drill proves recoverability. It does not grant rollback authority.

A recorded provider rollback **candidate** is useful baseline evidence, but it is not the same thing as an executed rollback drill.

## Production eligibility

Production remains `NOT_REACHED` until all of the following are present:

- property is currently `staging`;
- staging readiness is still valid;
- rollback drill passed;
- release live ref exists;
- release evidence ref exists;
- rollback target exists;
- rollback procedure exists;
- promotion decision is `promote`;
- the promotion decision contains the required human approval reference.

Only then does the planner return:

```text
ELIGIBLE_FOR_PRODUCTION_TRANSITION
```

The capability-gated Estate Registry still owns the production transition.

## Current canonical estate behavior

As of the connected-provider witness receipt on 2026-08-24:

- `KasiLink.com` is `witnessed` with exact GitHub/Vercel evidence, but its apex and `www` hostnames remain attached to **two different Vercel project identities**. The singular deployment target remains intentionally `null`; both provider environments are preserved explicitly. Runtime authentication errors are also witnessed. Migration remains **HOLD**.
- `starfallsalvage.kopanolabs.com` is `witnessed` with exact repository, Vercel project, current READY deployment, live release evidence and a real prior deployment recorded as rollback target. Adapter/renter/capability/governance/health/evaluation and rollback-drill evidence remain incomplete. Migration remains **HOLD**.
- The other four declared estate properties remain `declared_pending_witness` until authoritative evidence is admitted.

Machine evidence: `../estate-registry/evidence/live-provider-witness-2026-08-24.json`.

Therefore, running the migration assessor against the current canonical registry must still produce **HOLD for all six properties**. The reason is now situational per property rather than the old blanket claim that every property lacks witness evidence.

## CI reference proof

Tests use clearly labelled **CI reference fixtures** for two domains to prove the software playbook is reusable:

- `KasiLink.com`
- `starfallsalvage.kopanolabs.com`

These fixtures are not production registry state and are not DNS ownership evidence. They demonstrate that the same planner can:

- reach staging eligibility when the required contracts/evidence exist;
- refuse production while human approval/rollback evidence is absent;
- reach production-transition eligibility only in an explicitly simulated approved fixture;
- preserve `canonical_registry_changed=false` throughout;
- produce deterministic migration IDs for the same property/workflow;
- apply the identical playbook to a second property.

The live witness regression test separately proves that real provider evidence can advance a property to `witnessed` while missing KPGS gates still produce HOLD.

## Operator workflow

1. Copy `migration-template.json` for the bounded workflow.
2. Populate baseline references from witnessed/current systems.
3. Update the canonical Estate Registry only through admitted governance/review surfaces; runtime production mutations still require the capability-gated registry operation.
4. Add adapter/renter/capability/health declarations only when their evidence exists.
5. Run the exact-commit evaluation/evidence loop.
6. Run migration assessment.
7. If staging-eligible, request the separately authorized staging transition.
8. Execute and receipt the rollback drill.
9. Re-evaluate the exact staging release.
10. Obtain required human approval for high/critical-risk promotion.
11. Request the separately authorized production transition.
12. Observe the declared window and issue a governed rollback recommendation if policy thresholds fail.

## Proof commands

```bash
python -m unittest discover -s tests -p 'test_estate_migration.py' -v
python -m unittest discover -s tests -p 'test_live_estate_witness_admission.py' -v
python governance/kpgs-vnext/migration/assess_estate.py
```
