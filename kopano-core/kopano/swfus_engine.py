"""SWFUS Engine 3.0 — governed offline-first CRUD progression.

SWFUS = Sovereign Ingestion -> Witness Isolation -> Fluid Vectoring ->
Unified Synchronization -> Severance.

The runtime preserves local truth and evidence when transport is unavailable.
A sync failure is not automatically a governance failure, rejected updates never
erase witnessed state, and correlation-bound retries never duplicate mutation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import logging
import math
from typing import Any, Callable, Mapping

log = logging.getLogger("KESSA-SWFUS")

CRUD_ACTIONS = {"CREATE", "READ", "UPDATE", "DELETE"}
LEGACY_ACTIONS = {"TELEMETRY_INGESTION"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fingerprint(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class SwfusPayload:
    node_id: str
    action_type: str
    telemetry_value: float = 0.0
    is_hallucinated: bool = False
    data: Mapping[str, Any] = field(default_factory=dict)
    expected_revision: int | None = None
    correlation_id: str | None = None
    capability_lease_id: str | None = None


@dataclass(frozen=True)
class WitnessRecord:
    node_id: str
    revision: int
    telemetry_value: float
    data: Mapping[str, Any]
    tombstoned: bool
    updated_at: str
    evidence_hash: str


@dataclass(frozen=True)
class SwfusReceipt:
    node_id: str
    requested_action: str
    resolved_action: str
    accepted: bool
    stage: str
    sync_state: str
    revision: int | None
    correlation_id: str | None
    capability_lease_id: str | None
    evidence_hash: str
    reason: str | None
    observed_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SyncAdapter = Callable[[WitnessRecord, SwfusReceipt], bool]


class SwfusHierarchy:
    """Execute governed CRUD transitions while preserving offline evidence.

    `azure_sync_id` is retained only as a compatibility alias for older callers;
    it does not prove a live Azure connection. Real synchronization is represented
    only by an injected `sync_adapter` that returns an observed success/failure.
    """

    def __init__(
        self,
        azure_sync_id: str | None = None,
        *,
        sync_adapter: SyncAdapter | None = None,
        max_telemetry_value: float = 100.0,
    ) -> None:
        self.sync_id = azure_sync_id
        self.sync_adapter = sync_adapter
        self.max_telemetry_value = max_telemetry_value
        self.local_offline_db: dict[str, WitnessRecord] = {}
        self.quarantine_ledger: list[SwfusReceipt] = []
        self.receipt_ledger: list[SwfusReceipt] = []
        self.last_receipt: SwfusReceipt | None = None
        self._correlation_receipts: dict[str, SwfusReceipt] = {}
        self._correlation_fingerprints: dict[str, str] = {}
        log.info(
            "SWFUS Engine initialized; sync=%s",
            "configured" if sync_adapter else "offline-pending",
        )

    def execute(self, payload: SwfusPayload) -> bool:
        """Backward-compatible boolean wrapper around the receipt-bearing runtime."""
        return self.execute_with_receipt(payload).accepted

    def execute_with_receipt(self, payload: SwfusPayload) -> SwfusReceipt:
        """Run one payload through all governed SWFUS stages."""
        request_fingerprint = self._request_fingerprint(payload)
        replay = self._idempotent_replay(payload, request_fingerprint)
        if replay is not None:
            return replay

        ingest_reason = self._validate_ingestion(payload)
        if ingest_reason:
            return self._severance_execution(
                payload,
                ingest_reason,
                stage="sovereign_ingestion",
                request_fingerprint=request_fingerprint,
            )

        resolved_action = self._resolve_action(payload)
        transition = self._fluid_vectoring(payload, resolved_action)
        if isinstance(transition, str):
            return self._severance_execution(
                payload,
                transition,
                stage="fluid_vectoring",
                resolved_action=resolved_action,
                request_fingerprint=request_fingerprint,
            )

        record = transition
        self._witness_isolation(record)

        provisional = self._make_receipt(
            payload,
            resolved_action=resolved_action,
            accepted=True,
            stage="witness_isolation",
            sync_state="pending_sync",
            revision=record.revision,
            reason=None,
            evidence_hash=record.evidence_hash,
        )

        sync_state = self._unified_sync(record, provisional)
        receipt = self._make_receipt(
            payload,
            resolved_action=resolved_action,
            accepted=True,
            stage="unified_synchronization" if sync_state == "synced" else "witness_isolation",
            sync_state=sync_state,
            revision=record.revision,
            reason=None if sync_state == "synced" else "local witness accepted; external sync not proven",
            evidence_hash=record.evidence_hash,
        )
        self._record_receipt(receipt)
        self._remember_idempotency(payload, request_fingerprint, receipt)
        return receipt

    def read(self, node_id: str) -> WitnessRecord | None:
        record = self.local_offline_db.get(node_id)
        if record is None or record.tombstoned:
            return None
        return record

    def _request_fingerprint(self, payload: SwfusPayload) -> str:
        return _fingerprint(
            {
                "node_id": payload.node_id,
                "action_type": payload.action_type.strip().upper(),
                "telemetry_value": payload.telemetry_value,
                "is_hallucinated": payload.is_hallucinated,
                "data": dict(payload.data),
                "expected_revision": payload.expected_revision,
                "capability_lease_id": payload.capability_lease_id,
            }
        )

    def _idempotent_replay(
        self,
        payload: SwfusPayload,
        request_fingerprint: str,
    ) -> SwfusReceipt | None:
        correlation_id = payload.correlation_id
        if not correlation_id or not correlation_id.strip():
            return None

        previous = self._correlation_receipts.get(correlation_id)
        if previous is None:
            return None

        if self._correlation_fingerprints[correlation_id] == request_fingerprint:
            # Same intent + same correlation is a retry. Return the original verdict
            # without executing CRUD/vectoring again or incrementing revision.
            self.last_receipt = previous
            return previous

        return self._severance_execution(
            payload,
            "correlation_id cannot be reused for a different payload",
            stage="sovereign_ingestion",
            request_fingerprint=request_fingerprint,
            remember_idempotency=False,
        )

    def _remember_idempotency(
        self,
        payload: SwfusPayload,
        request_fingerprint: str,
        receipt: SwfusReceipt,
    ) -> None:
        correlation_id = payload.correlation_id
        if not correlation_id or not correlation_id.strip():
            return
        self._correlation_fingerprints[correlation_id] = request_fingerprint
        self._correlation_receipts[correlation_id] = receipt

    def _validate_ingestion(self, payload: SwfusPayload) -> str | None:
        if not payload.node_id.strip():
            return "node_id is required"
        action = payload.action_type.strip().upper()
        if action not in CRUD_ACTIONS | LEGACY_ACTIONS:
            return f"unsupported action_type: {payload.action_type}"
        if payload.correlation_id is not None and not payload.correlation_id.strip():
            return "correlation_id must be non-empty when supplied"
        if payload.is_hallucinated:
            return "payload explicitly marked hallucinated/untrusted"
        if not math.isfinite(payload.telemetry_value):
            return "telemetry_value must be finite"
        if abs(payload.telemetry_value) > self.max_telemetry_value:
            return "telemetry_value exceeds governed boundary"
        if payload.expected_revision is not None and payload.expected_revision < 0:
            return "expected_revision cannot be negative"
        return None

    def _resolve_action(self, payload: SwfusPayload) -> str:
        action = payload.action_type.strip().upper()
        if action == "TELEMETRY_INGESTION":
            current = self.local_offline_db.get(payload.node_id)
            return "UPDATE" if current and not current.tombstoned else "CREATE"
        return action

    def _fluid_vectoring(self, payload: SwfusPayload, action: str) -> WitnessRecord | str:
        current = self.local_offline_db.get(payload.node_id)
        active = current is not None and not current.tombstoned

        if action == "READ":
            if not active:
                return "read target does not exist"
            return current

        if action == "CREATE":
            if active:
                return "create target already exists"
            revision = 1 if current is None else current.revision + 1
            data = dict(payload.data)
            return self._build_record(payload, revision=revision, data=data, tombstoned=False)

        if not active:
            return f"{action.lower()} target does not exist"

        if payload.expected_revision is not None and payload.expected_revision != current.revision:
            return (
                "revision conflict: "
                f"expected {payload.expected_revision}, witnessed {current.revision}"
            )

        if action == "UPDATE":
            data = dict(current.data)
            data.update(dict(payload.data))
            return self._build_record(
                payload,
                revision=current.revision + 1,
                data=data,
                tombstoned=False,
            )

        if action == "DELETE":
            return self._build_record(
                payload,
                revision=current.revision + 1,
                data=dict(current.data),
                tombstoned=True,
            )

        return f"unhandled action: {action}"

    def _build_record(
        self,
        payload: SwfusPayload,
        *,
        revision: int,
        data: Mapping[str, Any],
        tombstoned: bool,
    ) -> WitnessRecord:
        observed_at = _utc_now()
        fingerprint_payload = {
            "node_id": payload.node_id,
            "revision": revision,
            "telemetry_value": payload.telemetry_value,
            "data": dict(data),
            "tombstoned": tombstoned,
            "observed_at": observed_at,
            "correlation_id": payload.correlation_id,
            "capability_lease_id": payload.capability_lease_id,
        }
        return WitnessRecord(
            node_id=payload.node_id,
            revision=revision,
            telemetry_value=payload.telemetry_value,
            data=dict(data),
            tombstoned=tombstoned,
            updated_at=observed_at,
            evidence_hash=_fingerprint(fingerprint_payload),
        )

    def _witness_isolation(self, record: WitnessRecord) -> None:
        self.local_offline_db[record.node_id] = record

    def _unified_sync(self, record: WitnessRecord, receipt: SwfusReceipt) -> str:
        if self.sync_adapter is None:
            return "pending_sync"
        try:
            return "synced" if self.sync_adapter(record, receipt) else "pending_sync"
        except Exception as exc:  # transport defects must not erase local truth
            log.warning("SWFUS sync adapter failed for %s: %s", record.node_id, exc)
            return "pending_sync"

    def _severance_execution(
        self,
        payload: SwfusPayload,
        reason: str,
        *,
        stage: str,
        resolved_action: str | None = None,
        request_fingerprint: str | None = None,
        remember_idempotency: bool = True,
    ) -> SwfusReceipt:
        """Quarantine the rejected attempt without deleting witnessed prior state."""
        evidence_hash = _fingerprint(
            {
                "node_id": payload.node_id,
                "action_type": payload.action_type,
                "telemetry_value": payload.telemetry_value,
                "data": dict(payload.data),
                "expected_revision": payload.expected_revision,
                "reason": reason,
            }
        )
        receipt = self._make_receipt(
            payload,
            resolved_action=resolved_action or payload.action_type.strip().upper(),
            accepted=False,
            stage=stage,
            sync_state="severed",
            revision=self.local_offline_db.get(payload.node_id).revision
            if payload.node_id in self.local_offline_db
            else None,
            reason=reason,
            evidence_hash=evidence_hash,
        )
        self.quarantine_ledger.append(receipt)
        self._record_receipt(receipt)
        if remember_idempotency:
            self._remember_idempotency(
                payload,
                request_fingerprint or self._request_fingerprint(payload),
                receipt,
            )
        log.warning(
            "[SWFUS SEVERED] node=%s stage=%s reason=%s",
            payload.node_id,
            stage,
            reason,
        )
        return receipt

    def _make_receipt(
        self,
        payload: SwfusPayload,
        *,
        resolved_action: str,
        accepted: bool,
        stage: str,
        sync_state: str,
        revision: int | None,
        reason: str | None,
        evidence_hash: str,
    ) -> SwfusReceipt:
        return SwfusReceipt(
            node_id=payload.node_id,
            requested_action=payload.action_type.strip().upper(),
            resolved_action=resolved_action,
            accepted=accepted,
            stage=stage,
            sync_state=sync_state,
            revision=revision,
            correlation_id=payload.correlation_id,
            capability_lease_id=payload.capability_lease_id,
            evidence_hash=evidence_hash,
            reason=reason,
            observed_at=_utc_now(),
        )

    def _record_receipt(self, receipt: SwfusReceipt) -> None:
        self.last_receipt = receipt
        self.receipt_ledger.append(receipt)
