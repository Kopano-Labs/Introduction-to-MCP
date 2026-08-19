# KPGS Canonical .NET Domain Adapter

Issue: #36

## Role

The .NET adapter is the stable service/control-plane boundary between an existing domain application and Kopano Sovereign Hub. It is **not** a requirement to rewrite a React, Next, Vite, MERN or other existing frontend in .NET.

```text
Existing PWA / Domain UI
        |
        v
KPGS Domain Adapter (.NET)
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

## Executable preview packages

```text
dotnet/Kopano.Kpgs.Contracts
  DTOs + protocol/version negotiation

dotnet/Kopano.Kpgs.Adapter
  lease/policy membrane, idempotency, resilience and ASP.NET route mapper

dotnet/Kopano.Kpgs.Realtime
  snapshot-first WS → SSE → polling fallback contract

dotnet/Kopano.Kpgs.Evidence
  correlation + evidence digest emission

dotnet/Kopano.Kpgs.ReferenceAdapter
  local ASP.NET Core reference service + mock Hub

dotnet/Kopano.Kpgs.Adapter.Tests
  dependency-free executable lifecycle/auth/realtime/rollback proof
```

All four reusable class libraries are configured as versioned NuGet-packable projects. They are preview artifacts; repository build proof does not mean a public NuGet feed publication has occurred.

## Required HTTP surface

The reference adapter exposes:

- `GET /kpgs/health` — liveness/readiness summary
- `GET /kpgs/version` — adapter + protocol compatibility
- `GET /kpgs/session/{id}` — user-safe workflow snapshot
- `POST /kpgs/tasks` — governed task creation
- `POST /kpgs/tasks/{id}/commands` — idempotent governed user commands
- `GET /kpgs/tasks/{id}/evidence` — authorized evidence summary

Domain-specific routes remain domain-specific.

## Hub client responsibilities

`IKpgsHubClient` keeps the adapter bounded to Hub-owned authority. The adapter:

1. registers its estate/domain manifest;
2. translates authenticated domain identity into `HubContext` without inventing authority;
3. requests a short-lived capability decision before privileged create/command paths;
4. binds task requests to governing spec, task, tenant and correlation identity;
5. emits evidence after admitted operations;
6. restores realtime state from snapshot before deltas;
7. exposes health/version compatibility;
8. fails closed when the Hub rejects registration, readiness or capability admission.

The adapter itself carries no durable canonical business state. Its process-local idempotency cache is only a front-line duplicate suppressor; the Hub/domain authority remains responsible for durable replay semantics.

## Resilience and idempotency

`KpgsResiliencePolicy` provides bounded timeout/retry/circuit behavior only for operations classified as safe reads/control checks. Privileged task creation and commands are **not transparently retried** by the adapter. They carry caller idempotency keys and rely on the Hub/domain authority for durable replay protection.

```text
SAFE READ / HEALTH → bounded retry permitted
PRIVILEGED MUTATION → capability lease + idempotency key + one Hub call
TRANSPORT RETRY != PERMISSION TO REPEAT SIDE EFFECT
```

## Realtime

`KpgsRealtimeClient` follows the canonical event-plane posture:

```text
canonical snapshot
→ WebSocket attempt
→ SSE fallback
→ governed polling fallback
→ deduplicate monotonically by sequence
```

Reconnect obtains a fresh snapshot before consuming deltas. Transport availability never becomes business authority.

## Authentication and secrets

- No long-lived user/service secret belongs in browser-readable configuration.
- `IKpgsSecretProvider` is the server-side secret-provider abstraction; consumers pass references rather than browser secrets.
- Renter capabilities are task/resource scoped and resolved through the Hub.
- Browser clients remain untrusted input even when they have an authenticated UI session.

## Existing JS/TS PWA integration

`governance/kpgs-vnext/dotnet/typescript/kpgs-adapter-client.ts` is the small frontend binding. An existing PWA imports/ports this client and continues using its current React/Next/Vite stack.

The browser sees everyday concepts:

- current task status;
- next available actions;
- user-safe explanation;
- approval commands;
- connectivity/recovery state.

It does not implement KPGS policy and it does not receive Hub authority merely because it can call the adapter.

## Local reference profile

Run the reference adapter after restoring/building the projects:

```bash
dotnet run --project dotnet/Kopano.Kpgs.ReferenceAdapter/Kopano.Kpgs.ReferenceAdapter.csproj
```

The local profile uses an explicit `LocalMockHub` and `localhost.kpgs` estate default. It is development proof only, not a production Sovereign Hub.

## Verification and packaging

The exact-head `.NET Domain Adapter Proof` workflow must:

```text
dotnet restore
→ dotnet build -warnaserror
→ run lifecycle/auth/idempotency/realtime/rollback proof
→ dotnet pack four reusable packages
```

Acceptance remains bounded:

```text
ADAPTER BUILD != PUBLIC NUGET RELEASE
MOCK HUB != PRODUCTION HUB
PROCESS IDEMPOTENCY CACHE != DURABLE BUSINESS AUTHORITY
REALTIME TRANSPORT != AUTHORITY
PWA INTEGRATION != FRONTEND REWRITE
```
