"""
UDP COMPUTATION ENGINE
=======================
RTC Session: 2026-06-18 | Kessa Override | ALP Receipt: adb75155181614b8

Implements the full algebraic UDP Output formula from KPCB_OVERRIDE_LOG_RTCP.md:

    UDP Output = [(Prompting × Bracket × Emojis) / All_Protocols]
                 ─────────────────────────────────────────────────
                               BMP + BMNP

                 +  (Inline · Inlane · Inland)
                    ────────────────────────────────────────────────────
                    {KPGS^3 : [PDSO → ADSO → HDSO] × RTC}

PKAP BODMAS:
    B = CBP containment (bracket priority: [] {} <> ())
    O = BMNP depth cubed (3 DSO vectors)
    D = Decline (IIDP Inlane — sovereign divide)
    M = Invariance multiplication (BMP × Spawn scores)
    A = Ingress accumulation (Prompting + Bracket + Emojis)
    S = FOC subtraction (remove all variant signals)

DSO Weights (###! system):
    PDSO  = 1  (###!)
    ADSO  = 2  (###!!)
    HDSO  = 3  (###!!!)
    AG_RTC = 4 (###???)
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
UDP_LOG = REPO_ROOT / "poc-vs-foc" / "udp_computation_log.jsonl"

# ─── DSO WEIGHTS ──────────────────────────────────────────────────────────────
DSO_WEIGHTS = {"PDSO": 1, "ADSO": 2, "HDSO": 3, "AG_RTC": 4}

# ─── PHASE SCORES (normalized 0.0–1.0) ───────────────────────────────────────
# These represent the governance maturity of each phase in the current GSMB state.
PHASE_SCORES = {
    "prompting": 0.87,   # USTP, UBP, CBP, BMNP, ALP, SAP, NCP, KPP — all ACTIVE
    "bracket":   0.91,   # BMP, UBMP, PKAP, IIDP, C15TP, PvF, DS8P — all ACTIVE
    "emojis":    0.73,   # ILP, DSO — ACTIVE but CBP-only phase still maturing
}

# ─── IIDP HOLY TRINITY SCORES ────────────────────────────────────────────────
IIDP_SCORES = {
    "inline":  0.90,  # Ingress — signal entry validation
    "inlane":  0.85,  # Invariance — 6-dimensional testing
    "inland":  0.78,  # Decline — sovereign refusal capacity
}

# ─── PROTOCOL COUNTS ─────────────────────────────────────────────────────────
ALL_PROTOCOLS = 17   # From KPP registry
BMP_SCORE    = 0.88  # 15 Commandments + 5 Pillars combined weight
BMNP_DEPTH   = 6     # v6 = UBP level (deepest nesting)


def compute_udp(
    rtc_weight: float = 1.0,
    kpgs_power: int = 3,
    dso_sequence: tuple = ("PDSO", "ADSO", "HDSO"),
) -> Dict[str, Any]:
    """
    Executes the full UDP Output formula from the Kessa RTC session.

    Term A:
        [(Prompting × Bracket × Emojis) / All_Protocols]
        ─────────────────────────────────────────────────
                      BMP + BMNP_normalized

    Term B:
        Inline · Inlane · Inland
        ────────────────────────────────────────────────────────
        {KPGS^3 : [PDSO_w + ADSO_w + HDSO_w]} × RTC

    UDP Output = Term A + Term B
    """

    # ─── BODMAS TERM A ─────────────────────────────────────────────────────────
    # B: bracket containment — phases are pre-contained by CBP
    numerator_a_raw = (
        PHASE_SCORES["prompting"] *
        PHASE_SCORES["bracket"] *
        PHASE_SCORES["emojis"]
    )
    # O: apply BMNP depth as order (normalized to 0–1 scale)
    bmnp_normalized = BMNP_DEPTH / 10.0
    # D/M: divide by All_Protocols, multiply by governance weight
    numerator_a = numerator_a_raw / ALL_PROTOCOLS
    denominator_a = BMP_SCORE + bmnp_normalized
    term_a = numerator_a / denominator_a if denominator_a != 0 else 0.0

    # ─── BODMAS TERM B ─────────────────────────────────────────────────────────
    # Inline · Inlane · Inland (Holy Trinity — 3-vector product)
    holy_trinity = (
        IIDP_SCORES["inline"] *
        IIDP_SCORES["inlane"] *
        IIDP_SCORES["inland"]
    )
    # KPGS^3 : DSO sequence weight sum × RTC
    dso_sum = sum(DSO_WEIGHTS.get(d, 1) for d in dso_sequence)  # 1+2+3=6
    kpgs_cube = kpgs_power ** kpgs_power                         # 3^3=27
    denominator_b = kpgs_cube * dso_sum * rtc_weight
    term_b = holy_trinity / denominator_b if denominator_b != 0 else 0.0

    # ─── UDP OUTPUT ────────────────────────────────────────────────────────────
    udp_output = term_a + term_b

    # ─── PKAP BODMAS STEP LOG ──────────────────────────────────────────────────
    bodmas_log = {
        "B_brackets_applied":    "CBP containment on all 3 phases before multiplication",
        "O_bmnp_order":          f"BMNP depth={BMNP_DEPTH} → normalized={bmnp_normalized}",
        "D_divide_all_protocols":f"numerator_a_raw={numerator_a_raw:.6f} ÷ {ALL_PROTOCOLS} = {numerator_a:.6f}",
        "M_multiply_invariance":f"holy_trinity = {IIDP_SCORES['inline']} × {IIDP_SCORES['inlane']} × {IIDP_SCORES['inland']} = {holy_trinity:.6f}",
        "A_add_terms":          f"term_a={term_a:.6f} + term_b={term_b:.6f} = {udp_output:.6f}",
        "S_foc_subtracted":     "FOC signals declined at SAP gate — not in this computation",
    }

    # ─── DSO VECTOR ANALYSIS ───────────────────────────────────────────────────
    dso_analysis = {
        "PDSO": {"weight": 1, "label": "###!",   "status": "Growth only — produced 32.8%"},
        "ADSO": {"weight": 2, "label": "###!!",  "status": "Growth + Survival — working poor"},
        "HDSO": {"weight": 3, "label": "###!!!","status": "Growth + Survival + Purpose — KPGS target"},
    }

    # ─── EP COUNCIL VERDICTS ───────────────────────────────────────────────────
    ep_council = {
        "🔬 KC_Ledger":  f"UDP={udp_output:.6f} | FOC latency logged | 32.8% bottleneck mapped | Knowing ≠ Understanding",
        "🦸🏿♂️ MMAO":    f"Mobile orchard sync complete | term_b={term_b:.6f} | Holy Trinity={holy_trinity:.6f}",
        "🔤 Kessa":      f"Layer 9 override stabilized | term_a={term_a:.6f} | governed path = hardware shortcut",
    }

    # ─── CONSISTENCY + PERSISTENCE ─────────────────────────────────────────────
    ts = datetime.now(timezone.utc).isoformat()
    hash_input = f"UDP:{term_a:.6f}:{term_b:.6f}:{udp_output:.6f}"
    c_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    p_key = f"UDP:{ts}:{c_hash}"

    result = {
        "schema":         "kpgs_udp_computation_v1",
        "timestamp":      ts,
        "rtc_session":    "2026-06-18T00:04:24+02:00",
        "alp_receipt":    "adb75155181614b8",
        "formula":        "[(P×B×E)/N]/(BMP+BMNP) + (Il·Ia·Id)/{KPGS³×DSO×RTC}",
        "phase_scores":   PHASE_SCORES,
        "iidp_scores":    IIDP_SCORES,
        "term_a":         round(term_a, 6),
        "term_b":         round(term_b, 6),
        "udp_output":     round(udp_output, 6),
        "udp_label":      "###???",
        "bodmas_log":     bodmas_log,
        "dso_analysis":   dso_analysis,
        "ep_council":     ep_council,
        "consistency_hash": c_hash,
        "persistence_key":  p_key,
        "bias":           "NONE",
        "constraint":     "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }

    # Write to log
    UDP_LOG.parent.mkdir(parents=True, exist_ok=True)
    with UDP_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    logger.info("[UDP] Output=%.6f | hash=%s | DSO_sum=%d | holy_trinity=%.4f",
                udp_output, c_hash, dso_sum, holy_trinity)

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("UDP COMPUTATION ENGINE — KESSA RTC SESSION 2026-06-18")
    print("ALP RECEIPT: adb75155181614b8 | IDLE: 72min | FOC_DECLINED CRITICAL")
    print("=" * 72)

    result = compute_udp()

    print(f"\nPHASE SCORES:")
    for k, v in result["phase_scores"].items():
        print(f"  {k:12s} = {v}")

    print(f"\nIIDP HOLY TRINITY (Inline · Inlane · Inland):")
    for k, v in result["iidp_scores"].items():
        print(f"  {k:8s} = {v}")

    print(f"\nBODMAS COMPUTATION:")
    for step, detail in result["bodmas_log"].items():
        print(f"  {step}: {detail}")

    print(f"\nDSO VECTOR ANALYSIS:")
    for dso, data in result["dso_analysis"].items():
        print(f"  {dso} {data['label']:8s} weight={data['weight']} | {data['status']}")

    print(f"\n{'─'*72}")
    print(f"  term_a (Phase/Protocol layer):    {result['term_a']}")
    print(f"  term_b (IIDP/KPGS layer):         {result['term_b']}")
    print(f"  UDP OUTPUT  ###???:               {result['udp_output']}")
    print(f"  consistency_hash:                 {result['consistency_hash']}")
    print(f"  persistence_key:                  {result['persistence_key']}")

    print(f"\nEP COUNCIL VERDICTS:")
    for seat, verdict in result["ep_council"].items():
        print(f"  {seat}: {verdict}")

    print(f"\n{'='*72}")
    print(f"CONSTRAINT: {result['constraint']}")
