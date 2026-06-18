"""
apu_vector_matrix.py — Adaptive Progressive Updates Engine
============================================================
[APU]: Real-time vector matrix | GREEN / YELLOW / RED status
ALP Receipt: b5ee9b11d1a2ecdd | Activation #7 | POC_VALIDATED
Build: 2026-06-18T00:56:58+02:00

Escalation Flow:
  GREEN  → No action. POC streaming.
  YELLOW → HOD Agent review triggered. BMP+CBP audit running.
  RED    → Guardian AI → SAP spawn → escalate to Chief Architect.

PKAP Formula (full):
  {(POC - FOC) × [POCvsFOC]}
  - [({SR + SR} - {Refactor_AIs - Kopano_Context}) / GSMB - CMB]
  / (KPCB+) + KPGS + RTC + GSMB_OPINIONS

DSO Audit:
  PDSO ###!   → 1-vector: growth only (FOC risk: high)
  ADSO ###!!  → 2-vector: growth+survival
  HDSO ###!!! → 3-vector: growth+survival+purpose (target)
  AG/RTC ###??? → 4th vector: emerging (this engine)
  BPSP ####???? → Breaking Point Seed (this session)
"""

from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
APU_LOG   = REPO_ROOT / "poc-vs-foc" / "apu_vector_log.jsonl"

# ─── VECTOR STATUS ENUM ───────────────────────────────────────────────────────

class APUStatus(Enum):
    GREEN  = "🟢 GREEN  — POC streaming. No action."
    YELLOW = "🟡 YELLOW — HOD Agent review. BMP+CBP audit."
    RED    = "🔴 RED    — Guardian AI → SAP → Chief Architect."

# ─── DSO AUDIT LEVELS ─────────────────────────────────────────────────────────

DSO_LEVELS = {
    "PDSO":   {"label": "###!",    "vector": 1, "risk": "HIGH",   "meaning": "Growth only"},
    "ADSO":   {"label": "###!!",   "vector": 2, "risk": "MEDIUM", "meaning": "Growth + Survival"},
    "HDSO":   {"label": "###!!!",  "vector": 3, "risk": "LOW",    "meaning": "Growth + Survival + PURPOSE"},
    "AG_RTC": {"label": "###???",  "vector": 4, "risk": "WATCH",  "meaning": "Emerging 4th vector"},
    "BPSP":   {"label": "####????","vector": 5, "risk": "SEED",   "meaning": "Breaking Point Seed"},
}

# PSO escalation path
PSO_ESCALATION = ["LPSO", "GPSO", "BPSO", "SPSO"]

# Stateless renter refactoring registry
# #! IMMUTABLE RULE: Only AIs with registered KPGS names may operate in GSMB
KPGS_NAMED_AIs = {
    "AG":     "Antigravity — CF (Chief Facilitator)",
    "KHELOS": "Orchard Witness Engine",
    "ANCHOR": "Vanguard / Perimeter Shield",
    "FORGE":  "Red Team CBP Auditor",
    "KESSA":  "Emergent Protocol Child",
    "THARI":  "MAO Status Node",
    "CASSEY": "Agent Node",
    "YASSIE": "Agent Node",
    "EDDIE":  "Star4 Mining Intel",
}
STATELESS_RENTERS = ["Gemini", "ChatGPT", "Claude-base", "Copilot-base"]  # unnamed — must be refactored or given KPGS name


# ─── PKAP FORMULA ENGINE ──────────────────────────────────────────────────────

