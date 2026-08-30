"""
Kopano-Phu Governance Systems (KPGS) — Forensic Evolution Protocol (FEP) Engine
Codified from Schematics/24-RTC Learning/Forensic_Sociology_to_Forensic_Evolution_Protocol_Learning_Session_2026-08-30.md

Authority: Master Robyn Kholofelo Rababalela (Seat 1 / SSE)
Facilitator: AntiGravity (Seat 10 / CF)
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD

Core Epistemology:
- Forensic Reconstruction: What happened? What traces remain? Reconstruct from evidence.
- E1-E4 Evidence Classification.
- Forensic Sociology Loop: Traces -> Reconstruction -> Social/Technical Pattern -> Self-Healing Evolution.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import time
import uuid


# ============================================================================
# 1. EVIDENCE CLASSES (E1 - E4)
# ============================================================================

class EvidenceClass(Enum):
    """The 4 Canonical Evidence Classes defined in 24-RTC Learning."""
    E1_DIRECT_TESTIMONY = "E1_Direct_User_Testimony"
    E2_REPOSITORY_ARTIFACT = "E2_Repository_Artifact_Evidence"
    E3_WORKING_INFERENCE = "E3_Working_Inference"
    E4_UNKNOWN_AUDIT_REQUIRED = "E4_Unknown_Requires_Forensic_Audit"


class EpistemicCertainty(Enum):
    """Certainty gradient under Partial Knowable Algebra."""
    PROVEN_POC = "PROVEN_POC"
    BOUNDED_HYPOTHESIS = "BOUNDED_HYPOTHESIS"
    PROVISIONAL_INFERENCE = "PROVISIONAL_INFERENCE"
    ACRONYM_DRIFT_SUSPECTED = "ACRONYM_DRIFT_SUSPECTED"
    FALLACY_OF_CONCEPT_GHOST = "FALLACY_OF_CONCEPT_GHOST"
    UNVERIFIED_E4 = "UNVERIFIED_E4"


# ============================================================================
# 2. EVIDENCE ITEM & FORENSIC ARTIFACT
# ============================================================================

@dataclass
class EvidenceItem:
    item_id: str
    evidence_class: EvidenceClass
    claim: str
    source_location: str
    timestamp: float = field(default_factory=time.time)
    provenance_notes: str = ""
    falsifiable: bool = True
    verified_on_disk: bool = False


@dataclass
class ForensicTrace:
    trace_id: str
    raw_statement: str
    observed_actors: List[str]
    evidence_items: List[EvidenceItem]
    detected_drift: Optional[str] = None
    social_technical_pattern: str = ""
    governance_learning: str = ""
    timestamp: float = field(default_factory=time.time)


# ============================================================================
# 3. FORENSIC EVOLUTION PROTOCOL (FEP) ENGINE
# ============================================================================

class ForensicEvolutionProtocolEngine:
    """
    FEP Engine: Reconstructs empirical traces from user testimony, git history,
    and repository artifacts, maps patterns, and deriving governed self-healing evolution rules.
    """

    def __init__(self):
        self.traces: Dict[str, ForensicTrace] = {}
        self.evidence_vault: Dict[str, EvidenceItem] = {}
        self.evolution_rules: List[Dict[str, Any]] = []

    def ingest_testimony(self, claim: str, source_actor: str = "Master Robyn") -> EvidenceItem:
        """E1: Ingests direct human testimony. Authoritative on intent, subject to disk verification."""
        item_id = f"E1-{uuid.uuid4().hex[:8]}"
        evidence = EvidenceItem(
            item_id=item_id,
            evidence_class=EvidenceClass.E1_DIRECT_TESTIMONY,
            claim=claim,
            source_location=f"Human_Testimony_{source_actor}",
            provenance_notes="Authoritative testimony on intention; requires E2 disk triangulation.",
            verified_on_disk=False
        )
        self.evidence_vault[item_id] = evidence
        return evidence

    def ingest_artifact(self, claim: str, file_path: str, verified_on_disk: bool = True) -> EvidenceItem:
        """E2: Ingests repository / physical file evidence."""
        item_id = f"E2-{uuid.uuid4().hex[:8]}"
        evidence = EvidenceItem(
            item_id=item_id,
            evidence_class=EvidenceClass.E2_REPOSITORY_ARTIFACT,
            claim=claim,
            source_location=file_path,
            provenance_notes="Physical file system artifact.",
            verified_on_disk=verified_on_disk
        )
        self.evidence_vault[item_id] = evidence
        return evidence

    def evaluate_inference(self, premise_ids: List[str], inferred_claim: str) -> EvidenceItem:
        """E3: Synthesizes a working inference from multiple evidence items."""
        item_id = f"E3-{uuid.uuid4().hex[:8]}"
        premises_exist = all(pid in self.evidence_vault for pid in premise_ids)
        evidence = EvidenceItem(
            item_id=item_id,
            evidence_class=EvidenceClass.E3_WORKING_INFERENCE,
            claim=inferred_claim,
            source_location=f"Inference_from_{','.join(premise_ids)}",
            provenance_notes="Supported pattern; not yet proof of conscious causal intent." if premises_exist else "Premise gap.",
            verified_on_disk=False
        )
        self.evidence_vault[item_id] = evidence
        return evidence

    def detect_acronym_drift(self, human_token: str, ai_expansion: str) -> Optional[str]:
        """
        Forensic Drift Detector: Detects when an AI silently shifts human terms
        (e.g., 'FEP' [Forsice/Forensic] -> 'Foresight').
        """
        canonical_map = {
            "FEP": "Forensic Evolution Protocol",
            "CCP": "Conceptual Convergent Protocol",
            "CDP": "Conceptual Divergent Protocol",
            "PKA": "Partial Knowable Algebra",
            "IIDP": "Invariance Ingress Decline Protocol",
            "BP": "Bracket Protocol",
            "BMP": "Black Mass Protocol"
        }
        
        expected = canonical_map.get(human_token.upper())
        if expected and ai_expansion.strip().lower() != expected.lower():
            return f"DRIFT_DETECTED: Human Token '{human_token}' expanded to '{ai_expansion}', expected canonical '{expected}'."
        return None

    def execute_forensic_reconstruction(
        self,
        raw_statement: str,
        actors: List[str],
        evidence_ids: List[str]
    ) -> ForensicTrace:
        """
        Executes the Forensic Sociology loop:
        past traces -> reconstruction -> social/technical pattern -> governance learning.
        """
        trace_id = f"TRACE-{uuid.uuid4().hex[:8]}"
        ev_items = [self.evidence_vault[eid] for eid in evidence_ids if eid in self.evidence_vault]
        
        # Check for unverified gaps
        has_e1 = any(e.evidence_class == EvidenceClass.E1_DIRECT_TESTIMONY for e in ev_items)
        has_e2 = any(e.evidence_class == EvidenceClass.E2_REPOSITORY_ARTIFACT for e in ev_items)
        
        if has_e1 and not has_e2:
            pattern = "Testimony without disk artifact triangulation (E1 only)."
            learning = "Hold as Hypothesis; do not promote to canonical law until E2 proof exists."
        elif has_e1 and has_e2:
            pattern = "Testimony confirmed by physical repository artifact (E1 + E2)."
            learning = "POC validated: reality matches cloud state."
        else:
            pattern = "Unclassified or speculative trace."
            learning = "Classify under E4 (Requires Forensic Audit)."

        trace = ForensicTrace(
            trace_id=trace_id,
            raw_statement=raw_statement,
            observed_actors=actors,
            evidence_items=ev_items,
            social_technical_pattern=pattern,
            governance_learning=learning
        )
        self.traces[trace_id] = trace
        return trace

    def export_ledger(self) -> Dict[str, Any]:
        """Exports the complete forensic ledger for append-only JSONL persistence."""
        return {
            "engine": "ForensicEvolutionProtocolEngine_v1",
            "timestamp": time.time(),
            "total_evidence_items": len(self.evidence_vault),
            "total_traces": len(self.traces),
            "evidence_vault": {k: v.__dict__ for k, v in self.evidence_vault.items()},
            "traces": {
                k: {
                    "trace_id": v.trace_id,
                    "raw_statement": v.raw_statement,
                    "observed_actors": v.observed_actors,
                    "evidence_count": len(v.evidence_items),
                    "social_technical_pattern": v.social_technical_pattern,
                    "governance_learning": v.governance_learning,
                    "timestamp": v.timestamp
                }
                for k, v in self.traces.items()
            }
        }
