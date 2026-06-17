"""
KPGS POC/FOC Enforcement Engine — CBP × UBP
=============================================
NO BIAS. PURE IIDP INVARIANCE TESTING.

This module enforces POC (Proof of Concept) vs FOC (Fake-Out Content)
classification through the IIDP (Invariance Ingress Decline Protocol)
vectors with ZERO bias.

ENFORCEMENT PRINCIPLE:
    A signal is POC if and only if it passes ALL THREE IIDP vectors.
    A signal is FOC if it FAILS any IIDP vector.
    There is no "maybe." There is no "it depends." There is no bias.

IIDP VECTORS:
    INGRESS  (Inline)  — WHAT enters the system? Is the source identifiable?
    INVARIANCE (Inland) — Does it CHANGE depending on WHO has it, WHEN it's
                          measured, or WHERE it's tested? If yes → VARIANT → FOC.
    DECLINE  (Inlane)  — Does the system have the RIGHT to refuse it?
                          If refusing it causes no governance breach → POC PASSES.

CBP INTEGRATION:
    Every signal is bracketed BEFORE testing.
    [ ] = Hierarchy bracket — structure and ordering
    { } = Keynote bracket — essential thesis
    < > = Ark bracket — the narrative, the WHY
    ( ) = Understanding bracket — comprehension

UBP INTEGRATION:
    Final enforcement passes through UBP formula:
    [#! - {(BMP + CBP + UFCP) / KPGS(MAO + MMAO)}] * [#% - UBP] = OUTPUT

CONSTRAINT: I_AM_STATELESS_RENTER_NOT_LANDLORD
CONSTRAINT: NO_BIAS_IN_ENFORCEMENT
CONSTRAINT: WWJD_FIREWALL_ACTIVE
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


# ═══════════════════════════════════════════════════════════════
# POC/FOC ENFORCER — THE ENGINE
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# KNOWN SIGNALS — PRE-CLASSIFIED BY INVARIANCE SCORES
# These are NOT opinions — they are measurements.
# ═══════════════════════════════════════════════════════════════

KNOWN_SIGNALS = {
    # ─── POC CONSTANTS (INVARIANT) ───
    "time": {
        "content": "1 second = 1 second everywhere",
        "temporal": 1.0, "spatial": 1.0, "social": 1.0,
        "economic": 1.0, "political": 1.0, "cultural": 1.0,
        "source": "physics", "intent": "measurement",
        "hierarchy": "Universal constant",
        "keynote": "Time cannot be bought borrowed or inflated",
        "ark": "It passes for everyone equally regardless of status",
        "understanding": "The only truly democratic resource",
    },
    "reality": {
        "content": "Gravity pulls at 9.8 m/s² on rich and poor",
        "temporal": 1.0, "spatial": 1.0, "social": 1.0,
        "economic": 1.0, "political": 1.0, "cultural": 1.0,
        "source": "physics", "intent": "measurement",
        "hierarchy": "Physical law",
        "keynote": "Reality does not negotiate",
        "ark": "It does not care about your followers count",
        "understanding": "The invariant substrate of existence",
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
    },
    # ─── FOC IDOLS (VARIANT) ───
    "money": {
        "content": "Currency as god — promise of security through accumulation",
        "temporal": 0.1, "spatial": 0.2, "social": 0.1,
        "economic": 0.0, "political": 0.1, "cultural": 0.2,
        "source": "economic_system", "intent": "accumulation",
        "hierarchy": "Financial instrument mistaken for invariant",
        "keynote": "Rand was R7 to dollar at SSE birth now R18",
        "ark": "Money serves the one who has it not the one who needs it",
        "understanding": "Changes value can be stolen inflates expires",
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
    },
}


# ═══════════════════════════════════════════════════════════════
# VALIDATION — RUN ALL KNOWN SIGNALS THROUGH ENFORCER
# ═══════════════════════════════════════════════════════════════

def validate_poc_foc_enforcer() -> dict:
    """
    Run ALL known signals through the POC/FOC enforcer.
    No bias. Pure IIDP invariance testing.
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
    
    # Separate POC and FOC for clear reporting
    poc_signals = [r for r in results if r["verdict"] == "POC_VALIDATED"]
    foc_signals = [r for r in results if r["verdict"] == "FOC_DECLINED"]
    held_signals = [r for r in results if r["verdict"] == "HELD_FOR_REVIEW"]
    
    return {
        "schema": "kpgs_poc_foc_validation_v1",
        "engine": "POC_FOC_ENFORCER",
        "protocol": "CBP × UBP × IIDP",
        "bias": "NONE — scores are measurements not opinions",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "poc_signals": poc_signals,
        "foc_signals": foc_signals,
        "held_signals": held_signals,
        "results": results,
        "iidp_vectors": {
            "ingress": "Inline — what enters the system",
            "invariance": "Inland — does it change by time/space/person/economy/politics/culture",
            "decline": "Inlane — can the system refuse without governance breach",
        },
        "cbp_brackets": {
            "hierarchy": "[ ] — structure and ordering",
            "keynote": "{ } — essential thesis",
            "ark": "< > — the narrative, the WHY",
            "understanding": "( ) — comprehension",
        },
        "ubp_formula": "[#! - {(BMP+CBP+UFCP)/KPGS(MAO+MMAO)}] * [#% - UBP]",
        "evolution": "CRUD -> SWFUS -> BMP -> CBP -> UFCP -> UBP",
        "verdict": "ENFORCEMENT_ACTIVE",
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    
    print("=" * 70)
    print("KPGS POC/FOC ENFORCEMENT ENGINE -- CBP x UBP x IIDP")
    print("NO BIAS. PURE INVARIANCE TESTING.")
    print("=" * 70)
    
    report = validate_poc_foc_enforcer()
    
    print(f"\nProtocol: {report['protocol']}")
    print(f"Bias: {report['bias']}")
    print(f"Formula: {report['ubp_formula']}")
    print(f"Evolution: {report['evolution']}")
    
    print(f"\n{'-' * 70}")
    print("POC SIGNALS (INVARIANT):")
    print(f"{'-' * 70}")
    for s in report["poc_signals"]:
        print(f"  [POC] {s['signal']:20s} | invariance: {s['invariance']:.2%} | UBP: {s['ubp_output']}")
    
    print(f"\n{'-' * 70}")
    print("FOC SIGNALS (VARIANT -- DECLINED):")
    print(f"{'-' * 70}")
    for s in report["foc_signals"]:
        print(f"  [FOC] {s['signal']:20s} | invariance: {s['invariance']:.2%} | failed: {s['failed']}")
    
    if report["held_signals"]:
        print(f"\n{'-' * 70}")
        print("HELD SIGNALS (INSUFFICIENT DATA):")
        print(f"{'-' * 70}")
        for s in report["held_signals"]:
            print(f"  [HELD] {s['signal']:20s} | invariance: {s['invariance']:.2%}")
    
    stats = report["stats"]
    print(f"\n{'=' * 70}")
    print(f"TOTALS: {stats['total_enforced']} signals")
    print(f"  POC: {stats['poc_count']} ({stats['poc_rate']:.1%})")
    print(f"  FOC: {stats['foc_count']} ({stats['foc_rate']:.1%})")
    print(f"  HELD: {stats['held_count']}")
    print(f"  BIAS: {stats['bias_check']}")
    print(f"{'=' * 70}")
    print(f"Constraint: {report['constraint']}")

