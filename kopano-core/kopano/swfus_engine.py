"""Canonical Adaptive Progressive Updates -> CRUD -> SWFUS runtime.

SWFUS means State-Wide Framework Universal Synchronization in this vNext
surface. Synchronization aligns governed framework state; it never grants
canonical authority.

Canonical stage law:
Telemetry -> Classification -> Routing -> Protocol Selection ->
Invariant Audit -> POC/FOC Check -> State Update -> Distribution

The legacy SwfusPayload/SwfusHierarchy.execute(bool) API remains as a bounded
compatibility adapter. New code should call execute_update() and consume the
receipt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import logging
import math
from typing import Any, Callable, MutableMapping

log = logging.getLogger("KPGS-SWFUS")

SWFUS_CANONICAL_NAME = "State-Wide Framework Universal Synchronization"
SWFUS_STAGE_ORDER = (
    "TELEMETRY",
    "CLASSIFICATION",
    "ROUTING",
    "PROTOCOL_SELECTION",
    "INVARIANT_AUDIT",
    "POC_FOC_CHECK",
    "STATE_UPDATE",
    "DISTRIBUTION",
)
ALLOWED_STATE_CLASSES = {
    "non_authoritative",
    "derived_projection",
    "pending_proposal",
}
MUTATING_OPERATIONS = {"CREATE", "UPDATE", "DELETE"}


class CrudOperation(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class UpdateDisposition(str, Enum):
    APPLIED = "APPLIED"
    OBSERVED = "OBSERVED"
    HELD = "HELD"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ProgressiveUpdate:
    update_id: str
    node_id: str
    operation: CrudOperation | str
    lane: str
    context_route: str
    protocol: str
    idempotency_key: str
    value: Any = None
    apu_status: str = "UNSPECIFIED"
    poc_validated: bool = False
    foc_detected: bool = False
    invariant_passed: bool = True
    authority_effect: str = "none"
    state_class: str = "non_authoritative"
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    correlation_id: str = ""
    source: str = "apu"
    expected_version: int | None = None
    boundary_marker: str = "#NB"

    def operation_name(self) -> str:
        if isinstance(self.operation, CrudOperation):
            return self.operation.value
        return str(self.operation).upper().strip()


@dataclass(frozen=True)
class StageReceipt:
    stage: str
    status: str
    reason: str


@dataclass(frozen=True)
class SwfusReceipt:
    schema: str
    receipt_id: str
    update_id: str
    node_id: str
    operation: str
    disposition: str
    stages: tuple[StageReceipt, ...]
    synchronized: bool
    canonical_authority_changed: bool
    state_digest: str | None
    evidence_refs: tuple[str, ...]
    correlation_id: str
    boundary_marker: str
    replayed: bool = False
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["stages"] = [asdict(stage) for stage in self.stages]
        return payload


@dataclass
class SwfusPayload:
    """Legacy telemetry adapter payload.

    Kept for callers such as KESSA. It cannot bypass the canonical vNext
    validation order and cannot grant authority.
    """

    node_id: str
    action_type: str
    telemetry_value: float
    is_hallucinated: bool = False


class SwfusHierarchy:
    """Governed progressive-update executor.

    The internal projection store is explicitly non-authoritative. A caller may
    inject another mutable projection store and/or a distribution sink, but
    neither becomes an authority source merely by being connected here.
    """

    def __init__(
        self,
        projection_store: MutableMapping[str, dict[str, Any]] | None = None,
        distribution_sink: Callable[[dict[str, Any]], None] | None = None,
        *,
        azure_sync_id: str | None = None,
    ):
        # azure_sync_id is accepted only for source compatibility. It no longer
        # controls routing or implies Azure synchronization.
        self.azure_sync_id = azure_sync_id
        self.projection_store = projection_store if projection_store is not None else {}
        self.local_offline_db = self.projection_store  # legacy read alias
        self.distribution_log: list[dict[str, Any]] = []
        self._distribution_sink = distribution_sink
        self._idempotency: dict[str, tuple[str, SwfusReceipt]] = {}

    @staticmethod
    def _stable_json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

    def _update_digest(self, update: ProgressiveUpdate) -> str:
        payload = asdict(update)
        payload["operation"] = update.operation_name()
        return hashlib.sha256(self._stable_json(payload).encode("utf-8")).hexdigest()

    @staticmethod
    def _state_digest(record: Any) -> str | None:
        if record is None:
            return None
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def _receipt_id(update_digest: str, disposition: str, state_digest: str | None) -> str:
        seed = f"swfus-vnext:{update_digest}:{disposition}:{state_digest or 'none'}"
        return "swfus_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _valid_text(value: str) -> bool:
        return isinstance(value, str) and bool(value.strip())

    @staticmethod
    def _finite_if_number(value: Any) -> bool:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return True
        return math.isfinite(float(value))

    @staticmethod
    def _remaining(stages: list[StageReceipt]) -> tuple[StageReceipt, ...]:
        seen = {stage.stage for stage in stages}
        for stage in SWFUS_STAGE_ORDER:
            if stage not in seen:
                stages.append(StageReceipt(stage, "NOT_REACHED", "prior governance gate stopped progression"))
        return tuple(stages)

    def _finalize(
        self,
        update: ProgressiveUpdate,
        update_digest: str,
        disposition: UpdateDisposition,
        stages: list[StageReceipt],
        *,
        synchronized: bool = False,
        state_record: Any = None,
    ) -> SwfusReceipt:
        state_digest = self._state_digest(state_record)
        return SwfusReceipt(
            schema="kpgs.swfus.receipt.v1",
            receipt_id=self._receipt_id(update_digest, disposition.value, state_digest),
            update_id=update.update_id,
            node_id=update.node_id,
            operation=update.operation_name(),
            disposition=disposition.value,
            stages=self._remaining(stages),
            synchronized=synchronized,
            canonical_authority_changed=False,
            state_digest=state_digest,
            evidence_refs=tuple(update.evidence_refs),
            correlation_id=update.correlation_id,
            boundary_marker=update.boundary_marker,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def execute_update(self, update: ProgressiveUpdate) -> SwfusReceipt:
        """Execute one progressive update through all governed stages.

        Mutating CRUD operations cannot reach STATE_UPDATE until classification,
        routing, protocol selection, invariants and POC/FOC checks have passed.
        Distribution occurs only after a successful state update and is rolled
        back if the injected distribution sink fails.
        """

        digest = self._update_digest(update)
        stages: list[StageReceipt] = []
        operation = update.operation_name()

        # TELEMETRY: establish deterministic update + idempotency identity.
        if not self._valid_text(update.update_id) or not self._valid_text(update.node_id):
            stages.append(StageReceipt("TELEMETRY", "REJECT", "update_id and node_id are required"))
            return self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
        if operation not in {item.value for item in CrudOperation}:
            stages.append(StageReceipt("TELEMETRY", "REJECT", "unsupported CRUD operation"))
            return self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
        if not self._valid_text(update.idempotency_key):
            stages.append(StageReceipt("TELEMETRY", "REJECT", "idempotency_key is required"))
            return self._finalize(update, digest, UpdateDisposition.REJECTED, stages)

        previous = self._idempotency.get(update.idempotency_key)
        if previous:
            previous_digest, previous_receipt = previous
            if previous_digest == digest:
                return replace(previous_receipt, replayed=True)
            stages.append(StageReceipt("TELEMETRY", "REJECT", "idempotency key collision"))
            return self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
        stages.append(StageReceipt("TELEMETRY", "PASS", "update identity accepted"))

        # CLASSIFICATION: lane + state class + APU status.
        if not self._valid_text(update.lane):
            stages.append(StageReceipt("CLASSIFICATION", "REJECT", "lane classification is required"))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        if update.state_class not in ALLOWED_STATE_CLASSES:
            stages.append(StageReceipt("CLASSIFICATION", "REJECT", "authoritative state classes are not admitted"))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        apu_status = update.apu_status.upper().strip()
        if apu_status not in {"GREEN", "YELLOW", "RED", "UNSPECIFIED"}:
            stages.append(StageReceipt("CLASSIFICATION", "REJECT", "invalid APU status"))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        stages.append(StageReceipt("CLASSIFICATION", "PASS", f"lane={update.lane}; apu={apu_status}"))

        # ROUTING: context must be explicit before reads or mutations.
        if not self._valid_text(update.context_route):
            stages.append(StageReceipt("ROUTING", "REJECT", "context_route is required"))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        stages.append(StageReceipt("ROUTING", "PASS", f"route={update.context_route}"))

        # READ is allowed after context routing. Remaining governance stages are
        # explicit no-op receipts; no state mutation or distribution occurs.
        if operation == CrudOperation.READ.value:
            stages.append(StageReceipt("PROTOCOL_SELECTION", "SKIP", "read requires no mutation protocol"))
            stages.append(StageReceipt("INVARIANT_AUDIT", "SKIP", "observation is not mutation"))
            stages.append(StageReceipt("POC_FOC_CHECK", "SKIP", "read cannot promote state"))
            record = self.projection_store.get(update.node_id)
            stages.append(StageReceipt("STATE_UPDATE", "OBSERVE", "projection read only"))
            stages.append(StageReceipt("DISTRIBUTION", "SKIP", "reads are not synchronized mutations"))
            receipt = self._finalize(update, digest, UpdateDisposition.OBSERVED, stages, state_record=record)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt

        # PROTOCOL SELECTION: mutations require an explicit governed protocol.
        if not self._valid_text(update.protocol):
            stages.append(StageReceipt("PROTOCOL_SELECTION", "REJECT", "mutation protocol is required"))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        stages.append(StageReceipt("PROTOCOL_SELECTION", "PASS", f"protocol={update.protocol}"))

        # INVARIANT AUDIT: synchronization cannot widen authority.
        invariant_failures: list[str] = []
        if update.authority_effect != "none":
            invariant_failures.append("authority_effect must remain none")
        if not update.invariant_passed:
            invariant_failures.append("caller-declared invariant audit failed")
        if update.boundary_marker != "#NB":
            invariant_failures.append("#NB boundary marker is required")
        if not self._finite_if_number(update.value):
            invariant_failures.append("numeric value must be finite")
        if update.expected_version is not None and update.expected_version < 0:
            invariant_failures.append("expected_version cannot be negative")
        if invariant_failures:
            stages.append(StageReceipt("INVARIANT_AUDIT", "REJECT", "; ".join(invariant_failures)))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        stages.append(StageReceipt("INVARIANT_AUDIT", "PASS", "authority and update invariants preserved"))

        # POC/FOC CHECK: APU YELLOW holds, RED/FOC rejects, mutation requires proof.
        if apu_status == "RED" or update.foc_detected:
            stages.append(StageReceipt("POC_FOC_CHECK", "REJECT", "FOC/RED update cannot mutate or distribute"))
            receipt = self._finalize(update, digest, UpdateDisposition.REJECTED, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        if apu_status == "YELLOW":
            stages.append(StageReceipt("POC_FOC_CHECK", "HOLD", "APU YELLOW requires review before mutation"))
            receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        if not update.poc_validated or not update.evidence_refs:
            stages.append(StageReceipt("POC_FOC_CHECK", "HOLD", "mutation requires POC validation and evidence refs"))
            receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt
        stages.append(StageReceipt("POC_FOC_CHECK", "PASS", "POC evidence admitted; FOC absent"))

        # STATE UPDATE: mutate only the non-authoritative projection.
        before = self.projection_store.get(update.node_id)
        before_copy = None if before is None else dict(before)
        if update.expected_version is not None:
            current_version = int(before.get("version", 0)) if before else 0
            if current_version != update.expected_version:
                stages.append(StageReceipt("STATE_UPDATE", "HOLD", "expected_version does not match projection"))
                receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages, state_record=before)
                self._idempotency[update.idempotency_key] = (digest, receipt)
                return receipt

        if operation == CrudOperation.CREATE.value:
            if before is not None:
                stages.append(StageReceipt("STATE_UPDATE", "HOLD", "CREATE target already exists"))
                receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages, state_record=before)
                self._idempotency[update.idempotency_key] = (digest, receipt)
                return receipt
            record = {
                "value": update.value,
                "version": 1,
                "state_class": update.state_class,
                "authority_effect": "none",
                "update_id": update.update_id,
            }
            self.projection_store[update.node_id] = record
        elif operation == CrudOperation.UPDATE.value:
            if before is None:
                stages.append(StageReceipt("STATE_UPDATE", "HOLD", "UPDATE target does not exist"))
                receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages)
                self._idempotency[update.idempotency_key] = (digest, receipt)
                return receipt
            record = {
                "value": update.value,
                "version": int(before.get("version", 0)) + 1,
                "state_class": update.state_class,
                "authority_effect": "none",
                "update_id": update.update_id,
            }
            self.projection_store[update.node_id] = record
        else:  # DELETE
            if before is None:
                stages.append(StageReceipt("STATE_UPDATE", "HOLD", "DELETE target does not exist"))
                receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages)
                self._idempotency[update.idempotency_key] = (digest, receipt)
                return receipt
            del self.projection_store[update.node_id]
            record = None
        stages.append(StageReceipt("STATE_UPDATE", "PASS", "bounded non-authoritative projection updated"))

        # DISTRIBUTION: emit alignment evidence only after all gates and state update.
        event = {
            "schema": "kpgs.swfus.distribution.v1",
            "update_id": update.update_id,
            "node_id": update.node_id,
            "operation": operation,
            "state_digest": self._state_digest(record),
            "evidence_refs": list(update.evidence_refs),
            "correlation_id": update.correlation_id,
            "authority_effect": "none",
            "canonical": False,
            "transport_grants_authority": False,
        }
        try:
            if self._distribution_sink is not None:
                self._distribution_sink(event)
            self.distribution_log.append(event)
        except Exception as exc:  # fail closed and restore projection atomically
            if before_copy is None:
                self.projection_store.pop(update.node_id, None)
            else:
                self.projection_store[update.node_id] = before_copy
            stages.append(StageReceipt("DISTRIBUTION", "HOLD", f"distribution failed; projection rolled back: {type(exc).__name__}"))
            receipt = self._finalize(update, digest, UpdateDisposition.HELD, stages, state_record=before_copy)
            self._idempotency[update.idempotency_key] = (digest, receipt)
            return receipt

        stages.append(StageReceipt("DISTRIBUTION", "PASS", "framework alignment event emitted without authority widening"))
        receipt = self._finalize(
            update,
            digest,
            UpdateDisposition.APPLIED,
            stages,
            synchronized=True,
            state_record=record,
        )
        self._idempotency[update.idempotency_key] = (digest, receipt)
        return receipt

    def execute(self, payload: SwfusPayload) -> bool:
        """Legacy boolean adapter routed through canonical vNext gates."""

        value = payload.telemetry_value
        is_foc = payload.is_hallucinated or not self._finite_if_number(value) or value > 100
        operation = CrudOperation.UPDATE if payload.node_id in self.projection_store else CrudOperation.CREATE
        legacy_seed = self._stable_json(
            {
                "node_id": payload.node_id,
                "action_type": payload.action_type,
                "telemetry_value": value,
                "is_hallucinated": payload.is_hallucinated,
            }
        )
        legacy_digest = hashlib.sha256(legacy_seed.encode("utf-8")).hexdigest()
        update = ProgressiveUpdate(
            update_id=f"legacy-{legacy_digest[:16]}",
            node_id=payload.node_id,
            operation=operation,
            lane="legacy.telemetry",
            context_route="kessa.telemetry",
            protocol="SWFUS-vNext/legacy-telemetry-adapter",
            idempotency_key=f"legacy-{legacy_digest}",
            value=value,
            apu_status="RED" if is_foc else "GREEN",
            poc_validated=not is_foc,
            foc_detected=is_foc,
            evidence_refs=(f"legacy-structural-check:sha256:{legacy_digest}",),
            correlation_id=legacy_digest[:24],
            source="legacy-kessa",
        )
        receipt = self.execute_update(update)
        return receipt.disposition == UpdateDisposition.APPLIED.value
