# KPGS Capability Lease Contract

Issue: #42

## Purpose

A capability lease is the temporary authority a Stateless Renter, domain adapter, skill or agent receives to perform a bounded action. Identity answers **who/what is acting**. The capability lease answers **what that actor may do, to which resource, for which tenant/domain/task, and until when**.

The reference runtime is `capability_lease.py`. It is standard-library only and proves the lease semantics without requiring a frontend rewrite or placing signing authority inside a renter.

## Rules

1. No privileged runtime receives ambient long-lived authority.
2. Every lease is short-lived and explicitly scoped.
3. Lease scope is intersected with the governing specification and policy decision; it cannot broaden either.
4. Expired or revoked leases fail closed.
5. A lease may reference a secret provider or delegated credential, but MUST NOT embed durable plaintext secrets.
6. Cross-tenant/domain/task access is denied when the requested scope does not exactly match the lease.
7. Sensitive use of a lease emits audit/evidence records tied to the same correlation chain as the task.
8. Each lease carries a unique lease nonce; each sensitive authorization requires a separate operation nonce so transport retries cannot silently duplicate side effects.
9. Signing-key rotation changes the active server-side key while prior verification keys remain available only for already-issued live leases. Frontends do not own or rotate signing keys.
10. Lease verification is not canonical business-state authority. It admits a bounded action to the next governed layer.

## Identity boundary

The compact reference token is a **KPGS lease envelope**, not a claim that KPGS has invented a new identity provider or a fully conformant JWT implementation.

An upstream OIDC/JWT/session boundary may authenticate a subject. The Sovereign Hub/policy boundary then translates that authenticated identity plus policy/specification decision into a short-lived capability lease.

```text
OIDC / JWT / governed session identity
        ↓
policy + governing specification
        ↓
KPGS capability lease
        ↓
exact tenant/domain/task/resource authorization
        ↓
Stateless Renter / adapter / skill operation
        ↓
audit + evidence
```

The renter never receives the signing key ring.

## Required dimensions

- subject: renter/adapter/skill/agent/human/service identity
- tenant
- domain
- task
- capabilities
- exact resource scopes
- issue/expiry timestamps
- unique lease nonce
- policy decision reference
- governing specification reference
- audit correlation + evidence reference
- optional secret-provider references
- revocation state managed by the issuing authority

The JSON contract is `capability-lease.schema.json`.

## Capability examples

Good capability scopes:

- `github.issue.write` on `RobynAwesome/Introduction-to-MCP`
- `estate.registry.read` on `kopano-labs`
- `domain.workflow.execute` on `kaslink:job-search`

Bad capability scopes:

- `admin`
- `all-access`
- `*`
- wildcard resource scope `*`
- a raw permanent API key exposed to the renter

The reference runtime intentionally uses exact resource matches. Broader/pattern scope semantics require a separate policy decision rather than being inferred by the lease library.

## Compact signed envelope

The reference token has three URL-safe Base64 segments:

```text
<header>.<lease-payload>.<HMAC-SHA256 signature>
```

The protected header carries:

- `typ=KPGS-LEASE`
- `alg=HS256`
- `kid=<server key id>`
- `iss=<configured lease authority>`

The payload is the machine-readable capability lease. The signature covers header + payload. Signature verification uses constant-time comparison.

This format is intentionally small and auditable. Production deployments may replace the signing implementation with a hardware-backed/JWS/JWT-compatible service as long as the same KPGS scope, expiry, revocation, replay and evidence invariants remain intact.

## Short-lived authority

The reference authority enforces a maximum lease TTL before signing and verifies the same maximum again when consuming a token. A caller cannot extend a lease simply by editing the payload because the signature would fail.

Time checks fail closed for:

- expiration;
- future/not-yet-active issuance;
- non-positive lifetimes;
- lifetimes exceeding configured KPGS policy.

## Revocation

The issuing authority maintains revocation state keyed by `lease_id`. Revocation requires a reason and evidence reference and emits a sanitized audit event.

A revoked lease cannot authorize another action even if its cryptographic signature and expiry remain valid.

## Replay resistance

Two replay boundaries are separate:

1. **Lease nonce** — unique identity material for the lease itself.
2. **Operation nonce** — supplied for every sensitive authorization attempt and consumed only after tenant/domain/task/capability/resource checks pass.

The same `(lease_id, operation_nonce)` pair cannot authorize twice.

This protects side-effecting operations from duplicate transport delivery without pretending transport is authoritative state.

## Key rotation

`KeyRing.rotate(new_kid, new_key)` changes the key used for newly issued leases. Existing, non-expired leases continue to verify against their original `kid` while that old verification key remains in the ring.

Operational rule:

> Do not retire an old verification key until every lease signed by it has expired or been revoked.

Because `kid` is inside the signed envelope header, a PWA/frontend does not require redeployment when the Sovereign Hub rotates signing keys.

## Audit/evidence boundary

Audit records contain reconstructable authorization metadata:

- lease ID
- subject ID/kind
- tenant/domain/task
- requested capability/resource
- allow/deny outcome and reason class
- correlation ID
- evidence reference
- signing key ID
- timestamp

They explicitly do **not** contain:

- raw compact lease token
- signing key bytes
- secret-provider values
- raw delegated credentials

Secret provider fields in leases are URI-like references only, for example `vault://runtime/github-write`.

## Verification requirements

A conformant implementation MUST prove:

- valid exact-scope authorization;
- expired lease rejection;
- revoked lease rejection;
- resource-scope enforcement;
- tenant/domain/task-scope enforcement;
- capability-scope enforcement;
- signature-tamper rejection;
- replay resistance for sensitive operations;
- short-lived TTL enforcement;
- ambient `admin`/`all-access`/wildcard rejection;
- audit correlation without exposing secret material;
- signing-key rotation while existing live leases remain verifiable;
- retirement of an active key fails closed.

These behaviors are exercised by `tests/test_capability_lease_runtime.py` and the KPGS vNext Contract Gate.
