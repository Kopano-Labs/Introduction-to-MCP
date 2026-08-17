# KPGS Capability Lease Contract

Issue: #42

## Purpose

A capability lease is the temporary authority a Stateless Renter, domain adapter, skill or agent receives to perform a bounded action. Identity answers **who/what is acting**. The capability lease answers **what that actor may do, to which resource, for which tenant/domain/task, and until when**.

## Rules

1. No privileged runtime receives ambient long-lived authority.
2. Every lease is short-lived and explicitly scoped.
3. Lease scope is intersected with the governing specification and policy decision; it cannot broaden either.
4. Expired or revoked leases fail closed.
5. A lease may reference a secret provider or delegated credential, but MUST NOT embed durable plaintext secrets.
6. Cross-tenant access is denied unless the lease explicitly names the additional tenant and policy permits it.
7. Sensitive use of a lease emits audit/evidence records tied to the same correlation chain as the task.

## Required dimensions

- subject: renter/adapter/skill/agent identity
- tenant
- domain
- task
- capabilities
- resource scopes
- issue/expiry timestamps
- nonce or unique lease identifier
- policy decision reference
- governing specification reference
- revocation status/reference

## Capability examples

Good capability scopes:

- `github.issue.write` on `RobynAwesome/Introduction-to-MCP`
- `estate.registry.read` on `kopano-labs`
- `domain.workflow.execute` on `kaslink:job-search`

Bad capability scopes:

- `admin`
- `all-access`
- a raw permanent API key exposed to the renter

## Verification requirements

A conformant implementation MUST prove:

- expired lease rejection;
- revoked lease rejection;
- resource-scope enforcement;
- tenant-scope enforcement;
- capability-scope enforcement;
- replay resistance for sensitive operations;
- audit correlation without exposing secret material.
