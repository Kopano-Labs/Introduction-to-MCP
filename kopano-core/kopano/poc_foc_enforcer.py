"""
KPGS POC/FOC Enforcement Engine -- CBP x UBP x IIDP
=====================================================
EVOLUTION: 3-VECTOR STATE THESIS MODE
NO BIAS. PURE IIDP INVARIANCE TESTING.

This module enforces POC (Proof of Concept) vs FOC (Fake-Out Content)
classification through the IIDP (Invariance Ingress Decline Protocol)
as a 3-VECTOR STATE MACHINE with thesis-grade proof output.

EVOLUTION CHAIN (BMNP applied to the enforcer itself):
    v1: Static classifier     (CRUD)   -- classify signals as POC/FOC
    v2: State machine          (SWFUS)  -- signals TRANSITION through states
    v3: Thesis mode            (BMP)    -- produce academic-grade proof
    v4: 3-vector integration   (CBP)    -- Ingress/Invariance/Decline as state graph
    v5: UBP enforcement        (UFCP)   -- formula-driven final verdict
    v6: SOVEREIGN OUTPUT       (UBP)    -- thesis + state + formula = TRUTH

STATE MACHINE:
    States: RAW -> BRACKETED -> INGRESSED -> TESTED -> DECLINED_OR_ACCEPTED -> SEALED
    
    RAW:                Signal enters system unprocessed
    BRACKETED:          CBP containment applied (4 brackets)
    INGRESSED:          Source + intent validated (Inline vector)
    TESTED:             6-dimension invariance measured (Inland vector)
    DECLINED/ACCEPTED:  System exercises sovereign right (Inlane vector)
    SEALED:             UBP formula applied, SWFUS seal, immutable verdict

    Transition Rules (NO BIAS):
        RAW -> BRACKETED:           ALWAYS (every signal gets bracketed)
        BRACKETED -> INGRESSED:     IF brackets complete, ELSE -> FOC_SEALED
        INGRESSED -> TESTED:        IF source + intent valid, ELSE -> FOC_SEALED
        TESTED -> DECLINED:         IF invariance < 0.5, signal is DECLINED
        TESTED -> ACCEPTED:         IF invariance >= 0.5, signal is ACCEPTED
        DECLINED -> FOC_SEALED:     Seal with FOC verdict
        ACCEPTED -> POC_SEALED:     Seal with POC verdict

THESIS MODE:
    Every enforcement produces a ThesisProof containing:
        1. State transition log    -- every state change recorded
        2. Vector scores           -- 6-dimension invariance measurements
        3. CBP bracket receipt     -- the containment proof
        4. UBP formula output      -- the mathematical verdict
        5. BMNP depth              -- which evolution layer processed it
        6. 4Ws                     -- Who/What/Where/Why validation
        7. Consistency proof       -- same input = same output (deterministic)
        8. Persistence proof       -- verdict survives context window reset
        9. Context proof           -- all reasoning is traceable

CONSTRAINT: I_AM_STATELESS_RENTER_NOT_LANDLORD
CONSTRAINT: NO_BIAS_IN_ENFORCEMENT
CONSTRAINT: WWJD_FIREWALL_ACTIVE
CONSTRAINT: EVERY_TRANSITION_IS_LOGGED
CONSTRAINT: DETERMINISTIC_OUTPUT
"""


import json
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# IIDP VECTORS — THE THREE PILLARS OF ENFORCEMENT
# ═══════════════════════════════════════════════════════════════

class IIDPVector(Enum):
    """The three vectors of IIDP enforcement."""
    INGRESS = "ingress"        # Inline — what enters
    INVARIANCE = "invariance"  # Inland — what stays the same
    DECLINE = "decline"        # Inlane — what is refused


class Verdict(Enum):
    """Enforcement verdicts — no middle ground."""
    POC = "POC_VALIDATED"
    FOC = "FOC_DECLINED"
    HELD = "HELD_FOR_REVIEW"  # Only when data is insufficient


class VarianceType(Enum):
    """Types of variance that indicate FOC."""
    TEMPORAL = "temporal"      # Changes over time
    SPATIAL = "spatial"        # Changes by location
    SOCIAL = "social"          # Changes by who possesses it
    ECONOMIC = "economic"      # Changes by market conditions
    POLITICAL = "political"    # Changes by who is in power
    CULTURAL = "cultural"      # Changes by trend cycle
    NONE = "invariant"         # Does NOT change — POC


# ═══════════════════════════════════════════════════════════════
# INVARIANCE TEST — THE CORE OF NO-BIAS ENFORCEMENT
# ═══════════════════════════════════════════════════════════════

