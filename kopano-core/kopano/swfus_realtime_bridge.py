"""SWFUS -> KPGS realtime distribution adapter.

The bridge is deliberately one-way. SWFUS remains the governed update executor;
the event plane persists observable distribution evidence and never calls CRUD.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from .realtime_event_plane import RealtimeEventPlane, make_event


@dataclass(frozen=True)
class SwfusRealtimeContext:
    tenant_id: str
    domain_id: str
    session_id: str
    task_id: str
    renter_id: str = "swfus.framework-distributor"
    lease_id: str = "lease:swfus-framework-distributor"

    def validate(self) -> None:
        for field_name in ("tenant_id", "domain_id", "session_id", "task_id"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")


class SwfusRealtimeDistributionSink:
    """Callable sink accepted by ``SwfusHierarchy(distribution_sink=...)``.

    Persistence failure is intentionally raised to SWFUS. The SWFUS runtime
    already treats a failed distribution sink as HOLD and atomically restores
    its non-authoritative projection. Slow or disconnected subscribers cannot
    cause that failure because live fan-out is bounded and non-blocking.
    """

    def __init__(
        self,
        event_plane: RealtimeEventPlane,
        context: SwfusRealtimeContext,
    ) -> None:
        context.validate()
        self.event_plane = event_plane
        self.context = context

    @staticmethod
    def _digest(event: Mapping[str, Any]) -> str:
        encoded = json.dumps(
            dict(event),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def __call__(self, distribution_event: dict[str, Any]) -> None:
        if distribution_event.get("schema") != "kpgs.swfus.distribution.v1":
            raise ValueError("unsupported SWFUS distribution schema")
        if distribution_event.get("canonical") is not False:
            raise ValueError("realtime bridge only accepts non-canonical projections")
        if distribution_event.get("authority_effect") != "none":
            raise ValueError("realtime transport cannot widen authority")
        if distribution_event.get("transport_grants_authority") is not False:
            raise ValueError("transport authority invariant failed")

        digest = self._digest(distribution_event)
        evidence = tuple(
            {"kind": "swfus", "ref": str(ref)}
            for ref in distribution_event.get("evidence_refs", ())
        )
        update_id = str(distribution_event.get("update_id", ""))
        correlation_id = str(distribution_event.get("correlation_id", ""))
        if not update_id or not correlation_id:
            raise ValueError("SWFUS distribution identity is incomplete")

        self.event_plane.publish(
            make_event(
                event_id=f"swfus-{digest[:32]}",
                event_kind="task.progress",
                tenant_id=self.context.tenant_id,
                domain_id=self.context.domain_id,
                session_id=self.context.session_id,
                task_id=self.context.task_id,
                correlation_id=correlation_id,
                renter_id=self.context.renter_id,
                lease_id=self.context.lease_id,
                idempotency_key=f"swfus:{update_id}:{digest}",
                payload={
                    "state": "working",
                    "stage": "distribution",
                    "update_id": update_id,
                    "node_id": distribution_event.get("node_id"),
                    "operation": distribution_event.get("operation"),
                    "state_digest": distribution_event.get("state_digest"),
                    "canonical": False,
                    "authority_effect": "none",
                },
                evidence=evidence,
                governing_spec_ref=(
                    "governance/kpgs-vnext/progressive-updates/README.md"
                ),
            )
        )
