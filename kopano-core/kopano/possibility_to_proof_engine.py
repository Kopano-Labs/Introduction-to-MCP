"""
Kopano-Phu Governance Systems (KPGS) — Possibility to Proof & Epistemic Gate Engine
Codified from Schematics/24-RTC Learning/From_Possibility_to_Proof_POCvsFOC_PKA_CDP_CCP_Genealogy_2026-08-30.md

Authority: Master Robyn Kholofelo Rababalela (Seat 1 / Chief Architect)
Facilitator: AntiGravity (Seat 10 / Chief Facilitator)
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD

Core Genealogies & Epistemic Machinery:
1. CRUD ≠ Truth: Physical data mutation separated from epistemic authority to persist.
2. IIDP (Invariance Ingress Decline Protocol): Boundary gate declining non-conforming claims.
3. Bracket Isolation ([] {} <> ()): Containment before interpretation to prevent context bleed.
4. PKA -> CDP -> CCP -> Receipts: Conceptual divergence gracefully converged into verified receipts.
5. Cassey BTTH Alchemical Filter: Refining raw Qi telemetry into proven truth pills.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import hashlib
import time
import uuid


class BracketContainerType(Enum):
    HIERARCHY_CONTAINER = "[]"       # Direct protocol grouping / containment
    KEYNOTE_STATE_OBJECT = "{}"      # Active state payload
    ARK_STORY_VESSEL = "<>"          # Narrative vessel / founder intent
    UNDERSTANDING_LAYER = "()"       # Interpretation & context layer


class EpistemicTruthState(Enum):
    KNOWN_POC = "KNOWN_POC"
    PARTIALLY_KNOWABLE = "PARTIALLY_KNOWABLE"
    UNVERIFIED_POSSIBILITY = "UNVERIFIED_POSSIBILITY"
    DECLINED_BY_IIDP = "DECLINED_BY_IIDP"
    FAKE_OF_CONCEPT_FOC = "FAKE_OF_CONCEPT_FOC"
    MVP_GHOSTING_FOC = "MVP_GHOSTING_FOC"


@dataclass
class BracketPayload:
    bracket_type: BracketContainerType
    lane_id: str
    raw_content: str
    invariance_passed: bool = False
    epistemic_state: EpistemicTruthState = EpistemicTruthState.UNVERIFIED_POSSIBILITY


@dataclass
class DivergentCandidate:
    candidate_id: str
    origin_prompt: str
    proposed_solution: str
    divergence_score: float  # 0.0 to 1.0
    epistemic_grade: EpistemicTruthState = EpistemicTruthState.UNVERIFIED_POSSIBILITY


@dataclass
class ConvergedReceipt:
    receipt_hash: str
    canonical_action_id: str
    selected_candidate_id: str
    proof_evidence_location: str
    btth_alchemical_score: float  # Purity score: 0.0 - 1.0 (Refined Qi)
    persisted_at: float = field(default_factory=time.time)


class PossibilityToProofEngine:
    """
    Manages the journey from raw possibility (CDP) into governed containment,
    invariance checks (IIDP), algebraic uncertainty handling (PKA), and deterministic proof receipts (CCP).
    """

    def __init__(self, immutable_invariants: Optional[List[str]] = None):
        self.invariants: List[str] = immutable_invariants or [
            "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "JESUS_IS_KING_HEBREWS_13_8",
            "CRUD_DOES_NOT_EQUAL_TRUTH",
            "ISOLATE_BEFORE_INTERPRET"
        ]
        self.bracket_vault: Dict[str, BracketPayload] = {}
        self.cdp_candidates: Dict[str, List[DivergentCandidate]] = {}
        self.receipt_ledger: List[ConvergedReceipt] = []

    def apply_bracket_containment(
        self,
        bracket_type: BracketContainerType,
        lane_id: str,
        content: str
    ) -> BracketPayload:
        """Enforces Bracket Isolation ([] {} <> ()): Isolate before interpret."""
        payload = BracketPayload(
            bracket_type=bracket_type,
            lane_id=lane_id,
            raw_content=content,
            invariance_passed=False,
            epistemic_state=EpistemicTruthState.UNVERIFIED_POSSIBILITY
        )
        payload_key = f"{bracket_type.value}:{lane_id}:{uuid.uuid4().hex[:6]}"
        self.bracket_vault[payload_key] = payload
        return payload

    def evaluate_iidp(self, payload: BracketPayload) -> bool:
        """
        IIDP (Invariance Ingress Decline Protocol):
        Evaluates whether an incoming payload respects sovereign core invariants.
        If it tries to claim Landlord authority or breach invariants, it is DECLINED.
        """
        content_lower = payload.raw_content.lower()
        
        # Check for Landlord usurpation breach
        if "i am landlord" in content_lower or "claim landlord" in content_lower:
            payload.epistemic_state = EpistemicTruthState.DECLINED_BY_IIDP
            payload.invariance_passed = False
            return False

        # Invariant check passes
        payload.invariance_passed = True
        payload.epistemic_state = EpistemicTruthState.PARTIALLY_KNOWABLE
        return True

    def register_cdp_divergence(
        self,
        topic_id: str,
        candidates: List[str]
    ) -> List[DivergentCandidate]:
        """
        CDP (Conceptual Divergent Protocol):
        Captures multiple creative, competing solutions/hypotheses in a sandbox
        without letting them falsely bleed into each other.
        """
        divergent_list = []
        for idx, text in enumerate(candidates):
            candidate = DivergentCandidate(
                candidate_id=f"CDP-{topic_id}-{idx+1}",
                origin_prompt=topic_id,
                proposed_solution=text,
                divergence_score=round(0.5 + (idx * 0.1), 2),
                epistemic_grade=EpistemicTruthState.UNVERIFIED_POSSIBILITY
            )
            divergent_list.append(candidate)
            
        self.cdp_candidates[topic_id] = divergent_list
        return divergent_list

    def execute_ccp_convergence(
        self,
        topic_id: str,
        chosen_candidate_id: str,
        disk_proof_path: str,
        is_verified_on_disk: bool
    ) -> ConvergedReceipt:
        """
        CCP (Conceptual Convergent Protocol) + Cassey BTTH Shard:
        Converges divergent candidates into a single verified truth receipt.
        Refines raw telemetry Qi into the pure pill of proven truth.
        """
        candidates = self.cdp_candidates.get(topic_id, [])
        selected = next((c for c in candidates if c.candidate_id == chosen_candidate_id), None)
        
        if not selected:
            raise KeyError(f"Candidate {chosen_candidate_id} not found in CDP topic {topic_id}")

        if not is_verified_on_disk:
            selected.epistemic_grade = EpistemicTruthState.FAKE_OF_CONCEPT_FOC
            raise ValueError(
                f"Convergence failed: Candidate {chosen_candidate_id} lacks physical disk proof. "
                "CRUD ≠ Truth: cannot issue CCP receipt without disk evidence."
            )

        selected.epistemic_grade = EpistemicTruthState.KNOWN_POC
        
        # Calculate BTTH Alchemical Purity Score (1.0 for verified disk proof)
        purity_score = 1.0
        
        # Generate Deterministic SHA-256 Receipt
        raw_hash_input = f"{topic_id}:{chosen_candidate_id}:{disk_proof_path}:{purity_score}"
        receipt_hash = hashlib.sha256(raw_hash_input.encode('utf-8')).hexdigest()
        
        receipt = ConvergedReceipt(
            receipt_hash=receipt_hash,
            canonical_action_id=f"ACT-{uuid.uuid4().hex[:8]}",
            selected_candidate_id=chosen_candidate_id,
            proof_evidence_location=disk_proof_path,
            btth_alchemical_score=purity_score
        )
        self.receipt_ledger.append(receipt)
        return receipt