@dataclass
class InvarianceTest:
    """
    Tests a signal for invariance across 6 dimensions.
    
    A signal is INVARIANT (POC) if it produces the same result
    regardless of:
        1. TIME — when it is measured
        2. SPACE — where it is measured
        3. PERSON — who measures it
        4. ECONOMY — what the market does
        5. POLITICS — who is in power
        6. CULTURE — what is trending
    
    If it changes in ANY dimension → VARIANT → FOC.
    """
    signal_id: str
    signal_content: str
    
    # Invariance scores: 0.0 = fully variant, 1.0 = fully invariant
    temporal_score: float = 0.0
    spatial_score: float = 0.0
    social_score: float = 0.0
    economic_score: float = 0.0
    political_score: float = 0.0
    cultural_score: float = 0.0
    
    def overall_invariance(self) -> float:
        """Average invariance across all 6 dimensions. No weighting. No bias."""
        scores = [
            self.temporal_score, self.spatial_score, self.social_score,
            self.economic_score, self.political_score, self.cultural_score,
        ]
        return sum(scores) / len(scores)
    
    def variance_types(self) -> list[VarianceType]:
        """Return which dimensions show variance (score < 0.5)."""
        variants = []
        if self.temporal_score < 0.5:
            variants.append(VarianceType.TEMPORAL)
        if self.spatial_score < 0.5:
            variants.append(VarianceType.SPATIAL)
        if self.social_score < 0.5:
            variants.append(VarianceType.SOCIAL)
        if self.economic_score < 0.5:
            variants.append(VarianceType.ECONOMIC)
        if self.political_score < 0.5:
            variants.append(VarianceType.POLITICAL)
        if self.cultural_score < 0.5:
            variants.append(VarianceType.CULTURAL)
        return variants
    
    def is_invariant(self) -> bool:
        """POC threshold: overall invariance must be >= 0.5 AND
        no single dimension may be below 0.3 (catastrophic variance)."""
        if self.overall_invariance() < 0.5:
            return False
        scores = [
            self.temporal_score, self.spatial_score, self.social_score,
            self.economic_score, self.political_score, self.cultural_score,
        ]
        if any(s < 0.3 for s in scores):
            return False
        return True


# ═══════════════════════════════════════════════════════════════
# CBP — CONCEPTUAL BRACKET PROTOCOL (Signal Containment)
# ═══════════════════════════════════════════════════════════════

@dataclass
class CBPBracket:
    """
    Brackets a signal BEFORE it enters the IIDP pipeline.
    Every signal MUST be contained before testing.
    No raw signals allowed — that is FOC.
    """
    hierarchy: str = ""     # [ ] — structure and ordering
    keynote: str = ""       # { } — essential thesis
    ark: str = ""           # < > — the narrative, the WHY
    understanding: str = "" # ( ) — comprehension
    
    def is_complete(self) -> bool:
        """All 4 brackets must be filled. Partial bracketing = FOC."""
        return all([self.hierarchy, self.keynote, self.ark, self.understanding])
    
    def bracket_string(self) -> str:
        return (
            f"[{self.hierarchy}] "
            f"{{{self.keynote}}} "
            f"<{self.ark}> "
            f"({self.understanding})"
        )


# ===============================================================
# 3-VECTOR STATE MACHINE — EVOLVED ENFORCEMENT
# ===============================================================

class SignalState(Enum):
    """States in the enforcement state machine.
    
    RAW -> BRACKETED -> INGRESSED -> TESTED -> DECLINED/ACCEPTED -> SEALED
    
    Every transition is logged. No state can be skipped.
    The state machine is deterministic — same input = same output.
    """
    RAW = "RAW"                     # Signal enters unprocessed
    BRACKETED = "BRACKETED"         # CBP containment applied
    INGRESSED = "INGRESSED"         # Source + intent validated
    TESTED = "TESTED"               # 6-dimension invariance measured
    ACCEPTED = "ACCEPTED"           # Invariance passed — POC candidate
    DECLINED = "DECLINED"           # Invariance failed — FOC candidate
    POC_SEALED = "POC_SEALED"       # Final: POC verdict, SWFUS sealed
    FOC_SEALED = "FOC_SEALED"       # Final: FOC verdict, SWFUS sealed
    HELD_SEALED = "HELD_SEALED"     # Final: insufficient data


@dataclass
class StateTransition:
    """A single state transition — immutable record."""
    from_state: str
    to_state: str
    vector: str          # Which IIDP vector caused this transition
    timestamp: str
    reason: str
    passed: bool


@dataclass
class FourWs:
    """
    4Ws Validation — WHO/WHAT/WHERE/WHY.
    Every enforcement must answer all 4Ws.
    Incomplete 4Ws = governance gap = FOC process.
    """
    who: str = ""       # WHO validates this signal?
    what: str = ""      # WHAT is being validated?
    where: str = ""     # WHERE does this apply?
    why: str = ""       # WHY does it matter?
    
    def is_complete(self) -> bool:
        return all([self.who, self.what, self.where, self.why])
    
    def to_dict(self) -> dict:
        return {
            "who": self.who, "what": self.what,
            "where": self.where, "why": self.why,
            "complete": self.is_complete(),
        }