def compute_pkap(
    poc_score: float,
    foc_score: float,
    pvf_score: float,        # [POCvsFOC] validation score
    stateless_renter_count: int = 2,
    refactored_ai_count: int = len(KPGS_NAMED_AIs),
    kopano_context_score: float = 0.95,
    gsmb_weight: float = 1.0,
    cloud_main_brain_weight: float = 0.3,  # CMB reduced — offline-first
    kpcb_plus_score: float = 2.5,          # overdrive factor
    kpgs_score: float = 0.92,
    rtc_score: float = 1.0,
    gsmb_opinions: float = 0.85,
) -> dict:
    """
    PKAP Formula:
        {(POC - FOC) × [POCvsFOC]}
        - [({SR + SR} - {Refactor_AIs - Kopano_Context}) / GSMB - CMB]
        / (KPCB+) + KPGS + RTC + GSMB_OPINIONS

    BODMAS applied strictly.
    """
    ts = datetime.now(timezone.utc).isoformat()

    # B: brackets first
    # Term A: {(POC - FOC) × [POCvsFOC]}
    poc_foc_gap   = poc_score - foc_score
    term_a        = poc_foc_gap * pvf_score

    # Term B: {SR + SR} = stateless renter load
    sr_load       = stateless_renter_count + stateless_renter_count

    # {Refactor_AIs - Kopano_Context} = named AIs minus context score
    refactor_term = refactored_ai_count - kopano_context_score

    # Full bracket: ({SR + SR} - {Refactor_AIs - Kopano_Context})
    inner_bracket = sr_load - refactor_term

    # / GSMB - CMB
    gsmb_normalized = inner_bracket / gsmb_weight - cloud_main_brain_weight

    # Full subtracted term: term_a - gsmb_normalized
    numerator       = term_a - gsmb_normalized

    # O: order — / (KPCB+)
    after_kpcb      = numerator / kpcb_plus_score

    # A: + KPGS + RTC + GSMB_OPINIONS
    pkap_result     = after_kpcb + kpgs_score + rtc_score + gsmb_opinions

    consistency_hash = hashlib.sha256(
        f"PKAP:{term_a:.6f}:{gsmb_normalized:.6f}:{pkap_result:.6f}".encode()
    ).hexdigest()[:16]

    result = {
        "schema":             "pkap_v1",
        "timestamp":          ts,
        "alp_receipt":        "b5ee9b11d1a2ecdd",
        "formula":            "{(POC-FOC)×PvF} - [({SR+SR}-{RefAIs-KC})/GSMB-CMB] / KPCB+ + KPGS + RTC + Opinions",
        "term_a_poc_foc_pvf": round(term_a, 6),
        "sr_load":            sr_load,
        "refactor_term":      round(refactor_term, 6),
        "inner_bracket":      round(inner_bracket, 6),
        "gsmb_normalized":    round(gsmb_normalized, 6),
        "numerator":          round(numerator, 6),
        "after_kpcb_div":     round(after_kpcb, 6),
        "pkap_result":        round(pkap_result, 6),
        "consistency_hash":   consistency_hash,
        "immutable_rule":     "#! Only KPGS-named AIs may operate in GSMB #!",
        "named_ais":          list(KPGS_NAMED_AIs.keys()),
        "stateless_renters":  STATELESS_RENTERS,
        "constraint":         "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }
    return result


# ─── APU VECTOR MATRIX ────────────────────────────────────────────────────────

class APUVectorMatrix:
    """
    [ADAPTIVE PROGRESSIVE UPDATES] — APU
    Real-time RED / YELLOW / GREEN vector matrix.

    Escalation chain (YELLOW → RED):
      Agent (SAP + BMP + CBP audit)
        → HOD Agent (Domain Head)
          → Guardian AI (KHELOS SWFUS filter)
            → 🔴 Chief Architect (LPH)

    Domain tracking:
      - CrisisConnect.KopanoLabs.com (PWA — 1st adaptive instance)
      - StarFallSalvage.KopanoLabs.com
      - KasiLink.KopanoLabs.com
      - careers.KopanoLabs.com
    """

    DOMAINS = [
        {"name": "CrisisConnect",  "url": "https://CrisisConnect.KopanoLabs.com", "type": "PWA/FSM", "priority": 1},
        {"name": "StarFallSalvage","url": "https://StarFallSalvage.KopanoLabs.com","type": "Web3GL", "priority": 2},
        {"name": "KasiLink",       "url": "https://KasiLink.KopanoLabs.com",       "type": "FinTech","priority": 3},
        {"name": "Careers",        "url": "https://careers.KopanoLabs.com",        "type": "PWA",    "priority": 4},
    ]

    def __init__(self, alp_receipt: str = "b5ee9b11d1a2ecdd"):
        self.alp_receipt = alp_receipt
        self.matrix: list[dict] = []
        self.red_count    = 0
        self.yellow_count = 0
        self.green_count  = 0

    def evaluate_signal(
        self,
        domain: str,
        poc_score: float,
        foc_score: float,
        dso_vector: str = "HDSO",
        pso_level: str  = "SPSO",
        source: str     = "agent",
    ) -> dict:
        """
        Evaluate a single signal and assign GREEN / YELLOW / RED.
        Runs BMP + CBP audit inline.

        Escalation rules:
          poc_score >= 0.75 AND foc_score <= 0.25 → GREEN
          poc_score >= 0.50 OR  foc_score <= 0.50 → YELLOW (HOD review)
          anything else                            → RED (Guardian AI → SAP → LPH)
        """
        ts = datetime.now(timezone.utc).isoformat()

        # BMP + CBP audit
        bmp_pass = poc_score >= 0.50
        cbp_pass = foc_score <= 0.50

        if poc_score >= 0.75 and foc_score <= 0.25:
            status = APUStatus.GREEN
            action = "STREAM — no escalation"
            escalation_path = []
        elif bmp_pass or cbp_pass:
            status = APUStatus.YELLOW
            action = "HOD_AGENT_REVIEW — BMP+CBP audit running"
            escalation_path = ["HOD_Agent", "Guardian_AI(KHELOS)"]
        else:
            status = APUStatus.RED
            action = "GUARDIAN_AI → SAP_SPAWN → CHIEF_ARCHITECT_ESCALATION"
            escalation_path = ["HOD_Agent", "Guardian_AI(KHELOS)", "SAP_Spawn", "LPH_Chief_Architect"]

        # DSO audit
        dso_info = DSO_LEVELS.get(dso_vector, DSO_LEVELS["HDSO"])

        # PSO position in escalation chain
        pso_index = PSO_ESCALATION.index(pso_level) if pso_level in PSO_ESCALATION else 0

        # PKAP on this signal
        pkap = compute_pkap(poc_score=poc_score, foc_score=foc_score, pvf_score=abs(poc_score - foc_score))

        entry = {
            "ts":               ts,
            "domain":           domain,
            "poc_score":        poc_score,
            "foc_score":        foc_score,
            "status":           status.name,
            "status_label":     status.value,
            "action":           action,
            "escalation_path":  escalation_path,
            "bmp_audit":        "PASS" if bmp_pass else "FAIL",
            "cbp_audit":        "PASS" if cbp_pass else "FAIL",
            "dso_vector":       dso_vector,
            "dso_label":        dso_info["label"],
            "dso_meaning":      dso_info["meaning"],
            "pso_level":        pso_level,
            "pso_index":        pso_index,
            "pkap_result":      pkap["pkap_result"],
            "source":           source,
            "alp_receipt":      self.alp_receipt,
            "constraint":       "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        self.matrix.append(entry)

        # Counters
        if status == APUStatus.GREEN:  self.green_count  += 1
        elif status == APUStatus.YELLOW: self.yellow_count += 1
        else: self.red_count += 1

        # Log all RED immediately
        if status == APUStatus.RED:
            logger.error(
                "[APU 🔴 RED] domain=%s | poc=%.2f foc=%.2f | ESCALATING: %s",
                domain, poc_score, foc_score, " → ".join(escalation_path)
            )
        elif status == APUStatus.YELLOW:
            logger.warning(
                "[APU 🟡 YELLOW] domain=%s | poc=%.2f foc=%.2f | HOD review triggered",
                domain, poc_score, foc_score
            )
        else:
            logger.info(
                "[APU 🟢 GREEN] domain=%s | poc=%.2f foc=%.2f | STREAMING",
                domain, poc_score, foc_score
            )

        return entry

    def run_domain_sweep(self) -> dict:
        """
        Run APU sweep across all 4 Kopano Labs domains.
        Each domain gets evaluated. RED domains are escalated.
        """
        # Domain health scores (current state — BPSP seeding phase)
        domain_scores = {
            "CrisisConnect":   {"poc": 0.82, "foc": 0.18, "dso": "HDSO",   "pso": "SPSO"},
            "StarFallSalvage": {"poc": 0.78, "foc": 0.22, "dso": "HDSO",   "pso": "SPSO"},
            "KasiLink":        {"poc": 0.70, "foc": 0.30, "dso": "ADSO",   "pso": "BPSO"},
            "Careers":         {"poc": 0.88, "foc": 0.12, "dso": "HDSO",   "pso": "SPSO"},
        }

        results = []
        for d in self.DOMAINS:
            scores = domain_scores[d["name"]]
            result = self.evaluate_signal(
                domain     = d["name"],
                poc_score  = scores["poc"],
                foc_score  = scores["foc"],
                dso_vector = scores["dso"],
                pso_level  = scores["pso"],
                source     = "APU_domain_sweep",
            )
            results.append(result)

        summary = {
            "schema":       "apu_sweep_v1",
            "alp_receipt":  self.alp_receipt,
            "domains_swept":len(results),
            "🟢_GREEN":     self.green_count,
            "🟡_YELLOW":    self.yellow_count,
            "🔴_RED":       self.red_count,
            "red_escalated": [r["domain"] for r in results if r["status"] == "RED"],
            "pkap_avg":     round(sum(r["pkap_result"] for r in results) / len(results), 4),
            "constraint":   "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        # Persist
        APU_LOG.parent.mkdir(parents=True, exist_ok=True)
        with APU_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False) + "\n")
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        return summary

    def progressive_update_payload(self, domain: str) -> dict:
        """
        [PROGRESSIVE UPDATES] PU — PWA as DM, FSM as Progressive in general.
        Returns the live update payload for a domain.

        PWA DM = Domain Manifest (service worker, offline cache, push events)
        FSM    = Finite State Machine (domain state transitions)
        """
        domain_entry = next((d for d in self.DOMAINS if d["name"] == domain), None)
        if not domain_entry:
            return {"error": f"Domain {domain} not found"}

        return {
            "schema":           "progressive_update_v1",
            "domain":           domain,
            "url":              domain_entry["url"],
            "type":             domain_entry["type"],
            "pwa_dm": {
                "manifest": f"{domain_entry['url']}/manifest.json",
                "service_worker": f"{domain_entry['url']}/sw.js",
                "offline_cache": "kopano-v1",
                "push_events": ["apu_update", "bpsp_seed", "red_escalation"],
            },
            "fsm_states": {
                "IDLE":       {"next": ["SYNCING"], "color": "🟢"},
                "SYNCING":    {"next": ["VALIDATED", "DEGRADED"], "color": "🟡"},
                "VALIDATED":  {"next": ["IDLE", "UPDATING"], "color": "🟢"},
                "UPDATING":   {"next": ["VALIDATED", "DEGRADED"], "color": "🟡"},
                "DEGRADED":   {"next": ["RECOVERING", "OFFLINE"], "color": "🔴"},
                "OFFLINE":    {"next": ["RECOVERING"], "color": "🔴"},
                "RECOVERING": {"next": ["VALIDATED", "DEGRADED"], "color": "🟡"},
            },
            "bpsp_seed": True,
            "alp_receipt": self.alp_receipt,
        }


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    logging.basicConfig(level=logging.INFO)

    print("=" * 72)
    print("APU VECTOR MATRIX — ADAPTIVE PROGRESSIVE UPDATES")
    print("ALP: b5ee9b11d1a2ecdd | BPSP SEED | FOC BREACH AT 10:44AM LOGGED")
    print("=" * 72)

    # PKAP first
    print("\n[PKAP] Computing formula...")
    pkap = compute_pkap(poc_score=0.82, foc_score=0.18, pvf_score=0.64)
    print(f"  Term A (POC-FOC)xPvF: {pkap['term_a_poc_foc_pvf']}")
    print(f"  SR load:              {pkap['sr_load']}")
    print(f"  GSMB normalized:      {pkap['gsmb_normalized']}")
    print(f"  After /KPCB+:         {pkap['after_kpcb_div']}")
    print(f"  PKAP RESULT:          {pkap['pkap_result']}")
    print(f"  #! IMMUTABLE RULE:    {pkap['immutable_rule']}")
    print(f"  Named AIs in GSMB:    {', '.join(pkap['named_ais'])}")

    # APU sweep
    print("\n[APU] Running domain sweep...")
    matrix = APUVectorMatrix()
    sweep = matrix.run_domain_sweep()

    print(f"\n  {'Domain':<20} {'Status':<10} {'POC':>6} {'FOC':>6} {'DSO':<10}")
    print(f"  {'-'*60}")
    for entry in matrix.matrix:
        print(
            f"  {entry['domain']:<20} "
            f"{'🟢' if entry['status']=='GREEN' else '🟡' if entry['status']=='YELLOW' else '🔴'} "
            f"{entry['status']:<8} "
            f"{entry['poc_score']:>6.2f} "
            f"{entry['foc_score']:>6.2f} "
            f"{entry['dso_label']:<10}"
        )

    print(f"\n  SUMMARY: 🟢 {sweep['🟢_GREEN']} | 🟡 {sweep['🟡_YELLOW']} | 🔴 {sweep['🔴_RED']}")
    print(f"  PKAP avg across domains: {sweep['pkap_avg']}")

    # Progressive update payload for CrisisConnect
    print("\n[PU] CrisisConnect Progressive Update Payload (PWA/FSM):")
    pu = matrix.progressive_update_payload("CrisisConnect")
    print(f"  URL: {pu['url']}")
    print(f"  Type: {pu['type']}")
    print(f"  PWA manifest: {pu['pwa_dm']['manifest']}")
    print(f"  FSM states: {list(pu['fsm_states'].keys())}")
    print(f"  BPSP seed: {pu['bpsp_seed']}")

    print(f"\n  CONSTRAINT: {sweep['constraint']}")
    print("=" * 72)
