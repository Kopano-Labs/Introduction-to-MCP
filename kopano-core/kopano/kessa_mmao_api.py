"""KESSA MMAO API — governed SWFUS execution facade.

KESSA evaluates bounded telemetry through the canonical SWFUS receipt runtime.
Transport state and governance acceptance are reported separately so an offline
or degraded sync path cannot masquerade as a rejected update or a successful
external synchronization.
"""

from __future__ import annotations

from typing import Any, Dict
import logging

from .swfus_engine import SwfusHierarchy, SwfusPayload

log = logging.getLogger("KESSA_MMAO_API")


class KessaMMAOAgent:
    def __init__(self, agent_id: str = "kessa", *, swfus_engine: SwfusHierarchy | None = None):
        self.agent_id = agent_id
        self.swfus_engine = swfus_engine or SwfusHierarchy()
        log.info("KESSA MMAO Agent initialized: %s", self.agent_id)

    def evaluate_telemetry(
        self,
        target_node_id: str,
        raw_telemetry: float,
        hallucinated: bool = False,
    ) -> Dict[str, Any]:
        """Execute legacy telemetry ingestion through SWFUS CRUD progression."""
        payload = SwfusPayload(
            node_id=target_node_id,
            action_type="TELEMETRY_INGESTION",
            telemetry_value=raw_telemetry,
            is_hallucinated=hallucinated,
            data={"telemetry": raw_telemetry},
        )

        receipt = self.swfus_engine.execute_with_receipt(payload)

        if not receipt.accepted:
            verdict = "SEVERED"
            action = "QUARANTINE_AND_REVIEW"
        elif receipt.sync_state == "synced":
            verdict = "SHIP"
            action = "SYNC_PROVEN"
        else:
            verdict = "PENDING_SYNC"
            action = "LOCAL_WITNESS_PRESERVED"

        return {
            "agent_id": self.agent_id,
            "target_node": target_node_id,
            "swfus_verdict": verdict,
            "telemetry_recorded": raw_telemetry if receipt.accepted else None,
            "action": action,
            "receipt": receipt.to_dict(),
        }

    def shotgun_protocol_drill(
        self,
        target_node_id: str,
        execution_telemetry: int,
    ) -> Dict[str, Any]:
        """Classify a bounded diagnostic signal without destructive evidence loss."""
        log.info("Executing Shotgun Protocol on %s", target_node_id)

        if execution_telemetry > 100:
            return {
                "agent_id": self.agent_id,
                "target_node": target_node_id,
                "verdict": "FOC_DETECTED",
                "action": "QUARANTINE_AND_REVIEW",
                "evidence_policy": "preserve prior witnessed state; do not destroy history",
            }

        return {
            "agent_id": self.agent_id,
            "target_node": target_node_id,
            "verdict": "ALIGNED",
            "action": "PROPOSE_PROMOTION",
            "evidence_policy": "promotion still requires external governing gate",
        }


def get_kessa_api() -> KessaMMAOAgent:
    return KessaMMAOAgent()