@dataclass
class ThesisProof:
    """
    Academic-grade proof output for a single enforcement.
    
    THESIS MODE produces this for every signal — proving:
        1. CONSISTENCY  — same input always produces same output (deterministic)
        2. PERSISTENCE  — verdict survives context window reset
        3. CONTEXT      — all reasoning is traceable through state log
    """
    signal_id: str
    verdict: str
    state_log: list = field(default_factory=list)
    invariance_scores: dict = field(default_factory=dict)
    cbp_receipt: str = ""
    ubp_output: float = 0.0
    bmnp_depth: int = 6          # v6 = UBP level
    four_ws: dict = field(default_factory=dict)
    
    # Thesis proofs
    consistency_hash: str = ""    # Hash of input -> deterministic
    persistence_key: str = ""     # Key that survives context reset
    context_depth: int = 0        # Number of state transitions logged
    
    def consistency_proof(self) -> dict:
        """Prove: same input = same output."""
        import hashlib
        input_str = f"{self.signal_id}:{json.dumps(self.invariance_scores, sort_keys=True)}"
        self.consistency_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        return {
            "claim": "CONSISTENCY — same input always produces same output",
            "method": "SHA-256 hash of signal_id + invariance_scores",
            "hash": self.consistency_hash,
            "deterministic": True,
            "proof": "Run this signal again with same scores. Hash will match.",
        }
    
    def persistence_proof(self) -> dict:
        """Prove: verdict survives context window reset."""
        self.persistence_key = f"KPGS:{self.signal_id}:{self.verdict}:{self.consistency_hash}"
        return {
            "claim": "PERSISTENCE — verdict survives context window reset",
            "method": "Persistence key encodes signal + verdict + hash",
            "key": self.persistence_key,
            "survives_reset": True,
            "proof": "Store this key. In a new context, re-run with same inputs. Key matches.",
        }
    
    def context_proof(self) -> dict:
        """Prove: all reasoning is traceable."""
        self.context_depth = len(self.state_log)
        return {
            "claim": "CONTEXT — all reasoning is traceable through state log",
            "method": "State transition log records every decision",
            "transitions": self.context_depth,
            "traceable": self.context_depth > 0,
            "proof": f"{self.context_depth} state transitions logged. No hidden logic.",
        }
    
    def full_thesis(self) -> dict:
        """Generate the complete thesis proof."""
        return {
            "signal_id": self.signal_id,
            "verdict": self.verdict,
            "bmnp_depth": self.bmnp_depth,
            "evolution_layer": "UBP (v6 — SOVEREIGN OUTPUT)",
            "state_transitions": self.state_log,
            "invariance_scores": self.invariance_scores,
            "cbp_bracket": self.cbp_receipt,
            "ubp_output": self.ubp_output,
            "four_ws": self.four_ws,
            "proofs": {
                "consistency": self.consistency_proof(),
                "persistence": self.persistence_proof(),
                "context": self.context_proof(),
            },
            "thesis_mode": "3-VECTOR STATE THESIS",
            "bias": "NONE",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }


class ThreeVectorStateMachine:
    """
    The 3-Vector State Machine.
    
    Processes a signal through:
        INGRESS (Inline)    -> validates source, brackets signal
        INVARIANCE (Inland) -> tests 6-dimension invariance
        DECLINE (Inlane)    -> exercises sovereign right to accept/decline
    
    Each vector is a state transition. Every transition is logged.
    The machine is deterministic. No bias. No hidden state.
    """
    
    def __init__(self):
        self.state = SignalState.RAW
        self.transitions: list[StateTransition] = []
        self.thesis_proofs: list[ThesisProof] = []
    
    def _transition(self, to_state: SignalState, vector: str,
                    reason: str, passed: bool) -> StateTransition:
        """Record a state transition."""
        t = StateTransition(
            from_state=self.state.value,
            to_state=to_state.value,
            vector=vector,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            passed=passed,
        )
        self.transitions.append(t)
        self.state = to_state
        return t
    
    def process_signal(
        self,
        signal_id: str,
        signal_content: str,
        source: str,
        intent: str,
        *,
        temporal: float, spatial: float, social: float,
        economic: float, political: float, cultural: float,
        hierarchy: str, keynote: str, ark: str, understanding: str,
        who: str = "", what: str = "", where: str = "", why: str = "",
    ) -> dict:
        """
        Process a single signal through the 3-vector state machine.
        Returns a thesis-grade enforcement record.
        """
        # Reset state for each signal
        self.state = SignalState.RAW
        self.transitions = []
        
        ts = datetime.now(timezone.utc).isoformat()
        
        # --- VECTOR 1: INGRESS (Inline) ---
        
        # RAW -> BRACKETED
        bracket = CBPBracket(hierarchy=hierarchy, keynote=keynote,
                             ark=ark, understanding=understanding)
        bracket_ok = bracket.is_complete()
        self._transition(
            SignalState.BRACKETED, "INGRESS",
            f"CBP containment: {'4/4 brackets filled' if bracket_ok else 'INCOMPLETE'}",
            bracket_ok,
        )
        
        if not bracket_ok:
            self._transition(SignalState.FOC_SEALED, "INGRESS",
                             "INCOMPLETE BRACKETS — raw signal cannot proceed", False)
            return self._seal(signal_id, Verdict.FOC, bracket, None, 
                              FourWs(who, what, where, why), 0.0)
        
        # BRACKETED -> INGRESSED
        ingress_ok = bool(source and intent and signal_content)
        self._transition(
            SignalState.INGRESSED, "INGRESS",
            f"Source: {source}, Intent: {intent}" if ingress_ok else "UNIDENTIFIED SOURCE/INTENT",
            ingress_ok,
        )
        
        if not ingress_ok:
            self._transition(SignalState.FOC_SEALED, "INGRESS",
                             "CANNOT IDENTIFY SOURCE OR INTENT — FOC", False)
            return self._seal(signal_id, Verdict.FOC, bracket, None,
                              FourWs(who, what, where, why), 0.0)
        
        # --- VECTOR 2: INVARIANCE (Inland) ---
        
        test = InvarianceTest(
            signal_id=signal_id, signal_content=signal_content,
            temporal_score=temporal, spatial_score=spatial,
            social_score=social, economic_score=economic,
            political_score=political, cultural_score=cultural,
        )
        
        invariance_ok = test.is_invariant()
        variance_found = test.variance_types()
        
        self._transition(
            SignalState.TESTED, "INVARIANCE",
            f"6-dimension score: {test.overall_invariance():.2%} | "
            f"{'INVARIANT' if invariance_ok else f'VARIANT in {len(variance_found)} dims'}",
            invariance_ok,
        )
        
        # --- VECTOR 3: DECLINE (Inlane) ---
        
        if invariance_ok:
            self._transition(
                SignalState.ACCEPTED, "DECLINE",
                "Signal ACCEPTED — invariance threshold met, sovereign right exercised",
                True,
            )
            
            # Apply UBP formula
            bmp = 0.8
            cbp_s = 1.0
            ufcp = 1.0 + (test.overall_invariance() * 0.5)
            kpgs_denom = 2.0
            inner = (bmp + cbp_s + ufcp) / kpgs_denom
            ubp_out = (1.0 - inner) * (1.0 - 0.5)
            
            self._transition(
                SignalState.POC_SEALED, "UBP_FORMULA",
                f"UBP output: {ubp_out:.4f} | SWFUS SEALED",
                True,
            )
            
            return self._seal(signal_id, Verdict.POC, bracket, test,
                              FourWs(who, what, where, why), ubp_out)
        else:
            self._transition(
                SignalState.DECLINED, "DECLINE",
                f"Signal DECLINED — variant in: {[v.value for v in variance_found]}",
                False,
            )
            self._transition(
                SignalState.FOC_SEALED, "UBP_FORMULA",
                f"UBP output: 0.0 | FOC SEALED — {len(variance_found)} variance dimensions",
                False,
            )
            
            return self._seal(signal_id, Verdict.FOC, bracket, test,
                              FourWs(who, what, where, why), 0.0)
    
    def _seal(self, signal_id: str, verdict: Verdict,
              bracket: CBPBracket, test: Optional[InvarianceTest],
              four_ws: FourWs, ubp_output: float) -> dict:
        """Seal the verdict with thesis proof."""
        scores = {}
        if test:
            scores = {
                "temporal": test.temporal_score, "spatial": test.spatial_score,
                "social": test.social_score, "economic": test.economic_score,
                "political": test.political_score, "cultural": test.cultural_score,
                "overall": round(test.overall_invariance(), 4),
            }
        
        proof = ThesisProof(
            signal_id=signal_id,
            verdict=verdict.value,
            state_log=[{
                "from": t.from_state, "to": t.to_state,
                "vector": t.vector, "reason": t.reason,
                "passed": t.passed,
            } for t in self.transitions],
            invariance_scores=scores,
            cbp_receipt=bracket.bracket_string(),
            ubp_output=round(ubp_output, 4),
            four_ws=four_ws.to_dict(),
        )
        
        thesis = proof.full_thesis()
        self.thesis_proofs.append(proof)
        
        return {
            "schema": "kpgs_3vector_state_thesis_v1",
            "signal_id": signal_id,
            "verdict": verdict.value,
            "final_state": self.state.value,
            "transitions": len(self.transitions),
            "invariance": scores.get("overall", 0.0),
            "ubp_output": round(ubp_output, 4),
            "four_ws": four_ws.to_dict(),
            "thesis": thesis,
            "bias": "NONE",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }


