# KPGS Canonical .NET Domain Adapter

Issue: #36

## Role

The .NET adapter is the stable service/control-plane boundary between an existing domain application and Kopano Sovereign Hub. It is **not** a requirement to rewrite a React, Next, Vite, MERN or other existing frontend in .NET.

```text
Existing PWA / Domain UI
        |
        | tiny JSON/TypeScript client
        v
KPGS Domain Adapter (.NET 10 reference implementation)
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

The reference implementation targets `net10.0`. Package compatibility is versioned independently from the frontend stack.

## Package split

```text
dotnet/Kopano.Kpgs.Contracts
  DTOs, renter envelopes and protocol/version contracts only

dotnet/Kopano.Kpgs.Adapter
  ASP.NET Core service membrane, Hub client contract, capability checks,
  idempotency, bounded timeout/retry/circuit-breaker and endpoints

dotnet/Kopano.Kpgs.Realtime
  realtime event-plane client and canonical reconnect recovery

dotnet/Kopano.Kpgs.Evidence
  non-authoritative evidence emission and correlation helpers

dotnet/Kopano.Kpgs.Reference
  removable ASP.NET Core reference service + development-only mock Hub

dotnet/client/kpgs-client.ts
  zero-rewrite TypeScript binding for existing PWAs
```

`Contracts`, `Adapter`, `Realtime` and `Evidence` are packable NuGet projects. The split keeps domain applications from depending on the complete Hub implementation.

## Canonical runtime boundary

The adapter carries **no durable canonical business state**.

- Task/session truth is read from the injected `IKpgsHubClient`.
- The in-memory idempotency gate is transient duplicate-work coordination only.
- The reference evidence sink is observability evidence with `canonical=false` and `authorityEffect=none`.
- Production domains replace the reference evidence sink and mock Hub through dependency injection.
- Realtime events are transport hints; reconnect uses `ICanonicalSessionReader` before the UI resumes.
- Removing/restarting the adapter cannot require local business-state recovery; the replacement instance reloads from Hub.

## Privileged operation membrane

Every privileged operation resolves a Hub decision before domain mutation:

| Operation | Capability | Resource scope |
|---|---|---|
| register estate property | `domain.register` | `estate:<property>` |
| read session state | `session.read` | `session:<id>` |
| create governed task | `task.create` | `domain:<domain-id>` |
| send task command | `task.command` | `task:<task-id>` |
| read evidence | `evidence.read` | `task:<task-id>` |

A decision is usable only when the Hub returns `Allowed=true`, a lease ID and a future expiry. Policy/lease transport failure is fail-closed for privileged work.

The adapter never issues its own authority and browser identity headers are translation inputs only. A real domain MUST replace the reference identity translator with its authenticated server-side identity integration.

## Progressive update / bounded CRUD

The first task mutation pilot preserves the canonical sequence:

```text
APU -> Progressive Update -> #NB -> bounded CRUD -> SWFUS
```

- Task CREATE requires literal `#NB` and `crudIntent=CREATE`.
- Commands require literal `#NB`.
- Idempotency keys are bound to a SHA-256 fingerprint of tenant/domain/task + governed request content.
- Exact replay returns the same bounded result.
- Same key + changed governed content rejects with conflict.
- Only operations explicitly declared safe/idempotent are retried.
- Transport success is not represented as new canonical authority.

## HTTP surface

The reference adapter exposes:

- `GET /kpgs/health` — Hub readiness + protocol/adapter version
- `GET /kpgs/version` — adapter + protocol compatibility
- `GET /kpgs/session/{id}` — capability-gated canonical user-safe workflow snapshot
- `POST /kpgs/tasks` — capability-gated, idempotent governed CREATE
- `POST /kpgs/tasks/{id}/commands` — capability-gated idempotent command
- `GET /kpgs/tasks/{id}/evidence` — capability-gated evidence summary/reference

Domain-specific routes remain domain-specific.

## Resilience defaults

`KpgsHubInvoker` provides dependency-free bounded defaults:

- request timeout;
- retry only for calls declared idempotent;
- exponential retry delay;
- circuit breaker after consecutive transient failures;
- cancellation propagation;
- fail-closed capability/policy resolution.

A retry never creates permission and never turns an unscoped browser request into trusted work.

## Authentication and secrets

- No long-lived user/service secret belongs in browser-readable configuration.
- `IKpgsSecretProvider` is the server-side abstraction for secret references.
- The reference implementation accepts `env:` references only and is for local development.
- Capability leases are short-lived and resource/task scoped.
- Browser UI sessions do not grant Hub authority.

## Existing PWA migration — no frontend rewrite

1. Deploy the adapter as a sidecar/service for the domain.
2. Register real implementations of `IKpgsHubClient`, `IKpgsIdentityTranslator`, `IKpgsEvidenceSink` and `IKpgsSecretProvider`.
3. Map `app.MapKpgsAdapterEndpoints()` in the adapter service.
4. Copy or package `dotnet/client/kpgs-client.ts` into the existing JS/TS application.
5. Keep the current React/Next/Vite/MERN routes/components. Replace only the workflow/API call that needs KPGS governance with `KpgsClient`.
6. Preserve domain-specific rendering and offline behavior; use canonical session reload after realtime reconnect.
7. Promote only after the exact integration commit passes domain tests and evidence gates.

Example:

```ts
const kpgs = new KpgsClient("https://adapter.example", () => serverResolvedIdentity);
const task = await kpgs.createTask({
  governingSpecRef: "spec://my-domain/create-order/v1",
  input: formPayload,
  idempotencyKey: submissionId,
  updateId: progressiveUpdateId,
});
```

The PWA remains a PWA. It does not reimplement capability policy.

## Rollback / removal

The adapter is deliberately removable:

1. Stop routing the governed workflow to `/kpgs/*`.
2. Restore the previous domain API call or place the workflow in a truthful HOLD state.
3. Remove the `KpgsClient` call/import if the domain no longer uses the adapter.
4. Stop the adapter service / remove `MapKpgsAdapterEndpoints()`.
5. Do **not** migrate canonical task/business records out of the adapter: it never owns them.
6. On later reinstall, recover task/session state from Hub/canonical sources.

Rollback must never copy the transient idempotency cache or reference mock-Hub state into production truth.

## Local reference service

```bash
dotnet run --project dotnet/Kopano.Kpgs.Reference/Kopano.Kpgs.Reference.csproj
```

The reference `DevelopmentMockHubClient` exists only to demonstrate the removable integration shape. It is not Sovereign Hub and must not be deployed as a production authority service.

## Verification

The dependency-free proof executable validates:

```bash
dotnet run --project dotnet/Kopano.Kpgs.Tests/Kopano.Kpgs.Tests.csproj -c Release
```

It covers:

- machine-readable health/version;
- lease-bound privileged CREATE;
- exact replay and changed-payload collision;
- denied capability before mutation;
- policy transport outage fail-closed;
- literal `#NB` before capability/mutation;
- bounded retry of transient idempotent work;
- realtime reconnect + canonical recovery;
- adapter replacement/rollback recovering from Hub;
- versioned Stateless Renter envelopes;
- non-authoritative evidence tied to correlation + lease.

CI additionally builds the reference service and packs the four NuGet projects. Runtime promotion is tied to the exact commit that passes those gates.
