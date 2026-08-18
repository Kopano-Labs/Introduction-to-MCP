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

## Runtime mapping

The canonical runtime implementation is intentionally layered rather than duplicated:

- `kopano-core/kopano/realtime_event_plane.py` owns the persistent replay journal, server cursor, duplicate handling, scoped subscriptions and bounded live queues. It owns **observable event history only**, never business truth.
- `kopano-core/kopano/swfus_realtime_bridge.py` is a one-way SWFUS distribution sink. The chain remains `Adaptive PU -> Progressive Update -> CRUD -> SWFUS -> realtime observation`; realtime delivery cannot call back into CRUD.
- `kopano-core/kopano/kasilink_realtime.py` adapts the existing KasiLink gig-match workflow to the event plane and exposes WebSocket-first delivery plus governed polling fallback.
- `kopano-core/kopano/kasilink_api.py` keeps the existing `/api/kasilink/match` surface and only adds optional session/task/correlation identifiers and realtime metadata. A realtime-journal fault does not block the existing business operation.

A subscriber is registered before replay is read. This intentionally permits a racing event to appear once in replay and once in the live queue; the transport suppresses that duplicate frame. Registering after replay would create an event-loss window and is forbidden.

Slow subscribers never block an authoritative producer. Non-critical progress may be dropped from a saturated live queue because it remains replayable from the persistent journal. Saturation on critical events forces reconnect/resume rather than pretending delivery occurred.

### Legacy broadcast surfaces

The older `/ws/live`, `/ws/neural-link`, `/ws/kasilink/live`, `/broadcast` and destructive shared `/updates` paths in the historical control-plane API are compatibility surfaces, **not** the canonical vNext realtime contract. New PWA/domain work must use the scoped event plane. They should be removed only after dependent legacy clients have migrated; their existence must not be used as proof that issue #40 reliability guarantees are present.

## SWFUS boundary

When the realtime journal is explicitly injected as a SWFUS `distribution_sink`, durable journal persistence is part of SWFUS distribution acceptance. If that persistence call fails, existing SWFUS fail-closed behavior holds/rolls back its non-authoritative projection. WebSocket disconnects and slow subscribers cannot trigger this rollback because subscriber fan-out is bounded and non-blocking.

This distinction is important:

- **journal persistence failure at the governed SWFUS distribution boundary** -> fail closed;
- **socket/polling delivery failure after persistence** -> business state remains untouched and the client resumes by cursor.

## Approval actions

A user approval is a governed command, not a UI click effect. Approval messages must carry an idempotency key and be re-checked against current policy/capability state at the server boundary before any external side effect occurs.

The realtime WebSocket accepts transport-control messages only (`auth`, `reauth`, `ack`, `ping`). Unknown or business-mutation messages are rejected and must be sent through a governed command endpoint. This keeps transport capability separate from mutation authority.