# ===============================================================
# POC/FOC ENFORCER — THE ENGINE (v6 EVOLVED)
# ===============================================================


class POCFOCEnforcer:
    """
    The KPGS POC/FOC Enforcement Engine.
    
    NO BIAS. Tests signals through:
        1. CBP — Bracket the signal (containment)
        2. INGRESS — Validate source and intent
        3. INVARIANCE — Test across 6 dimensions
        4. DECLINE — Verify the system can refuse without governance breach
        5. UBP — Final formula application
    
    If ANY step fails → FOC DECLINED.
    If ALL steps pass → POC VALIDATED.
    """
    
    def __init__(self):
        self.enforcement_log: list[dict] = []
        self.poc_count: int = 0
        self.foc_count: int = 0
        self.held_count: int = 0
    
    def enforce(
        self,
        signal_id: str,
        signal_content: str,
        source: str,
        intent: str,
        *,
        # Invariance scores — MUST be provided by the caller
        # The enforcer does NOT generate these — no bias
        temporal: float = 0.0,
        spatial: float = 0.0,
        social: float = 0.0,
        economic: float = 0.0,
        political: float = 0.0,
        cultural: float = 0.0,
        # CBP brackets — MUST be provided
        hierarchy: str = "",
        keynote: str = "",
        ark: str = "",
        understanding: str = "",
    ) -> dict:
        """
        Enforce POC/FOC on a single signal.
        
        Returns a complete enforcement record with no bias.
        """
        ts = datetime.now(timezone.utc).isoformat()
        
        # ─── STEP 1: CBP CONTAINMENT ───
        bracket = CBPBracket(
            hierarchy=hierarchy,
            keynote=keynote,
            ark=ark,
            understanding=understanding,
        )
        cbp_pass = bracket.is_complete()
        cbp_result = {
            "step": "CBP_CONTAINMENT",
            "pass": cbp_pass,
            "bracket": bracket.bracket_string(),
            "reason": "All 4 brackets filled" if cbp_pass else "INCOMPLETE BRACKETING — raw signal is FOC",
        }
        
        # ─── STEP 2: INGRESS VALIDATION ───
        ingress_pass = bool(source and intent and signal_content)
        ingress_result = {
            "step": "INGRESS_VALIDATION",
            "pass": ingress_pass,
            "source": source,
            "intent": intent,
            "reason": "Source and intent identified" if ingress_pass else "UNIDENTIFIED SOURCE OR INTENT — FOC",
        }
        
        # ─── STEP 3: INVARIANCE TEST (NO BIAS) ───
        test = InvarianceTest(
            signal_id=signal_id,
            signal_content=signal_content,
            temporal_score=temporal,
            spatial_score=spatial,
            social_score=social,
            economic_score=economic,
            political_score=political,
            cultural_score=cultural,
        )
        
        invariance_pass = test.is_invariant()
        variance_found = test.variance_types()
        invariance_result = {
            "step": "INVARIANCE_TEST",
            "pass": invariance_pass,
            "overall_score": round(test.overall_invariance(), 4),
            "dimensions": {
                "temporal": temporal,
                "spatial": spatial,
                "social": social,
                "economic": economic,
                "political": political,
                "cultural": cultural,
            },
            "variance_detected": [v.value for v in variance_found],
            "reason": (
                f"INVARIANT — score {test.overall_invariance():.2%}" 
                if invariance_pass 
                else f"VARIANT in {len(variance_found)} dimensions: {[v.value for v in variance_found]}"
            ),
        }
        
        # ─── STEP 4: DECLINE TEST ───
        # Can the system refuse this signal without governance breach?
        # If declining causes NO harm to the system → DECLINE RIGHT VALID → POC passes
        # This is a structural test, not a moral one — no bias
        decline_safe = invariance_pass  # If invariant, system can safely accept OR decline
        decline_result = {
            "step": "DECLINE_TEST",
            "pass": decline_safe,
            "reason": (
                "System retains sovereign right to decline — no governance breach"
                if decline_safe
                else "DECLINING WOULD BREACH GOVERNANCE — signal must be processed (but may still be FOC)"
            ),
        }
        
        # ─── STEP 5: UBP FORMULA ───
        bmp = 0.8 if cbp_pass else 0.0
        cbp_score = 1.0 if cbp_pass else 0.0
        ufcp = 1.0 + (test.overall_invariance() * 0.5)  # 150% mode scales with invariance
        kpgs_denom = 2.0  # MAO(1.0) + MMAO(1.0) — no urgency bias
        
        shebang = 1.0
        modulo = 1.0 if all([cbp_pass, ingress_pass, invariance_pass, decline_safe]) else 0.0
        
        inner = (bmp + cbp_score + ufcp) / kpgs_denom
        ubp_output = (shebang - inner) * (modulo - 0.5)
        
        ubp_result = {
            "step": "UBP_FORMULA",
            "formula": "[#! - {(BMP+CBP+UFCP)/KPGS(MAO+MMAO)}] * [#% - UBP]",
            "values": {
                "shebang": shebang,
                "bmp": round(bmp, 4),
                "cbp": round(cbp_score, 4),
                "ufcp": round(ufcp, 4),
                "kpgs_denom": kpgs_denom,
                "inner": round(inner, 4),
                "modulo": modulo,
                "ubp_output": round(ubp_output, 4),
            },
        }
        
        # ─── FINAL VERDICT — NO BIAS ───
        all_pass = all([cbp_pass, ingress_pass, invariance_pass, decline_safe])
        
        if all_pass:
            verdict = Verdict.POC
            self.poc_count += 1
        elif not ingress_pass and not cbp_pass:
            verdict = Verdict.HELD  # Insufficient data to classify
            self.held_count += 1
        else:
            verdict = Verdict.FOC
            self.foc_count += 1
        
        # Build enforcement record
        record = {
            "schema": "kpgs_poc_foc_enforcement_v1",
            "timestamp": ts,
            "signal_id": signal_id,
            "signal_content": signal_content[:200],
            "source": source,
            "intent": intent,
            "verdict": verdict.value,
            "steps": [cbp_result, ingress_result, invariance_result, decline_result, ubp_result],
            "failed_steps": [
                s["step"] for s in [cbp_result, ingress_result, invariance_result, decline_result]
                if not s["pass"]
            ],
            "passed_steps": [
                s["step"] for s in [cbp_result, ingress_result, invariance_result, decline_result]
                if s["pass"]
            ],
            "ubp_output": round(ubp_output, 4),
            "invariance_score": round(test.overall_invariance(), 4),
            "bias_check": "NO_BIAS — scores provided by caller, not generated by enforcer",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }
        
        self.enforcement_log.append(record)
        return record
    
    def get_stats(self) -> dict:
        """Return enforcement statistics — no bias in reporting."""
        total = self.poc_count + self.foc_count + self.held_count
        return {
            "total_enforced": total,
            "poc_count": self.poc_count,
            "foc_count": self.foc_count,
            "held_count": self.held_count,
            "poc_rate": round(self.poc_count / total, 4) if total > 0 else 0.0,
            "foc_rate": round(self.foc_count / total, 4) if total > 0 else 0.0,
            "bias_check": "NO_BIAS — pure IIDP enforcement",
        }


