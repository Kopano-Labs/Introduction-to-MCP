"""
Kopano-Phu Governance Systems (KPGS) — 24-RTC Learning Cloud API Router
Exposes REST endpoints for FEP, Reality-to-Cloud, MMAO Identity Mesh, and Possibility-to-Proof engines.

Authority: Master Robyn Kholofelo Rababalela (Seat 1 / Chief Architect)
Facilitator: AntiGravity (Seat 10 / Chief Facilitator)
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import time

from .fep_engine import ForensicEvolutionProtocolEngine, EvidenceClass
from .reality_to_cloud_workflow import RealityToCloudWorkflowOrchestrator, WorkflowStage
from .mmao_mao_identity_mesh import (
    MmaoMaoIdentityRecycler,
    DeviceOperatingMode,
    AiArchitecturePedigree
)
from .possibility_to_proof_engine import (
    PossibilityToProofEngine,
    BracketContainerType,
    EpistemicTruthState
)

router = APIRouter(prefix="/v1/rtc-learning", tags=["24-RTC Learning"])

# Singleton Engine Instances
fep_engine = ForensicEvolutionProtocolEngine()
r2c_orchestrator = RealityToCloudWorkflowOrchestrator()
identity_recycler = MmaoMaoIdentityRecycler()
p2p_engine = PossibilityToProofEngine()


# ============================================================================
# PYDANTIC REQUEST/RESPONSE SCHEMAS
# ============================================================================

class FepReconstructRequest(BaseModel):
    statement: str
    actors: List[str]
    testimony_claim: Optional[str] = None
    artifact_claim: Optional[str] = None
    artifact_file_path: Optional[str] = None


class AcronymDriftRequest(BaseModel):
    human_token: str
    ai_expansion: str


class R2CSessionRequest(BaseModel):
    title: str
    idea_prompt: str


class R2CDeliberationRequest(BaseModel):
    session_id: str
    seat_opinions: Dict[int, str]  # seat_num (1-10) -> opinion_text
    questions: List[str]
    decision_summary: str
    governed_document_path: str


class MmaoRecycleRequest(BaseModel):
    agent_id: str
    proposal_code: str
    disallowed_inventions: List[str]
    verified_exports: List[str]


class P2PConvergeRequest(BaseModel):
    topic_id: str
    candidates: List[str]
    chosen_candidate_id: str
    disk_proof_path: str
    is_verified_on_disk: bool


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/fep/reconstruct", status_code=status.HTTP_200_OK)
def fep_reconstruct(req: FepReconstructRequest):
    """Executes Forensic Evolution Protocol reconstruction across E1-E4 evidence."""
    evidence_ids = []
    
    if req.testimony_claim:
        e1 = fep_engine.ingest_testimony(req.testimony_claim, source_actor="Master Robyn")
        evidence_ids.append(e1.item_id)
        
    if req.artifact_claim and req.artifact_file_path:
        e2 = fep_engine.ingest_artifact(req.artifact_claim, req.artifact_file_path, verified_on_disk=True)
        evidence_ids.append(e2.item_id)
        
    trace = fep_engine.execute_forensic_reconstruction(
        raw_statement=req.statement,
        actors=req.actors,
        evidence_ids=evidence_ids
    )
    
    return {
        "status": "RECONSTRUCTION_COMPLETE",
        "trace_id": trace.trace_id,
        "social_technical_pattern": trace.social_technical_pattern,
        "governance_learning": trace.governance_learning,
        "evidence_count": len(trace.evidence_items)
    }


@router.post("/fep/check-drift", status_code=status.HTTP_200_OK)
def fep_check_drift(req: AcronymDriftRequest):
    """Checks for silent acronym/concept drift between human token and AI expansion."""
    drift_result = fep_engine.detect_acronym_drift(req.human_token, req.ai_expansion)
    return {
        "human_token": req.human_token,
        "ai_expansion": req.ai_expansion,
        "drift_detected": drift_result is not None,
        "message": drift_result or "CANONICAL_MATCH_NO_DRIFT"
    }


@router.post("/r2c/session", status_code=status.HTTP_201_CREATED)
def r2c_initiate_session(req: R2CSessionRequest):
    """Initiates a Reality-to-Cloud discussion session ('Discussion before metal')."""
    session = r2c_orchestrator.initiate_session(req.title, req.idea_prompt)
    return {
        "session_id": session.session_id,
        "title": session.title,
        "stage": session.current_stage.value
    }


@router.post("/r2c/deliberate", status_code=status.HTTP_200_OK)
def r2c_deliberate(req: R2CDeliberationRequest):
    """Records all 10 seat opinions and ratifies a governed decision."""
    for seat_num, opinion_text in req.seat_opinions.items():
        r2c_orchestrator.record_seat_opinion(
            session_id=req.session_id,
            seat_num=int(seat_num),
            opinion_text=opinion_text
        )
        
    try:
        session = r2c_orchestrator.submit_deliberation(
            session_id=req.session_id,
            questions=req.questions,
            decision=req.decision_summary,
            document_path=req.governed_document_path
        )
        authorized = r2c_orchestrator.authorize_execution(req.session_id)
        return {
            "session_id": session.session_id,
            "stage": session.current_stage.value,
            "quorum_seats_satisfied": len(session.opinions),
            "execution_authorized": authorized,
            "decision": session.decision_summary
        }
    except PermissionError as pe:
        raise HTTPException(status_code=400, detail=str(pe))


@router.post("/mmao/recycle", status_code=status.HTTP_200_OK)
def mmao_recycle(req: MmaoRecycleRequest):
    """Evaluates a stateless proposal, captures failure instrumentation, and recycles FOC."""
    # Ensure agent is registered
    if req.agent_id not in identity_recycler.agent_registry:
        identity_recycler.register_agent(
            agent_id=req.agent_id,
            pedigree=AiArchitecturePedigree.CHATBOT_RELATIONAL,
            operating_mode=DeviceOperatingMode.MOBILE_GEMINI_MMAO,
            seat=4
        )
        
    real_api_surface = {
        "disallowed_inventions": req.disallowed_inventions,
        "verified_exports": req.verified_exports
    }
    
    result = identity_recycler.process_stateless_proposal(
        submitting_agent_id=req.agent_id,
        proposal_text=req.proposal_code,
        real_api_surface=real_api_surface
    )
    return result


@router.post("/p2p/converge", status_code=status.HTTP_200_OK)
def p2p_converge(req: P2PConvergeRequest):
    """Executes CDP divergence -> CCP convergence with Cassey BTTH Alchemical receipt."""
    p2p_engine.register_cdp_divergence(req.topic_id, req.candidates)
    
    try:
        receipt = p2p_engine.execute_ccp_convergence(
            topic_id=req.topic_id,
            chosen_candidate_id=req.chosen_candidate_id,
            disk_proof_path=req.disk_proof_path,
            is_verified_on_disk=req.is_verified_on_disk
        )
        return {
            "status": "CONVERGENCE_SUCCESS",
            "receipt_hash": receipt.receipt_hash,
            "action_id": receipt.canonical_action_id,
            "btth_purity_score": receipt.btth_alchemical_score,
            "evidence_location": receipt.proof_evidence_location
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/receipts", status_code=status.HTTP_200_OK)
def list_receipts():
    """Returns all converged receipts and active FEP ledger traces."""
    return {
        "p2p_receipts_count": len(p2p_engine.receipt_ledger),
        "p2p_receipts": [r.__dict__ for r in p2p_engine.receipt_ledger],
        "fep_ledger": fep_engine.export_ledger()
    }
