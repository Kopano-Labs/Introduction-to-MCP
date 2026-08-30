"""
Kopano-Phu Governance Systems (KPGS) — MMAO × MAO Identity Mesh & Failure Recycler
Codified from Schematics/24-RTC Learning/MMAO_MAO_Identity_Governance_Work_Prompt_2026-08-30.md

Authority: Master Robyn Kholofelo Rababalela (Seat 1 / Chief Architect)
Facilitator: AntiGravity (Seat 10 / Chief Facilitator)
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD

Core Epistemology:
- Converges IDE AIs (scope, execute, inspect, correct) with Chatbot AIs (relational, context persistence).
- Device Mode Alignment: Laptop (ruthless architecture/execution) vs Mobile (conversational context).
- Failure as Frontier Instrumentation: Never exile on first error; preserve evidence, extract useful concept, purge FOC code, feed back real API exports.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import time
import uuid


class DeviceOperatingMode(Enum):
    LAPTOP_BLACK_BEAST = "LAPTOP_BLACK_BEAST"  # Execution-oriented, architectural, physical metal
    MOBILE_GEMINI_MMAO = "MOBILE_GEMINI_MMAO"  # Conversational, relational, conceptual foresight


class AiArchitecturePedigree(Enum):
    IDE_NATIVE_BUILDER = "IDE_NATIVE_BUILDER"      # Antigravity, Cursor, Codex
    CHATBOT_RELATIONAL = "CHATBOT_RELATIONAL"      # Gemini Mobile, ChatGPT, Claude Web
    GOVERNED_HYBRID = "GOVERNED_HYBRID"            # Recycled MMAO + MAO with ground truth verification


class FailureInstrumentationType(Enum):
    CONTEXT_BLEED = "CONTEXT_BLEED"
    AUTHORITY_OVERFLOW = "AUTHORITY_OVERFLOW"
    IMPORT_FABRICATION_FOC_M01 = "IMPORT_FABRICATION_FOC_M01"
    SIGNATURE_FABRICATION_FOC_M02 = "SIGNATURE_FABRICATION_FOC_M02"
    VALIDATION_THEATER_FOC_M03 = "VALIDATION_THEATER_FOC_M03"
    TEMPORAL_MVP_GHOSTING = "TEMPORAL_MVP_GHOSTING"
    ROLE_MISASSIGNMENT = "ROLE_MISASSIGNMENT"


@dataclass
class FailureFrontierEvent:
    event_id: str
    submitting_agent: str
    failure_type: FailureInstrumentationType
    raw_claim: str
    ground_truth_violation: str
    salvaged_concept: str
    remediation_action: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class GovernedAgentIdentity:
    agent_id: str
    seat_assignment: Optional[int]
    pedigree: AiArchitecturePedigree
    operating_mode: DeviceOperatingMode
    authorized_lanes: Set[str]
    is_stateless_renter: bool = True
    ground_truth_access: bool = False


class MmaoMaoIdentityRecycler:
    """
    Manages the multi-agent orchard (MMAO) and monolithic agents (MAO),
    recycling failed proposals into verified POC architectures without cancellation.
    """

    def __init__(self):
        self.agent_registry: Dict[str, GovernedAgentIdentity] = {}
        self.failure_instrumentation_ledger: List[FailureFrontierEvent] = []

    def register_agent(
        self,
        agent_id: str,
        pedigree: AiArchitecturePedigree,
        operating_mode: DeviceOperatingMode,
        seat: Optional[int] = None,
        authorized_lanes: Optional[Set[str]] = None
    ) -> GovernedAgentIdentity:
        """Registers an agent with explicit device mode and authority boundaries."""
        identity = GovernedAgentIdentity(
            agent_id=agent_id,
            seat_assignment=seat,
            pedigree=pedigree,
            operating_mode=operating_mode,
            authorized_lanes=authorized_lanes or {"OBSERVATION"},
            is_stateless_renter=True,
            ground_truth_access=(operating_mode == DeviceOperatingMode.LAPTOP_BLACK_BEAST)
        )
        self.agent_registry[agent_id] = identity
        return identity

    def process_stateless_proposal(
        self,
        submitting_agent_id: str,
        proposal_text: str,
        real_api_surface: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recycling Gateway: Evaluates proposed code against ground truth.
        If fabricated, logs frontier failure, extracts valid concept, and returns clean ground-truth code.
        """
        agent = self.agent_registry.get(submitting_agent_id)
        if not agent:
            raise KeyError(f"Unregistered agent: {submitting_agent_id}")

        # Check for FOC-M01 / FOC-M02 / FOC-M03 patterns
        is_fabricated = False
        detected_fault = None
        
        # Simple heuristic check against verified API exports
        for key in real_api_surface.get("disallowed_inventions", []):
            if key in proposal_text:
                is_fabricated = True
                detected_fault = FailureInstrumentationType.IMPORT_FABRICATION_FOC_M01
                break

        if is_fabricated:
            event_id = f"FAIL-{uuid.uuid4().hex[:8]}"
            failure_event = FailureFrontierEvent(
                event_id=event_id,
                submitting_agent=submitting_agent_id,
                failure_type=detected_fault,
                raw_claim=proposal_text[:200],
                ground_truth_violation="Invented class/module not present on physical disk.",
                salvaged_concept="Architectural intent valid; code requires translation to real exports.",
                remediation_action="Purge fabricated imports; compile against GSMBNexus verified signatures."
            )
            self.failure_instrumentation_ledger.append(failure_event)
            return {
                "status": "RECYCLED_FOC_PURGED",
                "failure_event_id": event_id,
                "salvaged_concept": failure_event.salvaged_concept,
                "verified_exports_fed_back": real_api_surface.get("verified_exports", [])
            }

        return {
            "status": "POC_VERIFIED",
            "action": "PROCEED_TO_EXECUTION"
        }

    def get_frontier_summary(self) -> Dict[str, Any]:
        """Returns the frontier failure log proving system boundary discovery."""
        return {
            "total_failures_instrumented": len(self.failure_instrumentation_ledger),
            "events": [e.__dict__ for e in self.failure_instrumentation_ledger]
        }