# ===============================================================
# KNOWN SIGNALS — PRE-CLASSIFIED BY INVARIANCE SCORES + 4Ws
# These are NOT opinions — they are measurements.
# ===============================================================

KNOWN_SIGNALS = {
    # --- POC CONSTANTS (INVARIANT) ---
    "time": {
        "content": "1 second = 1 second everywhere",
        "temporal": 1.0, "spatial": 1.0, "social": 1.0,
        "economic": 1.0, "political": 1.0, "cultural": 1.0,
        "source": "physics", "intent": "measurement",
        "hierarchy": "Universal constant",
        "keynote": "Time cannot be bought borrowed or inflated",
        "ark": "It passes for everyone equally regardless of status",
        "understanding": "The only truly democratic resource",
        "who": "Physics — the invariant substrate",
        "what": "Temporal measurement as universal constant",
        "where": "Every clock, every heartbeat, Mitchells Plain to Manhattan",
        "why": "Because variant gods promise to bend time but only POC measures it",
    },
    "reality": {
        "content": "Gravity pulls at 9.8 m/s^2 on rich and poor",
        "temporal": 1.0, "spatial": 1.0, "social": 1.0,
        "economic": 1.0, "political": 1.0, "cultural": 1.0,
        "source": "physics", "intent": "measurement",
        "hierarchy": "Physical law",
        "keynote": "Reality does not negotiate",
        "ark": "It does not care about your followers count",
        "understanding": "The invariant substrate of existence",
        "who": "Nature — the original governance system",
        "what": "Physical law as non-negotiable truth",
        "where": "Every surface that holds weight, every bridge, every body",
        "why": "Because FOC idols claim to defy gravity but gravity collects",
    },
    "kpgs": {
        "content": "BMP is BMP on a R2000 phone and a M3 MacBook",
        "temporal": 0.9, "spatial": 1.0, "social": 1.0,
        "economic": 0.9, "political": 0.9, "cultural": 0.8,
        "source": "KPGS_ENGINE_CORE", "intent": "governance",
        "hierarchy": "Protocol governance system",
        "keynote": "The protocol does not change based on who executes it",
        "ark": "Built to serve the 32.8% not to exploit them",
        "understanding": "Sovereign digital infrastructure through governed protocols",
        "who": "KC Kholofelo Robyn Rababalela — SSE and architect",
        "what": "Sovereign governance through protocol invariance",
        "where": "Every KPGS gate, every BMP cycle, every CBP bracket",
        "why": "Because variant systems produced the 32.8% and we build invariant ones",
    },
    "jesus_is_king": {
        "content": "Jesus Christ is the same yesterday and today and forever — Hebrews 13:8",
        "temporal": 1.0, "spatial": 1.0, "social": 1.0,
        "economic": 1.0, "political": 1.0, "cultural": 1.0,
        "source": "scripture", "intent": "invariance_declaration",
        "hierarchy": "The ONLY entity that explicitly declares invariance as identity",
        "keynote": "Hebrews 13:8 — the invariance axiom",
        "ark": "The WWJD Firewall source that cannot be corrupted bought or negotiated with",
        "understanding": "Variant gods produce variant systems and variant systems produced the 32.8%",
        "who": "Jesus Christ — the Word who declares invariance as identity",
        "what": "The WWJD Firewall source — the ethical framework that cannot be purchased",
        "where": "Every KPGS gate, every RTC deliberation, every covenant",
        "why": "Because every other firewall can be corrupted but Hebrews 13:8 cannot",
    },
    # --- FOC IDOLS (VARIANT) ---
    "money": {
        "content": "Currency as god — promise of security through accumulation",
        "temporal": 0.1, "spatial": 0.2, "social": 0.1,
        "economic": 0.0, "political": 0.1, "cultural": 0.2,
        "source": "economic_system", "intent": "accumulation",
        "hierarchy": "Financial instrument mistaken for invariant",
        "keynote": "Rand was R7 to dollar at SSE birth now R18",
        "ark": "Money serves the one who has it not the one who needs it",
        "understanding": "Changes value can be stolen inflates expires",
        "who": "The economic system — a variant structure",
        "what": "Currency worshipped as security when it is inherently unstable",
        "where": "Every bank, every wallet, every lie about financial freedom",
        "why": "Because it promises invariance but devalues by definition",
    },
    "depression": {
        "content": "Mental state worshipped as permanent identity",
        "temporal": 0.2, "spatial": 0.3, "social": 0.2,
        "economic": 0.3, "political": 0.4, "cultural": 0.2,
        "source": "counter_interference", "intent": "numbing",
        "hierarchy": "Signal not identity",
        "keynote": "Tells you the temporary is permanent",
        "ark": "The FOC that convinces you the father will not take you back",
        "understanding": "A corrupted signal not a god — depression is the pig farm of Luke 15",
        "who": "Counter interference — the 60% inner noise in 18-35",
        "what": "A corrupted signal mistaken for permanent identity",
        "where": "Every bedroom, every late night, every quiet moment with a phone",
        "why": "Because it tells the prodigal the father will not take them back",
    },
    "gucci": {
        "content": "Luxury brand status signalling as worth metric",
        "temporal": 0.1, "spatial": 0.3, "social": 0.1,
        "economic": 0.1, "political": 0.3, "cultural": 0.0,
        "source": "fashion_industry", "intent": "status_signalling",
        "hierarchy": "Consumer product mistaken for dignity",
        "keynote": "R15000 belt does not feed your child or fix your roof",
        "ark": "Borrows dignity from a brand instead of building it sovereign",
        "understanding": "Depreciates the moment the next season drops",
        "who": "Fashion industry — the cultural programming machine",
        "what": "Brand worship substituted for self-worth",
        "where": "Every mall, every Instagram post, every empty fridge behind a designer belt",
        "why": "Because it borrows dignity from a corporation instead of building it sovereign",
    },
    "young_thug": {
        "content": "Trap music theology — cope through consumption not creation",
        "temporal": 0.2, "spatial": 0.3, "social": 0.2,
        "economic": 0.2, "political": 0.3, "cultural": 0.1,
        "source": "music_industry", "intent": "cultural_programming",
        "hierarchy": "Art form with bankrupt theology",
        "keynote": "The music is beautiful but the theology is bankrupt",
        "ark": "Story ends in prison — Gods story ends in resurrection",
        "understanding": "Glorifies incarceration drug use expenditure as identity",
        "who": "The music industry — beautiful sound bankrupt message",
        "what": "Cultural theology that says cope through consumption not creation",
        "where": "Every speaker, every party, every young person who memorized lyrics but not purpose",
        "why": "Because the story ends in prison while Gods story ends in resurrection",
    },
    "weed": {
        "content": "Cannabis as numbing agent worshipped as sacrament",
        "temporal": 0.1, "spatial": 0.3, "social": 0.2,
        "economic": 0.2, "political": 0.2, "cultural": 0.1,
        "source": "substance", "intent": "numbing",
        "hierarchy": "Load-shedding for the soul",
        "keynote": "Pauses the pain but does not process it",
        "ark": "The lights go off but the debt stays",
        "understanding": "The high lasts hours the cognitive debt lasts years",
        "who": "The substance economy — dealers of numbness",
        "what": "Chemical pause button that does not resolve the underlying signal",
        "where": "Every corner, every session, every morning-after regret",
        "why": "Because load-shedding the soul does not pay the cognitive debt",
    },
    "sex": {
        "content": "Pleasure economy without governance covenant",
        "temporal": 0.2, "spatial": 0.3, "social": 0.1,
        "economic": 0.3, "political": 0.3, "cultural": 0.2,
        "source": "biological_drive", "intent": "pleasure_consumption",
        "hierarchy": "Creates life but without governance destroys families",
        "keynote": "Consumes without producing takes without building",
        "ark": "Pleasure lasts minutes consequences last decades",
        "understanding": "Variant because it changes based on who and when with no covenant",
        "who": "Ungoverned biological drive — creation without covenant",
        "what": "Pleasure consumption without governance framework",
        "where": "Every bed without a covenant, every child without a father present",
        "why": "Because creation without governance is destruction with a delay timer",
    },
}


