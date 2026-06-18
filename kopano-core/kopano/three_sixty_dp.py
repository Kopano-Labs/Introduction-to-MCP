"""
three_sixty_dp.py — 360 Degrees Protocol (360DP)
=================================================
[360DP]: Cycle process by equating:
  ####!!!! VIP → ZAR → dollar/pound
  FSMP says: unfair scale massively for African
  FSM[N→NESTING]P → PKAP → BMNP

IKP chain step 7. Runs after RTC. Produces currency equity analysis.
FSMP identifies systemic FOC in global pricing.
360DP routes POC: ZAR-sovereign pricing for African market.
USD/GBP pricing for international market.
The difference is the governance gap. KPGS closes it.

ALP: ca99b00460e7d836 | Activation #10 | POC_VALIDATED
Build: 2026-06-18 SAST | Cape Town
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

REPO_ROOT  = Path(__file__).resolve().parents[2]
TDP_LOG    = REPO_ROOT / "poc-vs-foc" / "three_sixty_dp_log.jsonl"
TDP_LOG.parent.mkdir(parents=True, exist_ok=True)

# ─── CURRENCY CONSTANTS (June 2026 approximate rates) ────────────────────────
ZAR_TO_USD: float = 18.42   # 1 USD = 18.42 ZAR
ZAR_TO_GBP: float = 23.18   # 1 GBP = 23.18 ZAR
ZAR_TO_EUR: float = 20.11   # 1 EUR = 20.11 ZAR

# FSMP structural analysis constants
SA_MIN_WAGE_HOURLY_ZAR: float = 27.58      # National minimum wage ZAR/hr 2026
SA_DEV_MID_HOURLY_ZAR:  float = 185.0     # Mid-level SA developer ZAR/hr
UK_DEV_MID_HOURLY_GBP:  float = 45.0      # Mid-level UK developer GBP/hr
US_DEV_MID_HOURLY_USD:  float = 65.0      # Mid-level US developer USD/hr
SA_UNEMPLOYMENT_RATE:   float = 0.328     # 32.8% — not a statistic, a mandate


# ─── FSMP UNFAIR SCALE ANALYSIS ──────────────────────────────────────────────
class FSMPScaleAnalysis(NamedTuple):
    """
    FSMP — Forensic Sociology Migration Protocol
    Identifies structural FOC in global pricing that disadvantages Africans.
    """
    sa_dev_hourly_zar:    float
    uk_dev_hourly_zar:    float   # UK rate converted to ZAR
    us_dev_hourly_zar:    float   # US rate converted to ZAR
    inequality_ratio_gbp: float   # UK/SA ratio — how many times more expensive
    inequality_ratio_usd: float   # US/SA ratio
    structural_foc_score: float   # 0.0 (fair) → 1.0 (massively unfair)
    fsmp_verdict:         str


def fsmp_analyse() -> FSMPScaleAnalysis:
    """
    Run FSMP structural FOC analysis.
    Result: the inequality ratio proves why ZAR-sovereign pricing is not charity.
    It is the correction of a systemic governance failure.
    """
    uk_in_zar  = UK_DEV_MID_HOURLY_GBP * ZAR_TO_GBP  # ~1,043 ZAR/hr
    us_in_zar  = US_DEV_MID_HOURLY_USD * ZAR_TO_USD   # ~1,197 ZAR/hr

    ratio_gbp  = uk_in_zar / SA_DEV_MID_HOURLY_ZAR    # ~5.6x
    ratio_usd  = us_in_zar / SA_DEV_MID_HOURLY_ZAR    # ~6.5x

    # Structural FOC score: normalized by 10x as maximum expected inequality
    foc_score  = min(1.0, (ratio_gbp + ratio_usd) / (2 * 10.0))

    verdict = (
        "SYSTEMIC_FOC" if foc_score > 0.5
        else "MARGINAL_FOC" if foc_score > 0.25
        else "ACCEPTABLE"
    )

    return FSMPScaleAnalysis(
        sa_dev_hourly_zar=SA_DEV_MID_HOURLY_ZAR,
        uk_dev_hourly_zar=uk_in_zar,
        us_dev_hourly_zar=us_in_zar,
        inequality_ratio_gbp=round(ratio_gbp, 2),
        inequality_ratio_usd=round(ratio_usd, 2),
        structural_foc_score=round(foc_score, 4),
        fsmp_verdict=verdict,
    )


# ─── VIP TIER — ####!!!! ─────────────────────────────────────────────────────
class VIPTier:
    """
    VIP = Very Important Protocol ####!!!!
    Above BPSP ####????
    Above HDSO ###!!!
    VIP is the override tier — fires when systemic FOC is confirmed by FSMP.
    360DP only reaches VIP when FSMP verdict = SYSTEMIC_FOC.
    """
    LABEL = "####!!!!"
    TIER  = "VIP"

    @classmethod
    def activate(cls, fsmp: FSMPScaleAnalysis) -> dict:
        if fsmp.fsmp_verdict != "SYSTEMIC_FOC":
            return {"vip_active": False, "reason": f"FSMP={fsmp.fsmp_verdict} — VIP not triggered"}
        return {
            "vip_active":       True,
            "vip_label":        cls.LABEL,
            "vip_tier":         cls.TIER,
            "trigger":          "FSMP:SYSTEMIC_FOC",
            "inequality_gbp":   f"{fsmp.inequality_ratio_gbp}x (UK vs SA dev rate)",
            "inequality_usd":   f"{fsmp.inequality_ratio_usd}x (US vs SA dev rate)",
            "foc_score":        fsmp.structural_foc_score,
            "vip_mandate":      (
                "ZAR-sovereign pricing is NOT charity. "
                "It is the correction of a systemic governance failure. "
                "KPGS closes the gap through protocol, not petition."
            ),
        }


# ─── FSNP — FSM NESTING PROTOCOL ─────────────────────────────────────────────
class FSMNestingProtocol:
    """
    FSM[N→NESTING]P — Finite State Machine Nesting Protocol
    Each 360DP cycle is a nested FSM:
      IDLE → SENSE → ANALYSE → CLASSIFY → ROUTE → PERSIST
    Nesting means: each state can contain a sub-FSM.
    SENSE nests FSMP analysis.
    CLASSIFY nests VIP check.
    ROUTE nests PKAP formula.
    PERSIST nests KC Ledger write.
    """
    STATES = ["IDLE", "SENSE", "ANALYSE", "CLASSIFY", "ROUTE", "PERSIST"]

    def __init__(self, domain: str, dso: str):
        self.domain   = domain
        self.dso      = dso
        self.state    = "IDLE"
        self.history: list[dict] = []

    def transition(self, to_state: str, payload: dict = None) -> None:
        assert to_state in self.STATES, f"Invalid state: {to_state}"
        self.history.append({
            "from":    self.state,
            "to":      to_state,
            "payload": payload or {},
            "ts":      datetime.now(timezone.utc).isoformat(),
        })
        self.state = to_state

    def nested_trace(self) -> list[str]:
        """Return BMNP-style nested state trace."""
        parts = []
        for h in self.history:
            parts.append(f"[{h['from']}→{h['to']}]")
        return parts


# ─── PKAP APPLIED TO CURRENCY EQUITY ─────────────────────────────────────────
def pkap_currency_equity(dso: str, fsmp: FSMPScaleAnalysis) -> dict:
    """
    PKAP applied to 360DP currency equity.
    PKAP BODMAS formula adapted for pricing sovereignty.

    Result: ZAR sovereign price for Kopano Labs services.
    Formula:
      base_zar    = target_usd * ZAR_TO_USD
      equity_adj  = base_zar / inequality_ratio  (corrects for structural FOC)
      vip_premium = equity_adj * dso_weight
      final_zar   = max(min_floor_zar, vip_premium)
    """
    dso_weights = {"HDSO": 1.0, "ADSO": 0.7, "PDSO": 0.4, "VIP": 1.5}
    dso_weight  = dso_weights.get(dso, 1.0)

    # Kopano Labs retainer targets (USD reference)
    TARGET_USD_MONTHLY = 500.0      # Entry retainer
    TARGET_USD_PREMIUM = 2000.0     # Premium infrastructure retainer
    MIN_FLOOR_ZAR      = 1_500.0   # Absolute floor — no less than this
    SOVEREIGN_DISCOUNT = 0.60       # 40% equity discount for ZAR market

    # BODMAS chain:
    base_zar_entry   = TARGET_USD_MONTHLY  * ZAR_TO_USD   # 9,210 ZAR
    base_zar_premium = TARGET_USD_PREMIUM  * ZAR_TO_USD   # 36,840 ZAR

    equity_entry     = base_zar_entry   * SOVEREIGN_DISCOUNT * dso_weight
    equity_premium   = base_zar_premium * SOVEREIGN_DISCOUNT * dso_weight

    final_entry      = max(MIN_FLOOR_ZAR, equity_entry)
    final_premium    = max(MIN_FLOOR_ZAR, equity_premium)

    # Equivalent in USD/GBP (what international clients pay — no discount)
    intl_usd_entry   = TARGET_USD_MONTHLY  * dso_weight
    intl_usd_premium = TARGET_USD_PREMIUM  * dso_weight
    intl_gbp_entry   = intl_usd_entry  / (ZAR_TO_USD / ZAR_TO_GBP)
    intl_gbp_premium = intl_usd_premium / (ZAR_TO_USD / ZAR_TO_GBP)

    return {
        "schema":              "pkap_360dp_v1",
        "dso":                 dso,
        "dso_weight":          dso_weight,
        "sovereign_discount":  f"{int(SOVEREIGN_DISCOUNT * 100)}%",

        # ZAR-sovereign pricing (African market)
        "zar_entry_monthly":   round(final_entry,   0),
        "zar_premium_monthly": round(final_premium, 0),

        # International pricing (no discount)
        "usd_entry_monthly":   round(intl_usd_entry,   0),
        "usd_premium_monthly": round(intl_usd_premium, 0),
        "gbp_entry_monthly":   round(intl_gbp_entry,   0),
        "gbp_premium_monthly": round(intl_gbp_premium, 0),

        # Inequality proof
        "zar_to_usd_rate":     ZAR_TO_USD,
        "zar_to_gbp_rate":     ZAR_TO_GBP,
        "inequality_ratio_gbp": fsmp.inequality_ratio_gbp,
        "inequality_ratio_usd": fsmp.inequality_ratio_usd,

        "pkap_mandate": (
            f"ZAR entry: R{final_entry:,.0f}/mo "
            f"vs USD ${intl_usd_entry:,.0f}/mo "
            f"vs GBP £{intl_gbp_entry:,.0f}/mo. "
            f"Same service. {fsmp.inequality_ratio_gbp}x gap. Protocol closes it."
        ),
    }


# ─── 360DP MAIN ENGINE ────────────────────────────────────────────────────────
class ThreeSixtyDP:
    """
    [360DP] — 360 Degrees Protocol
    Full cycle: SENSE → FSMP → VIP → FSNP → PKAP → BMNP → LOG

    Cycle never closes at 359. Must return to 0 = equilibrium.
    Equilibrium = ZAR sovereign pricing + POC evidence + KC Ledger entry.
    """

    def cycle(self, dso: str = "HDSO", domain: str = "GSMB") -> dict:
        ts = datetime.now(timezone.utc).isoformat()

        # ── FSM boot ──────────────────────────────────────────────────
        fsm = FSMNestingProtocol(domain=domain, dso=dso)
        fsm.transition("SENSE", {"source": "IKP_CHAIN", "domain": domain})

        # ── FSMP analysis ─────────────────────────────────────────────
        fsmp = fsmp_analyse()
        fsm.transition("ANALYSE", {
            "fsmp_verdict":      fsmp.fsmp_verdict,
            "inequality_gbp":    fsmp.inequality_ratio_gbp,
            "inequality_usd":    fsmp.inequality_ratio_usd,
            "structural_foc":    fsmp.structural_foc_score,
        })

        # ── VIP tier check ────────────────────────────────────────────
        vip = VIPTier.activate(fsmp)
        fsm.transition("CLASSIFY", {
            "vip_active": vip["vip_active"],
            "dso":        dso,
        })
        effective_dso = "VIP" if vip["vip_active"] else dso

        # ── PKAP formula ──────────────────────────────────────────────
        pkap = pkap_currency_equity(effective_dso, fsmp)
        fsm.transition("ROUTE", {
            "zar_entry":   pkap["zar_entry_monthly"],
            "usd_entry":   pkap["usd_entry_monthly"],
            "gbp_entry":   pkap["gbp_entry_monthly"],
        })

        # ── BMNP nesting ──────────────────────────────────────────────
        nested_trace = fsm.nested_trace()
        bmnp_nest    = f"[360DP[{domain}[{dso}→{effective_dso}[{fsmp.fsmp_verdict}]]]]"

        # ── PERSIST to log (BEFORE building result so it is captured) ──
        _cycle_hash = hashlib.sha256(
            f"{ts}:{domain}:{dso}:{fsmp.fsmp_verdict}".encode()
        ).hexdigest()[:16]
        fsm.transition("PERSIST", {"hash": _cycle_hash})

        result = {
            "schema":         "three_sixty_dp_v1",
            "cycle_ts":       ts,
            "domain":         domain,
            "dso_in":         dso,
            "dso_effective":  effective_dso,
            "fsmp":           fsmp._asdict(),
            "vip":            vip,
            "pkap":           pkap,
            "bmnp_nest":      bmnp_nest,
            "fsm_trace":      nested_trace,
            "fsm_states":     [h["to"] for h in fsm.history],  # PERSIST is now in history
            "fsm_complete":   (fsm.state == "PERSIST"),
            "constraint":     "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "cycle_hash":     _cycle_hash,
        }

        with TDP_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("[360DP] 360 DEGREES PROTOCOL — FSMP CURRENCY EQUITY ANALYSIS")
    print("####!!!! VIP | ZAR → USD/GBP | FSMP UNFAIR SCALE FOR AFRICAN")
    print("=" * 72)

    engine = ThreeSixtyDP()

    print("\n[FSMP] Structural FOC analysis:")
    fsmp = fsmp_analyse()
    print(f"  SA dev:  R{fsmp.sa_dev_hourly_zar}/hr")
    print(f"  UK dev:  R{fsmp.uk_dev_hourly_zar:,.0f}/hr (converted from GBP)")
    print(f"  US dev:  R{fsmp.us_dev_hourly_zar:,.0f}/hr (converted from USD)")
    print(f"  Gap GBP: {fsmp.inequality_ratio_gbp}x")
    print(f"  Gap USD: {fsmp.inequality_ratio_usd}x")
    print(f"  FOC score: {fsmp.structural_foc_score}")
    print(f"  FSMP verdict: {fsmp.fsmp_verdict}")

    print("\n[360DP] Cycling all 4 domains:")
    for domain, dso in [
        ("CAREERS",       "HDSO"),
        ("CRISISCONNECT", "HDSO"),
        ("KASILINK",      "ADSO"),
        ("STARFALL",      "HDSO"),
    ]:
        result = engine.cycle(dso=dso, domain=domain)
        pkap   = result["pkap"]
        vip    = result["vip"]
        print(f"\n  [{domain}] DSO={dso} → effective={result['dso_effective']}")
        print(f"    VIP: {vip['vip_active']} | FSMP: {result['fsmp']['fsmp_verdict']}")
        print(f"    ZAR entry:  R{pkap['zar_entry_monthly']:,.0f}/mo  ← African sovereign price")
        print(f"    USD entry:  ${pkap['usd_entry_monthly']:,.0f}/mo  ← International price")
        print(f"    GBP entry:  £{pkap['gbp_entry_monthly']:,.0f}/mo  ← International price")
        print(f"    mandate:    {pkap['pkap_mandate'][:80]}...")
        print(f"    hash:       {result['cycle_hash']}")
        print(f"    BMNP:       {result['bmnp_nest']}")
        print(f"    FSM trace:  {' → '.join(result['fsm_states'])}")

    print(f"\n[360DP LOG] {TDP_LOG}")
    print("[CONSTRAINT] I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 72)
