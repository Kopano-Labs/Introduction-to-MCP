# KPGS Sovereign Task Contract v0.1

Status: **Phase 0 / contract POC / non-production**

This slice makes task authority independent of MCP sessions, agent processes, model runtimes, and transports.

## Governing invariant

```text
principal identity
    +
explicit capability grant
    +
governing policy/spec
    ↓
KPGS task receipt
    ↓
protocol adapter (MCP/A2A/local/other)
    ↓
disposable executor
```

A protocol task handle is a correlation mechanism. It is **not** canonical task authority.

## Contract artifacts

- `principal-envelope.schema.json` — protocol-neutral identity, accountable principal, key/credential reference, and explicit capability grants.
- `task-receipt.schema.json` — canonical task state, receipt sequence/hash chain, policy lineage, idempotency key, protocol mapping, and metadata-only evidence references.
- `adapter.py` — deterministic reference adapter and conformance harness for MCP `2026-07-28`.
- `tests/test_kpgs_task_contract.py` — destruction/resume, duplicate-delivery, canonicalization, capability-denial, and MCP mapping tests.

## MCP 2026-07-28 boundary

KPGS follows the final MCP `2026-07-28` semantics at the adapter boundary:

- requests are stateless and carry protocol/client metadata per request;
- `server/discover` is available for version/capability discovery;
- protocol semantics are transport-independent;
- Tasks are an opt-in extension under `io.modelcontextprotocol/tasks`;
- MCP external task IDs remain external correlation identifiers.

KPGS does **not** put canonical task truth in:

- an MCP connection;
- an `initialize`-era session;
- a transport stream;
- a model context window;
- a Stateless Renter;
- an external task handle.

The adapter may be destroyed and recreated while the canonical ledger survives.

Primary MCP references:

- `modelcontextprotocol/modelcontextprotocol/docs/specification/2026-07-28/`
- `modelcontextprotocol/modelcontextprotocol/docs/specification/2026-07-28/server/discover.mdx`
- `modelcontextprotocol/modelcontextprotocol/docs/specification/2026-07-28/basic/transports/`
- `modelcontextprotocol/modelcontextprotocol` release note: `2026-07-28 Specification`

## Principal/capability law

Identity, authorization, delegation, transport, and governance are separate claims.

```text
principal_id               who is acting
accountable_principal_id   who is accountable where delegation exists
identity                   how the principal is verified
capability_grant           what it may attempt
protocol                   how the request arrived
KPGS policy                whether execution is permitted now
```

No current DID/AIP/agent-identity draft is constitutionalized by this v0.1 contract. Credential schemes are adapter choices behind the `identity` envelope.

## Receipt law

Each state mutation emits a new receipt:

```text
receipt[n]
   sha256
      ↓
receipt[n+1].previous_receipt_sha256
```

Required properties:

1. stable `task_id`;
2. monotonically increasing `sequence`;
3. explicit `principal_id` and `capability_grant_id`;
4. governing spec/policy lineage;
5. replay-safe `idempotency_key`;
6. protocol mapping kept subordinate to KPGS identity;
7. evidence represented by SHA-256 reference by default;
8. terminal states cannot silently resume.

## Privacy boundary

`evidence_refs[].content_captured` is locked to `false` in the v0.1 schema.

The receipt records:

```text
hash + optional governed reference
```

not raw prompts, retrieved documents, tool arguments, user data, or model outputs.

A later evidence-store contract may authorize encrypted content capture separately. Observability must not widen evidence disclosure by default.

## Conformance gates

This v0.1 POC must prove:

- **capability before execution** — an unauthorized operation fails before task creation;
- **duplicate delivery safety** — one idempotency key resolves to one canonical task;
- **process destruction safety** — replacing the adapter does not erase task state;
- **receipt continuity** — each mutation extends the prior receipt hash;
- **deterministic canonicalization** — equivalent JSON objects hash identically regardless of key order;
- **external handle non-authority** — MCP task IDs never replace KPGS task IDs;
- **metadata-only evidence** — evidence payloads are hashed and discarded by the reference adapter.

## Scope boundary

This is intentionally a narrow vertical slice. It does not yet claim:

- production persistence;
- live MCP SDK integration;
- DID/X.509 deployment;
- distributed consensus;
- CRDT reconciliation;
- iroh/libp2p transport;
- production signing/HSM integration.

The next isolated POC is offline replicated non-authoritative state. It must not be allowed to mutate this constitutional task contract merely because a CRDT converges.