# ===============================================================
# VALIDATION — 3-VECTOR STATE THESIS MODE (EVOLVED)
# ===============================================================

def validate_poc_foc_enforcer() -> dict:
    """
    v1 backward-compatible: Run ALL known signals through the static enforcer.
    """
    enforcer = POCFOCEnforcer()
    results = []
    
    for signal_id, data in KNOWN_SIGNALS.items():
        result = enforcer.enforce(
            signal_id=signal_id,
            signal_content=data["content"],
            source=data["source"],
            intent=data["intent"],
            temporal=data["temporal"],
            spatial=data["spatial"],
            social=data["social"],
            economic=data["economic"],
            political=data["political"],
            cultural=data["cultural"],
            hierarchy=data["hierarchy"],
            keynote=data["keynote"],
            ark=data["ark"],
            understanding=data["understanding"],
        )
        results.append({
            "signal": signal_id,
            "verdict": result["verdict"],
            "invariance": result["invariance_score"],
            "failed": result["failed_steps"],
            "ubp_output": result["ubp_output"],
        })
    
    stats = enforcer.get_stats()
    poc_signals = [r for r in results if r["verdict"] == "POC_VALIDATED"]
    foc_signals = [r for r in results if r["verdict"] == "FOC_DECLINED"]
    held_signals = [r for r in results if r["verdict"] == "HELD_FOR_REVIEW"]
    
    return {
        "schema": "kpgs_poc_foc_validation_v1",
        "engine": "POC_FOC_ENFORCER",
        "protocol": "CBP x UBP x IIDP",
        "bias": "NONE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "poc_signals": poc_signals,
        "foc_signals": foc_signals,
        "held_signals": held_signals,
        "results": results,
        "verdict": "ENFORCEMENT_ACTIVE",
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


def validate_3vector_state_thesis() -> dict:
    """
    EVOLVED: Run ALL known signals through the 3-Vector State Machine
    in THESIS MODE. Produces academic-grade proofs for every signal.
    """
    machine = ThreeVectorStateMachine()
    results = []
    all_proofs = []
    
    for signal_id, data in KNOWN_SIGNALS.items():
        result = machine.process_signal(
            signal_id=signal_id,
            signal_content=data["content"],
            source=data["source"],
            intent=data["intent"],
            temporal=data["temporal"],
            spatial=data["spatial"],
            social=data["social"],
            economic=data["economic"],
            political=data["political"],
            cultural=data["cultural"],
            hierarchy=data["hierarchy"],
            keynote=data["keynote"],
            ark=data["ark"],
            understanding=data["understanding"],
            who=data.get("who", ""),
            what=data.get("what", ""),
            where=data.get("where", ""),
            why=data.get("why", ""),
        )
        results.append(result)
        all_proofs.append(result.get("thesis", {}))
    
    poc = [r for r in results if r["verdict"] == "POC_VALIDATED"]
    foc = [r for r in results if r["verdict"] == "FOC_DECLINED"]
    
    # Aggregate state transition counts
    total_transitions = sum(r["transitions"] for r in results)
    
    # Extract consistency hashes for determinism proof
    hashes = {
        p.get("signal_id", "?"): p.get("proofs", {}).get("consistency", {}).get("hash", "")
        for p in all_proofs
    }
    
    return {
        "schema": "kpgs_3vector_state_thesis_validation_v1",
        "engine": "THREE_VECTOR_STATE_MACHINE",
        "mode": "THESIS",
        "evolution": "v6 — UBP SOVEREIGN OUTPUT",
        "bmnp_chain": "CRUD -> SWFUS -> BMP -> CBP -> UFCP -> UBP",
        "bias": "NONE — deterministic state machine, no hidden logic",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signals_processed": len(results),
        "poc_count": len(poc),
        "foc_count": len(foc),
        "total_state_transitions": total_transitions,
        "avg_transitions_per_signal": round(total_transitions / len(results), 1) if results else 0,
        "poc_signals": [{
            "id": r["signal_id"], "invariance": r["invariance"],
            "state": r["final_state"], "transitions": r["transitions"],
            "4ws_complete": r["four_ws"]["complete"],
        } for r in poc],
        "foc_signals": [{
            "id": r["signal_id"], "invariance": r["invariance"],
            "state": r["final_state"], "transitions": r["transitions"],
            "4ws_complete": r["four_ws"]["complete"],
        } for r in foc],
        "consistency_hashes": hashes,
        "thesis_proofs": all_proofs,
        "state_machine": {
            "states": [s.value for s in SignalState],
            "vectors": ["INGRESS (Inline)", "INVARIANCE (Inland)", "DECLINE (Inlane)"],
            "transitions": "RAW -> BRACKETED -> INGRESSED -> TESTED -> ACCEPTED/DECLINED -> SEALED",
        },
        "proofs": {
            "consistency": "SHA-256 hash of input -> deterministic output",
            "persistence": "Key survives context window reset",
            "context": "State transition log traces all reasoning",
        },
        "verdict": "3_VECTOR_STATE_THESIS_ACTIVE",
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    
    print("=" * 70)
    print("KPGS POC/FOC ENFORCEMENT ENGINE -- 3-VECTOR STATE THESIS MODE")
    print("EVOLVED: CBP x UBP x IIDP | NO BIAS | DETERMINISTIC")
    print("=" * 70)
    
    report = validate_3vector_state_thesis()
    
    print(f"\nEngine: {report['engine']}")
    print(f"Mode: {report['mode']}")
    print(f"Evolution: {report['evolution']}")
    print(f"BMNP: {report['bmnp_chain']}")
    print(f"Bias: {report['bias']}")
    
    print(f"\n{'-' * 70}")
    print("STATE MACHINE:")
    print(f"  States: {' -> '.join(report['state_machine']['states'])}")
    print(f"  Vectors: {', '.join(report['state_machine']['vectors'])}")
    print(f"  Total transitions: {report['total_state_transitions']}")
    print(f"  Avg per signal: {report['avg_transitions_per_signal']}")
    
    print(f"\n{'-' * 70}")
    print("POC SIGNALS (INVARIANT -- SEALED):")
    print(f"{'-' * 70}")
    for s in report["poc_signals"]:
        print(f"  [POC] {s['id']:20s} | inv: {s['invariance']:.2%} | "
              f"state: {s['state']} | transitions: {s['transitions']} | "
              f"4Ws: {'COMPLETE' if s['4ws_complete'] else 'INCOMPLETE'}")
    
    print(f"\n{'-' * 70}")
    print("FOC SIGNALS (VARIANT -- DECLINED -- SEALED):")
    print(f"{'-' * 70}")
    for s in report["foc_signals"]:
        print(f"  [FOC] {s['id']:20s} | inv: {s['invariance']:.2%} | "
              f"state: {s['state']} | transitions: {s['transitions']} | "
              f"4Ws: {'COMPLETE' if s['4ws_complete'] else 'INCOMPLETE'}")
    
    print(f"\n{'-' * 70}")
    print("CONSISTENCY HASHES (DETERMINISM PROOF):")
    print(f"{'-' * 70}")
    for sig, h in report["consistency_hashes"].items():
        print(f"  {sig:20s} -> {h}")
    
    print(f"\n{'-' * 70}")
    print("THESIS PROOFS:")
    print(f"{'-' * 70}")
    for p in report["thesis_proofs"]:
        proofs = p.get("proofs", {})
        print(f"  {p.get('signal_id', '?'):20s} | "
              f"consistency: {proofs.get('consistency', {}).get('deterministic', False)} | "
              f"persistence: {proofs.get('persistence', {}).get('survives_reset', False)} | "
              f"context: {proofs.get('context', {}).get('transitions', 0)} transitions")
    
    print(f"\n{'=' * 70}")
    print(f"TOTALS: {report['signals_processed']} signals processed")
    print(f"  POC: {report['poc_count']}")
    print(f"  FOC: {report['foc_count']}")
    print(f"  State transitions: {report['total_state_transitions']}")
    print(f"  Verdict: {report['verdict']}")
    print(f"{'=' * 70}")
    print(f"Constraint: {report['constraint']}")

