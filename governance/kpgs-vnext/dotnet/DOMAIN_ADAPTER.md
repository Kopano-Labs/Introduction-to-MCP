# KPGS Canonical .NET Domain Adapter

Issue: #36

## Role

The .NET adapter is the stable service/control-plane boundary between an existing domain application and Kopano Sovereign Hub. It is **not** a requirement to rewrite a React, Next, Vite, MERN or other existing frontend in .NET.

```text
Existing PWA / Domain UI
        |
        v
KPGS Domain Adapter (.NET reference implementation)
        |
        v
Kopano Sovereign Hub
        |
        +--> capability/policy
        +--> skill routing
        +--> realtime events
        +--> evidence
        `--> Stateless Renters
```

## Proposed package split

```text
Kopano.Kpgs.Contracts
  DTOs and protocol/version contracts only

Kopano.Kpgs.Adapter
  ASP.NET Core middleware and Hub client

Kopano.Kpgs.Realtime
  realtime session/event-plane client and fallback semantics

Kopano.Kpgs.Evidence
  evidence emission and correlation helpers
```

The split keeps domain applications from depending on the complete Hub implementation.

## Required HTTP surface

A reference adapter SHOULD expose:

- `GET /kpgs/health` — liveness/readiness summary
- `GET /kpgs/version` — adapter + protocol compatibility
- `GET /kpgs/session/{id}` — canonical user-safe workflow snapshot
- `POST /kpgs/tasks` — create a governed task from an accepted spec/input
- `POST /kpgs/tasks/{id}/commands` — idempotent user commands/approvals
- `GET /kpgs/tasks/{id}/evidence` — authorized evidence summary/reference

Domain-specific routes remain domain-specific.

## Hub client responsibilities

The adapter MUST:

1. register/resolve its estate property;
2. translate authenticated domain identity into Hub context without inventing authority;
3. request short-lived capability leases for privileged operations;
4. bind task requests to a governing specification;
5. pass renter/skill events through canonical correlation identifiers;
6. recover live state after transport reconnect from Hub/canonical sources;
7. emit evidence and release/version metadata;
8. fail closed when policy/lease verification is unavailable for a privileged action.

## Resilience primitives

The reference package SHOULD provide bounded defaults for:

- request timeout;
- retry of safe/idempotent operations;
- idempotency keys;
- circuit breaker;
- reconnect/backoff;
- cancellation;
- correlation/log context.

Retries MUST NOT turn a non-idempotent side effect into duplicate durable work.

## Authentication and secrets

- No long-lived user/service secret is stored in browser-readable configuration.
- The adapter may use a server-side secret provider reference.
- Renter capabilities are short-lived and task/resource scoped.
- Browser clients never become trusted merely because they possess a UI session.

## TypeScript/front-end interoperability

Canonical JSON schemas under `governance/kpgs-vnext/` are the language-neutral truth. TypeScript types MAY be generated from those schemas or exposed through a tiny client package.

The frontend should consume simple concepts such as:

- current task status;
- next available actions;
- user-safe explanation;
- approval requirement;
- offline/reconnect state.

It should not need to implement KPGS policy itself.

## Verification before runtime promotion

Actual NuGet/runtime implementation MUST remain unreleased until:

- the project builds on its target .NET SDK;
- contract/schema tests pass;
- unauthorized capability tests fail closed;
- retry/idempotency tests pass;
- realtime reconnect tests pass;
- at least one existing JS/TS PWA integrates without a frontend rewrite;
- rollback/removal of the adapter is demonstrated.

The current GitHub Actions billing lock prevents producing that executable evidence, so this file is a contract, not a claim that the .NET runtime package is already verified.
