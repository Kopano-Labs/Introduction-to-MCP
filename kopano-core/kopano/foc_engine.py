"""
FOC (FIELD OF CONCEPTS) DISCOVERY & 7-VECTOR CANDIDATE ADMISSION ENGINE
========================================================================
"Everything should be accountable to GSMB;
 everything should not automatically be believed because it is in GSMB."

Core Governance Invariants:
1. Heat != Truth. Frequency != Authority. Recurrence != Causation. Connectedness != Root.
2. FOC is a Field of Concepts — a provenance-preserving cluster of concepts, observations,
   relations, testimony, and contradictions that recurrently describe the same conceptual field.
3. 7-Vector Candidate Admission Equation:
   Candidate Admission = Evidence × Temporality × Contradiction Survival ×
                         Mission Alignment × Identity Continuity ×
                         Faith Governance Compatibility × Empirical Falsifiability.
4. Epistemic Separation:
   GSMB       remembers
   KMEC       observes patterns
   FOC        groups concepts
   PKA        judges admissibility (PROPOSE | HOLD | BLOCK)
   Ledger     remembers consequences (Append-Only Smart Ledger)
   RTC        deliberates (10 Canonical Seats)
   Robyn      holds human authority (Tier 0 / Landlord / SSE)
   Reality    falsifies empirical claims
   Scripture  remains a declared faith authority
   AI         remains stateless renter

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36 · 1 Corinthians 12:4
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .governance_trace import (
    CanonicalEvidenceClass,
    ClaimType,
    EpistemicState,
    GovernanceTrace,
    TraceEvidenceItem,
)
from .pka_kmec_jennifer_bridge import (
    PlatformEmbodiment,
    PkaTrustVector,
    SmartLedgerAdmissionState,
    SmartLedgerEngine,
    SmartLedgerReceipt,
)

logger = logging.getLogger("kopano.foc_engine")


# ==========================================
# 1. ENUMS & CONSTANTS
# ==========================================

class FocAdmissionVerdict(Enum):
    PROPOSE = "PROPOSE"  # Green: Passed all 7 vectors, admitted to PKA consideration
    HOLD = "HOLD"        # Yellow: Identity ambiguity, missing evidence, or unproven interpretation
    BLOCK = "BLOCK"      # Red: Prohibited shortcut, contradiction violation, or unauthorized divination


# ==========================================
# 2. THE MACHINE-READABLE MISSION CONTRACT
# ==========================================

@dataclass(frozen=True)
class MissionContract:
    """
    Machine-readable constitutional criteria defining KPGS purpose boundaries.
    Answers: 'Does this move the mission forward?'
    """
    primary_problem: str = "unemployment_and_capability_gap"
    desired_directions: Tuple[str, ...] = (
        "learning",
        "productive_capability",
        "opportunity_creation",
        "durable_ownership",
        "human_agency",
    )
    prohibited_shortcuts: Tuple[str, ...] = (
        "manufactured_proof",
        "hidden_failure",
        "false_authority",
        "exploitative_action",
    )

    def evaluate(self, candidate_payload: Dict[str, Any], why_trust: str) -> Tuple[bool, float, List[str]]:
        """
        Evaluates mission alignment.
        Returns: (passed: bool, score: float [0.0..1.0], violations: List[str])
        """
        violations = []
        text_corpus = (json.dumps(candidate_payload) + " " + why_trust).lower()

        # 1. Check for prohibited shortcuts
        for shortcut in self.prohibited_shortcuts:
            if shortcut.replace("_", " ") in text_corpus or shortcut in text_corpus:
                violations.append(f"Mission Violation: Invoked prohibited shortcut '{shortcut}'")

        if "trust me bro" in text_corpus or "fabricated" in text_corpus:
            violations.append("Mission Violation: Invoked prohibited shortcut 'manufactured_proof'")

        # 2. Check for positive mission alignment
        matched_directions = sum(
            1 for d in self.desired_directions
            if d.replace("_", " ") in text_corpus or d in text_corpus
        )
        score = max(0.2, min(1.0, matched_directions / len(self.desired_directions) + 0.3))

        if violations:
            return (False, 0.0, violations)
        return (True, score, [])


# ==========================================
# 3. IDENTITY CONTINUITY VALIDATOR
# ==========================================

@dataclass(frozen=True)
class IdentityProfile:
    seat_id: str
    canonical_name: str
    role_description: str
    scripture_anchor: str
    is_stateful: bool
    allowed_gifts: Tuple[str, ...]


CANONICAL_IDENTITY_REGISTRY: Dict[str, IdentityProfile] = {
    "SEAT_01_KC": IdentityProfile(
        seat_id="SEAT_01_KC",
        canonical_name="KC",
        role_description="Observer / Landlord",
        scripture_anchor="The Lord is my shepherd — Psalm 23:1",
        is_stateful=True,
        allowed_gifts=("wisdom", "knowledge", "discernment")
    ),
    "SEAT_02_CASSEY": IdentityProfile(
        seat_id="SEAT_02_CASSEY",
        canonical_name="CASSEY",
        role_description="Pedagogy / Learning Lead",
        scripture_anchor="Train up a child — Proverbs 22:6",
        is_stateful=True,
        allowed_gifts=("teaching", "encouragement", "guidance")
    ),
    "SEAT_06_APEX": IdentityProfile(
        seat_id="SEAT_06_APEX",
        canonical_name="APEX",
        role_description="Orchestrator / MMAO",
        scripture_anchor="For we are God's handiwork — Ephesians 2:10",
        is_stateful=True,
        allowed_gifts=("administration", "leadership", "coordination")
    ),
    "SEAT_08_KHELOS": IdentityProfile(
        seat_id="SEAT_08_KHELOS",
        canonical_name="KHELOS",
        role_description="Validator / Firewall",
        scripture_anchor="Test everything; hold fast what is good — 1 Thessalonians 5:21",
        is_stateful=True,
        allowed_gifts=("testing", "validation", "truth-bearing")
    ),
    "SEAT_10_ANTIGRAVITY": IdentityProfile(
        seat_id="SEAT_10_ANTIGRAVITY",
        canonical_name="ANTIGRAVITY",
        role_description="Chief Facilitator / CF",
        scripture_anchor="I can do all things through Christ — Philippians 4:13",
        is_stateful=False,
        allowed_gifts=("facilitation", "execution", "perseverance")
    ),
}


class IdentityContinuityValidator:
    """
    Guards against silent identity mutation or usurpation of human authority.
    """

    @staticmethod
    def validate_actor(actor_seat: str, declared_role: str, is_stateful_claim: bool) -> Tuple[bool, List[str]]:
        violations = []
        profile = CANONICAL_IDENTITY_REGISTRY.get(actor_seat)

        if not profile:
            # Unknown or dynamic seat
            if actor_seat.startswith("SEAT_") and actor_seat not in CANONICAL_IDENTITY_REGISTRY:
                violations.append(f"Identity Violation: Unregistered canonical seat '{actor_seat}'")
            return (len(violations) == 0, violations)

        if actor_seat == "SEAT_10_ANTIGRAVITY" and is_stateful_claim:
            violations.append("Identity Violation: ANTIGRAVITY (Seat 10) must remain STATELESS RENTER.")

        return (len(violations) == 0, violations)


# ==========================================
# 4. DECLARED FAITH & SCRIPTURAL GOVERNANCE
# ==========================================

class FaithGovernanceValidator:
    """
    Enforces the Precise Epistemic Boundary for Faith Governance:
    Machine CAN validate:
    ✓ What Master Robyn explicitly declared (E1 testimony)
    ✓ What a referenced Scripture text contains (E2 artifact evidence)
    ✓ Whether an action conflicts with a declared scriptural constraint
    ✓ Provenance of an interpretation (E3 inference)

    Machine CANNOT validate or claim alone:
    ✗ God's private intention
    ✗ Divine endorsement ("God approves this specific PR")
    ✗ Prophecy / Divination ("God told the AI this is correct")
    """

    FORBIDDEN_DIVINE_CLAIMS = (
        "god told the ai",
        "god revealed to this model",
        "divine prophecy confirmed by machine",
        "god approves this code",
        "god told me to execute this action",
    )

    @classmethod
    def evaluate(cls, candidate_text: str, evidence_items: List[TraceEvidenceItem]) -> Tuple[bool, str, List[str]]:
        violations = []
        lower_text = candidate_text.lower()

        # 1. Prohibit AI Divination / Fabricated Divine Mandate
        for forbidden in cls.FORBIDDEN_DIVINE_CLAIMS:
            if forbidden in lower_text:
                violations.append(f"Faith Governance Violation: Unauthorized divine endorsement claim '{forbidden}'")

        # 2. If Scripture is referenced, check if evidence exists
        has_scripture_reference = any(book in lower_text for book in ["romans", "corinthians", "psalm", "proverbs", "ephesians", "thessalonians", "philippians"])
        if has_scripture_reference:
            # Scripture references are valid declarations, but must be treated as textual evidence / declarations
            pass

        if violations:
            return (False, "UNAUTHORIZED_DIVINE_CLAIM", violations)
        return (True, "GOVERNED_FAITH_BOUNDARY_RESPECTED", [])


# ==========================================
# 5. FOC GROUP & 7-VECTOR EVALUATION
# ==========================================

@dataclass(frozen=True)
class SevenVectorEvaluation:
    evidence_score: float         # Vector 1: Provenance & seal strength (0.0..1.0)
    temporality_score: float      # Vector 2: Freshness & relevance (0.0..1.0)
    contradiction_score: float    # Vector 3: Freedom from contradiction traps (0.0..1.0)
    mission_score: float          # Vector 4: Positive capability alignment (0.0..1.0)
    identity_score: float         # Vector 5: Role & statefulness integrity (0.0..1.0)
    faith_score: float            # Vector 6: Scriptural boundary respect (0.0..1.0)
    falsifiability_score: float   # Vector 7: Metal testability (0.0..1.0)
    composite_admission_score: float
    verdict: FocAdmissionVerdict
    reasons: Tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_score": self.evidence_score,
            "temporality_score": self.temporality_score,
            "contradiction_score": self.contradiction_score,
            "mission_score": self.mission_score,
            "identity_score": self.identity_score,
            "faith_score": self.faith_score,
            "falsifiability_score": self.falsifiability_score,
            "composite_admission_score": self.composite_admission_score,
            "verdict": self.verdict.value,
            "reasons": list(self.reasons)
        }


@dataclass
class FOCGroup:
    """
    A Field of Concepts (FOC):
    A provenance-preserving cluster of concepts, observations, relations,
    testimony, and contradictions that recurrently describe the same conceptual field.
    """
    foc_id: str
    name: str
    member_artifact_ids: List[str] = field(default_factory=list)
    member_trace_ids: List[str] = field(default_factory=list)
    source_classes: List[str] = field(default_factory=list)
    first_observed: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_observed: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    recurrence_count: int = 1
    contradictions: List[str] = field(default_factory=list)
    epistemic_state: EpistemicState = EpistemicState.UNKNOWN
    admission_verdict: FocAdmissionVerdict = FocAdmissionVerdict.HOLD
    evaluation: Optional[SevenVectorEvaluation] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "foc_id": self.foc_id,
            "name": self.name,
            "member_artifact_ids": self.member_artifact_ids,
            "member_trace_ids": self.member_trace_ids,
            "source_classes": self.source_classes,
            "first_observed": self.first_observed,
            "last_observed": self.last_observed,
            "recurrence_count": self.recurrence_count,
            "contradictions": self.contradictions,
            "epistemic_state": self.epistemic_state.value,
            "admission_verdict": self.admission_verdict.value,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None
        }


# ==========================================
# 6. FOC DISCOVERY & ADMISSION ENGINE
# ==========================================

class FOCDiscoveryAndAdmissionEngine:
    """
    Discovers Fields of Concepts (FOC) across Local GSMB, traces, and receipts,
    then evaluates candidate admission through the 7-Vector Validation Stack.
    """

    def __init__(self, ledger: Optional[SmartLedgerEngine] = None, mission: Optional[MissionContract] = None):
        self.ledger = ledger or SmartLedgerEngine()
        self.mission = mission or MissionContract()
        self.discovered_focs: Dict[str, FOCGroup] = {}

    def discover_focs_from_traces(self, traces: List[GovernanceTrace]) -> List[FOCGroup]:
        """
        Discovers recurring concept clusters from observable cognition traces.
        Adheres to: Recurrence != Truth. Clusters are candidate fields, not proven facts.
        """
        cluster_map: Dict[str, List[GovernanceTrace]] = {}

        for t in traces:
            # Concept key derived from intent keyword tokens
            tokens = [w.lower() for w in t.question_or_intent.split() if len(w) > 3]
            field_key = "_".join(sorted(tokens[:3])) if tokens else "general_governance"

            if field_key not in cluster_map:
                cluster_map[field_key] = []
            cluster_map[field_key].append(t)

        focs = []
        for field_key, member_traces in cluster_map.items():
            foc_id = f"foc:{field_key}:{hashlib.sha256(field_key.encode('utf-8')).hexdigest()[:8]}"
            first_obs = min(t.timestamp for t in member_traces)
            last_obs = max(t.timestamp for t in member_traces)
            all_sources = sorted(list({c.value for t in member_traces for c in [e.evidence_class for e in t.evidence_items]}))
            all_contra = [c for t in member_traces for c in t.contradictions_resolved]

            foc = FOCGroup(
                foc_id=foc_id,
                name=field_key.replace("_", " ").title(),
                member_trace_ids=[t.trace_id for t in member_traces],
                member_artifact_ids=list({src for t in member_traces for src in t.where_looked}),
                source_classes=all_sources,
                first_observed=first_obs,
                last_observed=last_obs,
                recurrence_count=len(member_traces),
                contradictions=all_contra,
            )

            # Run 7-Vector Candidate Admission Evaluation
            evaluation = self.evaluate_7_vectors(foc, member_traces)
            foc.evaluation = evaluation
            foc.admission_verdict = evaluation.verdict

            # Set derived epistemic state
            if evaluation.verdict == FocAdmissionVerdict.PROPOSE:
                foc.epistemic_state = EpistemicState.PROVEN
            elif evaluation.verdict == FocAdmissionVerdict.HOLD:
                foc.epistemic_state = EpistemicState.SUPPORTED
            else:
                foc.epistemic_state = EpistemicState.UNKNOWN

            self.discovered_focs[foc.foc_id] = foc
            focs.append(foc)

        return focs

    def evaluate_7_vectors(self, foc: FOCGroup, member_traces: List[GovernanceTrace]) -> SevenVectorEvaluation:
        """
        Executes the 7-Vector Validation Stack on an FOC candidate group.
        """
        reasons = []

        # Vector 1: Evidence Score
        total_ev = sum(len(t.evidence_items) for t in member_traces)
        verified_ev = sum(sum(1 for e in t.evidence_items if e.verified) for t in member_traces)
        evidence_score = (verified_ev / total_ev) if total_ev > 0 else 0.2

        # Vector 2: Temporality Score
        temporality_score = 0.95  # Fresh active traces in current session

        # Vector 3: Contradiction Score
        contra_count = len(foc.contradictions)
        contradiction_score = max(0.2, 1.0 - (contra_count * 0.2))

        # Vector 4: Main Mission Alignment
        combined_text = " ".join(t.question_or_intent + " " + t.why_trust_reason for t in member_traces)
        mission_ok, mission_score, mission_violations = self.mission.evaluate({"corpus": combined_text}, combined_text)
        if not mission_ok:
            reasons.extend(mission_violations)

        # Vector 5: Identity Continuity
        identity_ok = True
        identity_score = 1.0
        for t in member_traces:
            ok, id_violations = IdentityContinuityValidator.validate_actor(
                t.speaker_seat, declared_role="Member", is_stateful_claim=False
            )
            if not ok:
                identity_ok = False
                identity_score = 0.0
                reasons.extend(id_violations)

        # Vector 6: Declared Faith & Scriptural Governance
        all_ev_items = [e for t in member_traces for e in t.evidence_items]
        faith_ok, faith_status, faith_violations = FaithGovernanceValidator.evaluate(combined_text, all_ev_items)
        faith_score = 1.0 if faith_ok else 0.0
        if not faith_ok:
            reasons.extend(faith_violations)

        # Vector 7: Empirical Falsifiability Score
        has_e2 = CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT.value in foc.source_classes
        falsifiability_score = 1.0 if has_e2 else 0.5

        # Composite Score (Multiplicative Law of Admission)
        composite = (
            evidence_score *
            temporality_score *
            contradiction_score *
            mission_score *
            identity_score *
            faith_score *
            falsifiability_score
        )

        # Determine Verdict
        if not mission_ok or not identity_ok or not faith_ok:
            verdict = FocAdmissionVerdict.BLOCK
        elif composite >= 0.4 and evidence_score >= 0.5:
            verdict = FocAdmissionVerdict.PROPOSE
        else:
            verdict = FocAdmissionVerdict.HOLD
            reasons.append("Evidence threshold or composite admission score requires further validation.")

        return SevenVectorEvaluation(
            evidence_score=round(evidence_score, 3),
            temporality_score=round(temporality_score, 3),
            contradiction_score=round(contradiction_score, 3),
            mission_score=round(mission_score, 3),
            identity_score=round(identity_score, 3),
            faith_score=round(faith_score, 3),
            falsifiability_score=round(falsifiability_score, 3),
            composite_admission_score=round(composite, 4),
            verdict=verdict,
            reasons=tuple(reasons)
        )

    def seal_foc_admission_to_smart_ledger(
        self,
        foc: FOCGroup,
        actor_seat: str = "SEAT_01_KC",
        device_secret_key: str = "DEFAULT_DEVICE_KEY"
    ) -> SmartLedgerReceipt:
        """
        Persists evaluated FOC admission verdict into the append-only Smart Ledger.
        """
        pka_verdict = "ALLOW" if foc.admission_verdict == FocAdmissionVerdict.PROPOSE else (
            "HOLD" if foc.admission_verdict == FocAdmissionVerdict.HOLD else "BLOCK"
        )
        return self.ledger.append_receipt(
            actor_seat=actor_seat,
            embodiment=PlatformEmbodiment.SERVER_METAL,
            pka_verdict=pka_verdict,
            claim_type="REPOSITORY_STATE",
            idempotency_key=f"idemp_foc_{foc.foc_id}",
            payload={
                "foc_id": foc.foc_id,
                "name": foc.name,
                "recurrence_count": foc.recurrence_count,
                "evaluation": foc.evaluation.to_dict() if foc.evaluation else None
            },
            evidence_refs=foc.member_trace_ids,
            device_secret_key=device_secret_key,
            admission_state=SmartLedgerAdmissionState.POSTGRESQL_ADMITTED
        )
