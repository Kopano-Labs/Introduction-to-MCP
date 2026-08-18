# SWFUS Cross-Runtime Mapping

The Python runtime uses Pythonic `snake_case`; the portable domain wire contract uses JSON/TypeScript/.NET-friendly `camelCase`.

| Python runtime | Portable wire |
|---|---|
| `node_id` | `nodeId` |
| `action_type` | `action` |
| `telemetry_value` | `telemetryValue` |
| `expected_revision` | `expectedRevision` |
| `correlation_id` | `correlationId` |
| `capability_lease_id` | `capabilityLeaseId` |
| `requested_action` | `requestedAction` |
| `resolved_action` | `resolvedAction` |
| `sync_state` | `syncState` |
| `evidence_hash` | `evidenceHash` |
| `observed_at` | `observedAt` |

Adapters may translate field casing at their boundary. They must preserve values and semantics.

In particular:

```text
pending_sync != synced
severed != delete
DELETE -> tombstone + next revision
revision conflict -> fail closed
```
