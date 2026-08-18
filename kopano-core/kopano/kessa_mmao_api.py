"""KESSA MMAO API.

KESSA remains an orchestration caller. SWFUS owns governed update ordering and
returns evidence receipts; KESSA does not gain canonical state authority and no
transport/provider is implied by a successful synchronization receipt.
"""

from __future__ import annotations

from typing import Any, Dict
import hashlib
import json
import logging

from .swfus_engine import (
    CrudOperation,
    ProgressiveUpdate,
    SwfusHierarchy,
    UpdateDisposition,
)

log = logging.getLogger("KESSA_MMAO_API")


class KessaMMAOAgent:
    def __init__(self, agent_id: str = "kessa", swfus_engine: SwfusHierarchy | None = None):
        self.agent_id = agent_id
        self.swfus_engine = swfus_engine or SwfusHierarchy()
        log.info("KESSA MMAO Agent initialized: %s", self.agent_id)

    def evaluate_telemetry(
        self,
        target_node_id: str,
        raw_telemetry: float,
        hallucinated: bool = False,
    ) -> Dict[str, Any]:
        """Evaluate bounded telemetry through APU -> CRUD -> SWFUS.

        The legacy public method is preserved, but the result now exposes the
        canonical SWFUS receipt instead of pretending success means an Azure
        write occurred.
        """

        exists = target_node_id in self.swfus_engine.projection_store
        operation = CrudOperation.UPDATE if exists else CrudOperation.CREATE
        canonical_seed = json.dumps(
            {
                "target_node_id": target_node_id,
                "raw_telemetry": raw_telemetry,
                "hallucinated": hallucinated,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical_seed.encode("utf-8")).hexdigest()
        is_foc = hallucinated or raw_telemetry > 100

        update = ProgressiveUpdate(
            update_id=f"kessa-{digest[:16]}",
            node_id=target_node_id,
            operation=operation,
            lane="mmao.telemetry",
            context_route="kessa.telemetry",
            protocol="APU->CRUD->SWFUS",
            idempotency_key=f"kessa-{digest}",
            value=raw_telemetry,
            apu_status="RED" if is_foc else "GREEN",
            poc_validated=not is_foc,
            foc_detected=is_foc,
            evidence_refs=(f"kessa-telemetry-check:sha256:{digest}",),
            correlation_id=digest[:24],
            source="kessa-mmao",
            boundary_marker="#NB",
        )
        receipt = self.swfus_engine.execute_update(update)
        shipped = receipt.disposition == UpdateDisposition.APPLIED.value

        return {
            "agent_id": self.agent_id,
            "target_node": target_node_id,
            "swfus_verdict": "SHIP" if shipped else receipt.disposition,
            "telemetry_recorded": raw_telemetry,
            "action": "DISTRIBUTE_FRAMEWORK_STATE" if receipt.synchronized else "NO_DISTRIBUTION",
            "receipt_id": receipt.receipt_id,
            "disposition": receipt.disposition,
            "synchronized": receipt.synchronized,
            "canonical_authority_changed": receipt.canonical_authority_changed,
            "stage_order": [stage.stage for stage in receipt.stages],
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

    def shotgun_protocol_drill(
        self,
        target_node_id: str,
        execution_telemetry: int,
    ) -> Dict[str, Any]:
        """Legacy sandbox drill; it does not mutate canonical state."""

        log.info("Executing Shotgun Protocol on %s", target_node_id)
        if execution_telemetry > 100:
            return {
                "agent_id": self.agent_id,
                "target_node": target_node_id,
                "verdict": "FOC_DETECTED",
                "action": "HOLD_AND_SEVER_NON_AUTHORITATIVE_PROJECTION",
                "canonical_authority_changed": False,
            }

        return {
            "agent_id": self.agent_id,
            "target_node": target_node_id,
            "verdict": "ALIGNED",
            "action": "PROPOSE_FOR_GOVERNED_UPDATE",
            "canonical_authority_changed": False,
        }


def get_kessa_api() -> KessaMMAOAgent:
    return KessaMMAOAgent()
