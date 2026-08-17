# KPGS Realtime Event Plane

Issue: #40

## Purpose

The event plane connects an Adaptive PWA or domain UI to Kopano Sovereign Hub and active Stateless Renters with live progress, approvals and recovery signals. It makes the experience feel responsive without turning the network connection into a source of truth.

## Transport order

1. WebSocket when a bidirectional persistent connection is available.
2. Server-Sent Events when the client mainly needs server-to-client streaming.
3. Governed polling when constrained networks or infrastructure prevent streaming transports.

Transport selection is an implementation detail. The canonical task/event semantics stay the same.

## User-visible states

Everyday UI should reduce connection/runtime complexity to a small state model:

- `ready`
- `working`
- `waiting-for-approval`
- `offline`
- `reconnecting`
- `done`
- `failed`

The UI MAY provide technical detail through progressive disclosure, but must not require the user to understand WebSockets, renters or correlation IDs to recover.

## Reliability rules

- A disconnected socket MUST NOT erase canonical task state.
- Reconnect MUST use a server-recognized cursor/checkpoint rather than trusting client-only progress.
- Duplicate event delivery MUST be safe.
- Privileged client events MUST be authorized server-side even if the UI already hid/disabled the action.
- Event queues MUST be bounded and apply backpressure or coalescing where appropriate.
- Heartbeat/timeout behavior MUST distinguish `offline`, `reconnecting` and actual task failure.
- A reconnecting client MUST be able to request the current canonical workflow snapshot before consuming new deltas.

## Event semantics

The renter event envelope in `../stateless-renter/renter-envelope.schema.json` is the canonical execution event shape. The event plane may add transport framing, but must preserve:

- tenant/domain/task/correlation identity;
- event kind;
- sequence/cursor where ordering matters;
- capability/policy decision references for privileged actions;
- evidence references;
- failure/recovery classification.

## Approval actions

A user approval is a governed command, not a UI click effect. Approval messages must carry an idempotency key and be re-checked against current policy/capability state at the server boundary before any external side effect occurs.
