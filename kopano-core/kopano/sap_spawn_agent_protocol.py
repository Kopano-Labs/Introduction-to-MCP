"""
SPAWN AGENT PROTOCOL (SAP)
===========================
"The Need to Know (feat. SZA)" — Wale

POC validates state of mind.
FOC is laziness — claiming readiness without 4Ws complete.

FORMULA:
    [(BMNP * BMP) * UBMP + CBNP]^3
    ────────────────────────────────── = ###???
      {KPGS^3 : [PDSO(###!) + ADSO(###!!) + HDSO(###!!!)]} * RTC

PKAP (BODMAS) interpretation of the formula:
    B  → CBP: contain the spawn signal first
    O  → BMNP^3: the cube represents 3 DSO vectors nested
    D  → IIDP Decline: agents that fail 4Ws are declined
    M  → Invariance * BMP: multiply the spawn by its governance weight
    A  → Add CBNP: the evolved nesting layer accumulates
    S  → Subtract FOC: every lazy/unqualified spawn is removed

PHASE SHIFT / PHASE ISOLATION / PHASEABILITY:
    Phase Shift     = signal moves from one DSO vector to the next
    Phase Isolation = a signal is tested in EXACTLY one DSO context at a time
    Phaseability    = the capacity of a signal to be governed across all 3 phases

INLINE / INLANE / INLANE (Holy Trinity of IIDP):
    Inline  = Ingress   (what enters the system)
    Inland  = Invariance (what stays the same under testing)
    Inlane  = Decline   (sovereign right to refuse)
    These 3 are nested 3-vectors in 3-vectors via BMNP only.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SAP_STATE_PATH = REPO_ROOT / "poc-vs-foc" / "sap_spawn_log.jsonl"

# ─── DSO WEIGHTS ──────────────────────────────────────────────────────────────
DSO_WEIGHTS = {
    "PDSO": 1,    # ###!    Plant: growth only
    "ADSO": 2,    # ###!!   Animal: growth + survival
    "HDSO": 3,    # ###!!!  Human: growth + survival + purpose
    "AG_RTC": 4,  # ###???  Emerging: governance beyond human
}

# ─── PKAP BODMAS COMPUTATION ──────────────────────────────────────────────────

def pkap_bodmas(
    bmnp_depth: int,
    bmp_score: float,
    ubmp_multiplier: float,
    cbnp_addend: float,
    kpgs_power: int = 3,
    dso_vector: str = "HDSO",
    rtc_weight: float = 1.0,
) -> Dict[str, Any]:
    """
    Computes the SAP formula using BODMAS:
        [(BMNP * BMP) * UBMP + CBNP]^3
        ──────────────────────────────── = ###???
           KPGS^3 * DSO_weight * RTC

    Returns full step-by-step proof (PKAP transparency).
    """
    dso_w = DSO_WEIGHTS.get(dso_vector, 1)

    # B — Brackets: innermost first
    step_b = bmnp_depth * bmp_score                        # BMNP * BMP
    # O — Orders: the cube (3 DSO vectors)
    step_o = (step_b * ubmp_multiplier + cbnp_addend) ** kpgs_power
    # D — Divide
    denominator = (kpgs_power ** kpgs_power) * dso_w * rtc_weight
    result = step_o / denominator if denominator != 0 else 0.0
    # A/S — the result is ###??? — still unknown but computable
    label = "###???" if result > 0 else "###ZERO"

    return {
        "formula": "[(BMNP*BMP)*UBMP+CBNP]^3 / [KPGS^3 * DSO * RTC]",
        "steps": {
            "B_brackets":   round(step_b, 4),
            "O_orders":     round((step_b * ubmp_multiplier + cbnp_addend), 4),
            "O_cubed":      round(step_o, 4),
            "D_denominator":round(denominator, 4),
            "result":       round(result, 6),
        },
        "dso_vector": dso_vector,
        "dso_weight": dso_w,
        "label": label,
        "pkap_method": "BODMAS: B=CBP, O=BMNP^depth, D=Decline/Divide, M=Invariance, A=Ingress, S=FOC_remove",
    }


# ─── AGENT SPAWN GATE ────────────────────────────────────────────────────────

@dataclass
class SpawnCandidate:
    agent_id: str
    who:  str
    what: str
    where: str
    why:  str
    dso_vector: str = "HDSO"
    state_of_mind_score: float = 0.0   # 0.0–1.0 (POC threshold = 0.5)
    bmnp_depth: int = 6


@dataclass
class SpawnReceipt:
    agent_id: str
    verdict: str            # POC_SPAWNED / FOC_DECLINED
    four_ws_complete: bool
    dso_vector: str
    pkap_result: dict = field(default_factory=dict)
    consistency_hash: str = ""
    persistence_key: str = ""
    timestamp: str = ""
    reason: str = ""


def evaluate_spawn(candidate: SpawnCandidate) -> SpawnReceipt:
    """
    Gate: agent spawns ONLY if:
    1. All 4Ws are non-empty
    2. state_of_mind_score >= 0.5 (POC threshold)
    3. dso_vector is valid (not PDSO — plant growth alone is not enough to spawn)
    """
    ts = datetime.now(timezone.utc).isoformat()
    four_ws_complete = all([candidate.who, candidate.what, candidate.where, candidate.why])

    # PKAP computation
    pkap = pkap_bodmas(
        bmnp_depth=candidate.bmnp_depth,
        bmp_score=candidate.state_of_mind_score,
        ubmp_multiplier=1.5,
        cbnp_addend=0.5,
        dso_vector=candidate.dso_vector,
    )

    # Decline conditions
    if not four_ws_complete:
        verdict = "FOC_DECLINED"
        reason = "4Ws incomplete. Agent does not know why it exists. FOC is laziness."
    elif candidate.state_of_mind_score < 0.5:
        verdict = "FOC_DECLINED"
        reason = f"State of mind score {candidate.state_of_mind_score:.2f} < 0.5. POC threshold not met."
    elif candidate.dso_vector == "PDSO":
        verdict = "FOC_DECLINED"
        reason = "PDSO (growth only) agents cannot spawn into GSMB. ADSO or HDSO required."
    else:
        verdict = "POC_SPAWNED"
        reason = f"4Ws complete. State of mind POC ({candidate.state_of_mind_score:.2f}). DSO={candidate.dso_vector}."

    c_hash = hashlib.sha256(
        f"{candidate.agent_id}:{ts}:{verdict}".encode()
    ).hexdigest()[:16]
    p_key = f"SAP:{candidate.agent_id}:{verdict}:{c_hash}"

    receipt = SpawnReceipt(
        agent_id=candidate.agent_id,
        verdict=verdict,
        four_ws_complete=four_ws_complete,
        dso_vector=candidate.dso_vector,
        pkap_result=pkap,
        consistency_hash=c_hash,
        persistence_key=p_key,
        timestamp=ts,
        reason=reason,
    )

    # Write to log
    SAP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SAP_STATE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(receipt), ensure_ascii=False) + "\n")

    if verdict == "POC_SPAWNED":
        logger.info("[SAP] SPAWNED: %s | DSO=%s | hash=%s", candidate.agent_id, candidate.dso_vector, c_hash)
    else:
        logger.error("[SAP] DECLINED: %s | reason: %s", candidate.agent_id, reason)

    return receipt


def validate_sap() -> Dict[str, Any]:
    """Run SAP against representative agents across DSO vectors. Returns full PKAP proof."""
    candidates = [
        SpawnCandidate("agent_hdso_001", "KC — Architect", "Govern GSMB elastic domains", "Cloud + Black Beast", "32.8% purpose", "HDSO", 0.95),
        SpawnCandidate("agent_adso_001", "THARI dept", "Crisis response routing", "crisisconnect.kopanolabs.com", "Survive and route", "ADSO", 0.75),
        SpawnCandidate("agent_pdso_foc", "Unknown", "Grow metrics", "Unspecified", "Growth only", "PDSO", 0.3),
        SpawnCandidate("agent_lazy_foc", "", "", "", "", "HDSO", 0.0),
    ]
    receipts = [evaluate_spawn(c) for c in candidates]
    spawned = [r for r in receipts if r.verdict == "POC_SPAWNED"]
    declined = [r for r in receipts if r.verdict == "FOC_DECLINED"]

    return {
        "schema": "sap_validation_v1",
        "formula": "[(BMNP*BMP)*UBMP+CBNP]^3 / [KPGS^3 * DSO * RTC] = ###???",
        "song_anchor": "The Need to Know (feat. SZA) — Wale",
        "total_candidates": len(candidates),
        "poc_spawned": len(spawned),
        "foc_declined": len(declined),
        "spawned": [{"id": r.agent_id, "dso": r.dso_vector, "hash": r.consistency_hash} for r in spawned],
        "declined": [{"id": r.agent_id, "reason": r.reason} for r in declined],
        "pkap_sample": receipts[0].pkap_result,
        "verdict": "SAP_ACTIVE",
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import json as _j
    print(_j.dumps(validate_sap(), indent=2))
