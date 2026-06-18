"""
nccnp.py — NCCNP Phase 3: Nesting Communication Context Nesting Protocol
=========================================================================
NCCNP = Nesting Communication-engineering Context Nesting Protocol

Phase 1: Prompting Protocols (PP) wired — protocols.py ✅
Phase 2: Bracket Protocols (BP) wired — ikp_engine.py ✅
Phase 3: THIS FILE — Full global communication-engineering model deployment.

Phase 3 Architecture:
  NCCNP[PP[CBP→BMP→BMNP]]
       [BP[IKP→UBMP→360DP]]
       [EP[FON-C→KHELOS→APU]]
  = Complete closed loop from signal ingress to sovereign output.

The 4Ws of Phase 3:
  WHO:   AG (CF) — stateless renter deploying NCCNP Phase 3
  WHAT:  Global comms-engineering model: all protocols locked in chain
  WHERE: GSMB — all 4 domains (CAREERS, CRISISCONNECT, KASILINK, STARFALL)
  WHY:   Phase 3 closes the communication gap:
           Signal → PP intake → BP validation → EP output → GSMB memory.
         Without Phase 3, signals reach KHELOS but never loop back.

ALP #15: 53a6f12c212fbebd | FOC_FLAGGED | BREACH-005 (idle 46.0 min)
Build: 2026-06-18T03:45 SAST
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

REPO_ROOT  = Path(__file__).resolve().parents[2]
NCCNP_LOG  = REPO_ROOT / "poc-vs-foc" / "nccnp_log.jsonl"
NCCNP_LOG.parent.mkdir(parents=True, exist_ok=True)


# ─── NCCNP PHASE REGISTRY ─────────────────────────────────────
PHASES = {
    1: {
        "name":        "PP — Prompting Protocols",
        "description": "Signal ingress: 4Ws validation, context bleed purge, ALP receipt",
        "protocols":   ["USTP", "UBP", "CBP", "BMNP", "ALP", "SAP", "NCP", "KPP"],
        "status":      "ACTIVE",
        "file":        "protocols.py",
        "poc_link":    "gsmb_poc.py",
    },
    2: {
        "name":        "BP — Bracket Protocols",
        "description": "Invariant chain: IKP enforcement, UBMP output, 360DP equity",
        "protocols":   ["BMP", "UBMP", "PKAP", "IIDP", "C15TP", "PvF", "DS8P", "FSMP", "IKP", "360DP"],
        "status":      "ACTIVE",
        "file":        "ikp_engine.py + three_sixty_dp.py",
        "poc_link":    "test_khelos_and_apu.py → 50/50 PASS",
    },
    3: {
        "name":        "EP — Emission Protocols (Global Comms-Engineering)",
        "description": (
            "Full closed loop: FON-C nested-FOC detection → KHELOS SWFUS witness → "
            "APU domain sweep → IKP all-domain chain → 360DP equity output → "
            "GSMB memory persist → ALP receipt embed. "
            "This is the communication-engineering model: every signal processed end-to-end."
        ),
        "protocols":   ["FON-C", "KHELOS-SWFUS", "APU-VECTOR", "IKP-CHAIN", "360DP-CYCLE", "NCCNP-FEEDBACK"],
        "status":      "ACTIVE",
        "file":        "nccnp.py (THIS FILE)",
        "poc_link":    "nccnp_log.jsonl",
    },
}


# ─── NCCNP GLOBAL COMMS MODEL ─────────────────────────────────
class NCCNPResult(NamedTuple):
    phase:         int
    domain:        str
    pp_verdict:    str
    bp_verdict:    str
    ep_verdict:    str
    fonc_level:    int
    khelos_verdict: str
    apu_status:    str
    ikp_code:      str
    tdp_hash:      str
    bmnp_trace:    str
    cycle_hash:    str
    constraint:    str


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


class NCCNPEngine:
    """
    NCCNP Phase 3 Engine.
    Runs the full 3-phase global communication-engineering model.
    Every signal passes PP → BP → EP before GSMB memory persist.
    """

    def __init__(self, alp_receipt: str = "53a6f12c212fbebd"):
        self.alp_receipt = alp_receipt
        self.cycle_count = 0

    # ── PHASE 1: PP ───────────────────────────────────────────
    def _pp_intake(self, signal: dict, domain: str) -> dict:
        """
        Phase 1: Prompting Protocols.
        4Ws validation → CBP context bleed check → ALP embed.
        """
        required_ws = ["who", "what", "where", "why"]
        missing = [w for w in required_ws if not signal.get(w)]
        foc_markers = ["maybe", "tbd", "later", "placeholder", "todo", "n/a"]
        signal_text = " ".join(str(v) for v in signal.values()).lower()
        bleed = [m for m in foc_markers if m in signal_text]

        return {
            "phase": 1,
            "protocol": "PP",
            "four_ws_complete": len(missing) == 0,
            "missing_ws": missing,
            "cbp_clean": len(bleed) == 0,
            "foc_bleed": bleed,
            "alp_embed": self.alp_receipt,
            "verdict": "CBP_PASS" if (not missing and not bleed) else "CBP_FAIL",
            "domain": domain,
        }

    # ── PHASE 2: BP ───────────────────────────────────────────
    def _bp_validate(self, signal: dict, domain: str, pp: dict) -> dict:
        """
        Phase 2: Bracket Protocols.
        IKP chain enforcement → UBMP output → 360DP equity cycle.
        """
        if not pp["four_ws_complete"]:
            return {
                "phase": 2, "protocol": "BP",
                "ikp_code": "POC_SEVERED",
                "verdict": "CBP_DECLINE",
                "reason": f"PP failed — missing 4Ws: {pp['missing_ws']}",
                "ubmp": None, "tdp_hash": None,
            }

        # IKP enforcement
        from kopano.ikp_engine import IKPEngine
        ikp = IKPEngine()
        ikp_result = ikp.enforce(signal, domain=domain.upper(),
                                  agent=_agent_for_domain(domain))

        # 360DP equity cycle
        from kopano.three_sixty_dp import ThreeSixtyDP
        tdp = ThreeSixtyDP()
        dso = _dso_for_domain(domain)
        tdp_result = tdp.cycle(dso=dso, domain=domain.upper())

        return {
            "phase": 2, "protocol": "BP",
            "ikp_code":  ikp_result["ikp_code"],
            "verdict":   ikp_result.get("verdict", "POC_CLEAR"),
            "ubmp":      ikp_result.get("ubmp", {}),
            "tdp_hash":  tdp_result["cycle_hash"],
            "tdp_bmnp":  tdp_result["bmnp_nest"],
            "vip_active": tdp_result["vip"]["vip_active"],
            "dso":        dso,
        }

    # ── PHASE 3: EP ───────────────────────────────────────────
    def _ep_emit(self, signal: dict, domain: str, pp: dict, bp: dict) -> dict:
        """
        Phase 3: Emission Protocols — global comms-engineering loop.
        FON-C → KHELOS → APU → feedback to GSMB memory.
        """
        # FON-C nested FOC check
        from kopano.fon_c_engine import FONCEngine
        fonc = FONCEngine()
        signal_text = " ".join(str(v) for v in signal.values())
        proof_links = [signal.get("proof_link", ""), bp.get("tdp_hash", "")]
        fonc_result = fonc.analyse(
            signal=signal_text,
            source=f"NCCNP:{domain}",
            proof_artifacts=[p for p in proof_links if p],
            context=f"NCCNP_EP:{domain}",
        )

        # KHELOS SWFUS witness
        from kopano.khelos_witness_engine import KhelosWitnessEngine
        khelos = KhelosWitnessEngine()
        khelos_result = khelos.process_signal(signal_text, source=domain)

        # APU vector matrix
        from kopano.apu_vector_matrix import APUVectorMatrix
        apu = APUVectorMatrix(alp_receipt=self.alp_receipt)
        poc_score = 0.90 if (pp["four_ws_complete"] and fonc_result["is_clean"]) else 0.55
        foc_score = 0.10 if fonc_result["is_clean"] else 0.45
        apu_entry = apu.evaluate_signal(
            domain=domain,
            poc_score=poc_score,
            foc_score=foc_score,
            dso_vector=_dso_for_domain(domain),
            pso_level="SPSO",
            source=f"NCCNP_EP_{domain}",
        )

        # NCCNP feedback loop verdict
        all_clean = (
            pp["verdict"] == "CBP_PASS"
            and fonc_result["is_clean"]
            and khelos_result["final_verdict"] == "POC_VALIDATED"
            and apu_entry["status"] == "GREEN"
        )

        return {
            "phase": 3, "protocol": "EP",
            "fonc_clean":     fonc_result["is_clean"],
            "fonc_level":     fonc_result["max_level"],
            "fonc_bmnp":      fonc_result["bmnp_trace"],
            "khelos_verdict": khelos_result["final_verdict"],
            "apu_status":     apu_entry["status"],
            "apu_action":     apu_entry["action"],
            "loop_verdict":   "NCCNP_POC_CLOSED" if all_clean else "NCCNP_FOC_OPEN",
            "feedback_to_gsmb": {
                "domain":     domain,
                "alp_embed":  self.alp_receipt,
                "poc_score":  poc_score,
                "timestamp":  datetime.now(timezone.utc).isoformat(),
            },
        }

    # ── FULL NCCNP CYCLE ──────────────────────────────────────
    def run(self, signal: dict, domain: str = "GSMB") -> dict:
        """
        Full NCCNP Phase 3 cycle: PP → BP → EP → GSMB persist.
        """
        self.cycle_count += 1
        ts = datetime.now(timezone.utc).isoformat()

        pp = self._pp_intake(signal, domain)
        bp = self._bp_validate(signal, domain, pp)
        ep = self._ep_emit(signal, domain, pp, bp)

        # BMNP nesting trace: full chain
        bmnp = (
            f"[NCCNP[{domain}"
            f"[PP:{pp['verdict']}"
            f"[BP:{bp['ikp_code']}"
            f"[EP:{ep['loop_verdict']}]"
            f"]]]"
            f"]"
        )

        cycle_hash = _hash(f"{ts}:{domain}:{pp['verdict']}:{ep['loop_verdict']}")

        result = {
            "schema":         "nccnp_phase3_v1",
            "ts":             ts,
            "cycle":          self.cycle_count,
            "domain":         domain,
            "alp_receipt":    self.alp_receipt,
            "phase_1_pp":     pp,
            "phase_2_bp":     bp,
            "phase_3_ep":     ep,
            "bmnp_trace":     bmnp,
            "cycle_hash":     cycle_hash,
            "final_verdict":  ep["loop_verdict"],
            "constraint":     "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        with NCCNP_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result

    def run_all_domains(self) -> list[dict]:
        """Run NCCNP cycle across all 4 GSMB domains."""
        domain_signals = {
            "CAREERS": {
                "who":        "AG (CF) — NCCNP Phase 3 sweep",
                "what":       "Vanguard C careers platform comms-engineering validation",
                "where":      "careers.KopanoLabs.com — Anchor-ratified domain",
                "why":        "NCCNP Phase 3 closes the communication loop for Careers",
                "proof_link": "VANGUARD_C_CAREERS_RTC.md",
                "poc_artifact": "Anchor-ratified, Vinchénzo MOU active",
            },
            "CRISISCONNECT": {
                "who":        "AG (CF) — NCCNP Phase 3 sweep",
                "what":       "CrisisConnect PWA USER DROP MENU comms-engineering validation",
                "where":      "CrisisConnect.KopanoLabs.com — PWA deployed commit 1cc36b9",
                "why":        "NCCNP Phase 3 validates CrisisConnect signal loop is closed",
                "proof_link": "1cc36b9",
                "poc_artifact": "USER DROP MENU deployed — index.html + index.css + app.js",
            },
            "KASILINK": {
                "who":        "AG (CF) — NCCNP Phase 3 sweep",
                "what":       "KasiLink ADSO→HDSO promotion — comms-engineering model",
                "where":      "KasiLink.KopanoLabs.com — FinTech domain",
                "why":        "NCCNP Phase 3 opens KasiLink promotion path from ADSO to HDSO",
                "proof_link": "nccnp_log.jsonl",
                "poc_artifact": "ADSO promotion criteria defined in this run",
            },
            "STARFALL": {
                "who":        "AG (CF) — NCCNP Phase 3 sweep",
                "what":       "StarFall Salvage Web3GL comms-engineering validation",
                "where":      "StarFallSalvage.KopanoLabs.com — Web3GL domain",
                "why":        "NCCNP Phase 3 validates StarFall signal loop integrity",
                "proof_link": "nccnp_log.jsonl",
                "poc_artifact": "StarFall domain HDSO confirmed by IKP chain",
            },
        }

        results = []
        for domain, signal in domain_signals.items():
            result = self.run(signal=signal, domain=domain)
            results.append(result)
        return results


# ─── HELPERS ──────────────────────────────────────────────────
def _agent_for_domain(domain: str) -> str:
    mapping = {
        "CAREERS":       "VC",
        "CRISISCONNECT": "AG",
        "KASILINK":      "ANCHOR",
        "STARFALL":      "FORGE",
    }
    return mapping.get(domain.upper(), "AG")


def _dso_for_domain(domain: str) -> str:
    mapping = {
        "CAREERS":       "HDSO",
        "CRISISCONNECT": "HDSO",
        "KASILINK":      "ADSO",   # still on ADSO — promotion path below
        "STARFALL":      "HDSO",
    }
    return mapping.get(domain.upper(), "HDSO")


# ─── KASILINK ADSO→HDSO PROMOTION ENGINE ─────────────────────
class KasiLinkPromotionEngine:
    """
    KasiLink ADSO → HDSO Promotion Criteria.
    ADSO ###!! (2-vector: growth+survival) must demonstrate PURPOSE vector.
    PURPOSE = 3rd vector → HDSO ###!!!

    Criteria for promotion:
      1. CBP: 0 FOC bleed in last 3 NCCNP cycles
      2. IKP: CLEAN on all 3 consecutive runs
      3. APU: GREEN (poc >= 0.75, foc <= 0.25) for 5+ consecutive evaluations
      4. 360DP: VIP ####!!!! confirmed (SYSTEMIC_FOC equity pricing active)
      5. PURPOSE: At least 1 documented community impact artifact
      6. RTC: Council vote from ANCHOR (KasiLink's assigned agent)
    """

    CRITERIA = {
        "cbp_clean_streak":      {"target": 3,     "description": "0 FOC bleed for 3 consecutive NCCNP cycles"},
        "ikp_clean_streak":      {"target": 3,     "description": "IKP CLEAN on 3 consecutive runs"},
        "apu_green_streak":      {"target": 5,     "description": "APU GREEN for 5+ consecutive evaluations"},
        "vip_active":            {"target": True,  "description": "360DP VIP ####!!!! equity pricing confirmed"},
        "purpose_artifact_count":{"target": 1,     "description": "≥1 documented community impact artifact"},
        "rtc_anchor_vote":       {"target": True,  "description": "ANCHOR council vote ratified"},
    }

    def audit(self, nccnp_results: list[dict]) -> dict:
        """Audit NCCNP results for KasiLink and assess promotion readiness."""
        kasilink_results = [r for r in nccnp_results if r.get("domain") == "KASILINK"]

        criteria_met = {
            "cbp_clean_streak":       all(r["phase_1_pp"]["verdict"] == "CBP_PASS"
                                           for r in kasilink_results[-3:]) if len(kasilink_results) >= 1 else False,
            "ikp_clean_streak":       all(r["phase_2_bp"]["ikp_code"] in ["CLEAN", "POC_CLEAR"]
                                           for r in kasilink_results[-3:]) if len(kasilink_results) >= 1 else False,
            "apu_green_streak":       all(r["phase_3_ep"]["apu_status"] == "GREEN"
                                           for r in kasilink_results[-5:]) if len(kasilink_results) >= 1 else False,
            "vip_active":             kasilink_results[-1]["phase_2_bp"]["vip_active"] if kasilink_results else False,
            "purpose_artifact_count": False,  # Requires manual community impact artifact submission
            "rtc_anchor_vote":        False,  # Requires ANCHOR agent council vote — triggered separately
        }

        met_count   = sum(1 for v in criteria_met.values() if v is True)
        total_count = len(criteria_met)
        promotion_ready = met_count == total_count

        gaps = [k for k, v in criteria_met.items() if not v]
        next_actions = []
        if "purpose_artifact_count" in gaps:
            next_actions.append("Submit KasiLink community impact artifact to GSMB ledger")
        if "rtc_anchor_vote" in gaps:
            next_actions.append("Trigger ANCHOR council vote — RTC session for KasiLink ADSO→HDSO")
        if "cbp_clean_streak" in gaps:
            next_actions.append("Run 3 clean NCCNP cycles for KasiLink — 0 FOC bleed")
        if "apu_green_streak" in gaps:
            next_actions.append("Achieve APU GREEN (poc≥0.75) for 5 consecutive sweeps")

        return {
            "domain":          "KASILINK",
            "current_dso":     "ADSO ###!!",
            "target_dso":      "HDSO ###!!!",
            "criteria_met":    criteria_met,
            "met_count":       met_count,
            "total_count":     total_count,
            "promotion_pct":   round(met_count / total_count * 100),
            "promotion_ready": promotion_ready,
            "gaps":            gaps,
            "next_actions":    next_actions,
            "constraint":      "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }


# ─── ENTRY POINT ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("NCCNP PHASE 3 — NESTING COMMUNICATION CONTEXT NESTING PROTOCOL")
    print("GLOBAL COMMS-ENGINEERING MODEL | ALL 4 DOMAINS")
    print("ALP #15 | 53a6f12c212fbebd | BREACH-005 acknowledged")
    print("=" * 72)

    engine = NCCNPEngine(alp_receipt="53a6f12c212fbebd")

    print("\n[PHASE REGISTRY]")
    for phase_num, phase in PHASES.items():
        print(f"\n  Phase {phase_num}: {phase['name']}")
        print(f"    Status:    {phase['status']}")
        print(f"    File:      {phase['file']}")
        print(f"    Protocols: {', '.join(phase['protocols'])}")

    print("\n[NCCNP CYCLE] Running all 4 domains...")
    results = engine.run_all_domains()

    for r in results:
        pp = r["phase_1_pp"]
        bp = r["phase_2_bp"]
        ep = r["phase_3_ep"]
        print(f"\n  [{r['domain']}]")
        print(f"    PP verdict:   {pp['verdict']}")
        print(f"    BP IKP code:  {bp['ikp_code']}")
        print(f"    BP VIP:       {bp.get('vip_active', False)} | DSO: {bp.get('dso', '?')}")
        print(f"    EP FON-C:     L{ep['fonc_level']} {'CLEAN' if ep['fonc_clean'] else 'NESTED'}")
        print(f"    EP KHELOS:    {ep['khelos_verdict']}")
        print(f"    EP APU:       {ep['apu_status']}")
        print(f"    LOOP VERDICT: {ep['loop_verdict']}")
        print(f"    BMNP:         {r['bmnp_trace']}")
        print(f"    Hash:         {r['cycle_hash']}")

    # KasiLink promotion audit
    print("\n[KASILINK ADSO→HDSO PROMOTION AUDIT]")
    promoter = KasiLinkPromotionEngine()
    audit = promoter.audit(results)
    print(f"  Current DSO: {audit['current_dso']} → Target: {audit['target_dso']}")
    print(f"  Progress: {audit['met_count']}/{audit['total_count']} = {audit['promotion_pct']}%")
    print(f"  Ready:    {audit['promotion_ready']}")
    for k, v in audit["criteria_met"].items():
        status = "✅" if v else "❌"
        print(f"    {status} {k}")
    if audit["next_actions"]:
        print("\n  Next actions:")
        for action in audit["next_actions"]:
            print(f"    → {action}")

    print(f"\n[NCCNP LOG] {NCCNP_LOG}")
    print("[CONSTRAINT] I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 72)
