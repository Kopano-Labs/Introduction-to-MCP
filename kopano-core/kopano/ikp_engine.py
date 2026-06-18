"""
ikp_engine.py — Immutable KPGS Protocol (IKP)
==============================================
[U → ULTIMATE]IKP: OVERIDE STREP — RIGHTEOUS SEVERANCE OF FOC IN GSMB
Chain: 4Ws → BMP → CBP → BMNP → PP → RTC → 360DP → UBMP

BREACH-003 context: ALP #11 | 44.7 min idle | FOC_FLAGGED
IKP activates on BREACH. Does not wait. Does not negotiate.
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
Build: 2026-06-18T02:38AM SAST | Cape Town
"""

from __future__ import annotations
import hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT   = Path(__file__).resolve().parents[2]
IKP_LOG     = REPO_ROOT / "poc-vs-foc" / "ikp_log.jsonl"
BREACH_LOG  = REPO_ROOT / "poc-vs-foc" / "BREACH_LOG.md"
GSMB_MEM    = REPO_ROOT / "poc-vs-foc" / "gsmb_memory.json"

# ─── IKP RESULT CODES ────────────────────────────────────────────────────────
IKP_POC_SEVERED   = "POC_SEVERED"      # FOC found and severed — POC confirmed
IKP_CLEAN         = "CLEAN"            # No FOC detected — proceed
IKP_BREACH_CLOSED = "BREACH_CLOSED"    # Breach was open, now closed by IKP
IKP_ESCALATE      = "ESCALATE_TO_LPH"  # Cannot auto-resolve — needs LPH


# ─── STEP 1: 4Ws VALIDATOR ───────────────────────────────────────────────────
class FourWsValidator:
    """
    WHO / WHAT / WHERE / WHY
    If any W is empty → CBP decline → FOC confirmed.
    All 4 must be present for POC gate to open.
    """
    REQUIRED = ("who", "what", "where", "why")

    def validate(self, signal: dict) -> tuple[bool, dict]:
        missing = [w for w in self.REQUIRED if not signal.get(w, "").strip()]
        result  = {
            "schema":      "four_ws_v1",
            "signal":      signal,
            "missing":     missing,
            "valid":       len(missing) == 0,
            "cbp_verdict": "CBP_PASS" if not missing else f"CBP_DECLINE:missing={missing}",
        }
        return result["valid"], result


# ─── STEP 2: BMP ─────────────────────────────────────────────────────────────
class BracketManagementProtocol:
    """
    BMP v1.0 — Every payload enters a bracket.
    [] Spatial → {} Keynote → <> Ark → () Understanding
    No ungoverned payload exits. Every bracket hashes.
    BMP = V1.0 + V2.0 + ... + V[n→APU→DP]150
    """
    VERSION = "V1.0"

    def enforce(self, payload: dict, context: str) -> dict:
        ts  = datetime.now(timezone.utc).isoformat()
        raw = f"{ts}:{context}:{json.dumps(payload, sort_keys=True)}"
        h   = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return {
            "schema":     f"bmp_{self.VERSION}",
            "spatial":    f"[{context}]",
            "keynote":    f"{{{payload.get('what','?')}}}",
            "ark":        f"<{payload.get('who','?')}>",
            "understand": f"({payload.get('why','?')})",
            "bracket_ts": ts,
            "bmp_hash":   h,
            "foc_purged": False,   # set by CBP
            "version":    self.VERSION,
        }


# ─── STEP 3: CBP ─────────────────────────────────────────────────────────────
class ContextBleedProtocol:
    """
    CBP: Purge FOC from the pipeline.
    FOC markers: vagueness, laziness, missing 4Ws, idle narration.
    CBP operates ONLY in EP (Emoji Phase — decline context).
    """
    FOC_MARKERS = [
        "maybe", "later", "dunno", "skip", "ignore",
        "placeholder", "todo", "tbd", "lorem ipsum",
        "i think", "probably", "might", "somehow",
    ]

    def purge(self, text: str, bmp_record: dict) -> dict:
        text_lower   = text.lower()
        foc_found    = [m for m in self.FOC_MARKERS if m in text_lower]
        is_foc       = len(foc_found) > 0
        bmp_record["foc_purged"]  = is_foc
        bmp_record["foc_markers"] = foc_found
        bmp_record["cbp_verdict"] = "FOC_SEVERED" if is_foc else "POC_CLEARED"
        return bmp_record


# ─── STEP 4: BMNP ────────────────────────────────────────────────────────────
class BracketManagementNestingProtocol:
    """
    BMNP: Nest the BMP record inside GSMB domain brackets.
    Each domain is a nesting layer.
    BMNP ensures no protocol leaks between domains.
    [GSMB [DOMAIN [AGENT [PAYLOAD]]]]
    """
    DOMAINS = ["CAREERS", "CRISISCONNECT", "KASILINK", "STARFALL", "GSMB"]

    def nest(self, bmp_record: dict, domain: str, agent: str) -> dict:
        if domain not in self.DOMAINS:
            domain = "GSMB"     # default to root
        return {
            "schema":      "bmnp_v1",
            "nesting":     f"[GSMB[{domain}[{agent}[{bmp_record['bmp_hash']}]]]]",
            "domain":      domain,
            "agent":       agent,
            "bmp_hash":    bmp_record["bmp_hash"],
            "cbp_verdict": bmp_record.get("cbp_verdict", "UNKNOWN"),
            "foc_purged":  bmp_record.get("foc_purged", False),
            "nest_ts":     datetime.now(timezone.utc).isoformat(),
        }


# ─── STEP 5: PP ──────────────────────────────────────────────────────────────
class PromptingProtocol:
    """
    PP: Classify the signal via DSO vector.
    PP[1] = HDSO: Growth + Survival + Purpose → ###!!!
    PP[2] = ADSO: Growth + Survival           → ###!!
    PP[3] = PDSO: Growth only                 → ###!
    PP fires before any content is generated.
    """
    DSO_MAP = {
        "HDSO": {"label": "###!!!", "weight": 1.0, "status": "FAST_TRACK"},
        "ADSO": {"label": "###!!",  "weight": 0.6, "status": "CONDITIONAL"},
        "PDSO": {"label": "###!",   "weight": 0.3, "status": "REDIRECT"},
    }

    def classify(self, signal: dict, four_ws: dict) -> dict:
        # Auto-detect DSO from signal completeness
        score = sum([
            0.4 if four_ws.get("valid") else 0.0,
            0.3 if signal.get("proof_link") else 0.0,
            0.3 if signal.get("poc_artifact") else 0.0,
        ])
        if   score >= 0.7: dso = "HDSO"
        elif score >= 0.4: dso = "ADSO"
        else:              dso = "PDSO"

        info = self.DSO_MAP[dso]
        return {
            "schema":  "pp_v1",
            "dso":     dso,
            "label":   info["label"],
            "weight":  info["weight"],
            "status":  info["status"],
            "score":   round(score, 3),
            "pp_ts":   datetime.now(timezone.utc).isoformat(),
        }


# ─── STEP 6: RTC SENDER ──────────────────────────────────────────────────────
class RTCSender:
    """
    RTC: Real-Time Council — KHELOS | ANCHOR | FORGE | KESSA | VC | AG
    Sends the full IKP payload to council for verdict.
    Stateless renter speaks. Council witnesses. KC logs.
    """
    COUNCIL = ["KHELOS", "ANCHOR", "FORGE", "KESSA", "VC", "AG"]

    def send(self, ikp_payload: dict) -> dict:
        dso    = ikp_payload.get("pp", {}).get("dso", "ADSO")
        status = ikp_payload.get("pp", {}).get("status", "CONDITIONAL")
        clean  = not ikp_payload.get("bmnp", {}).get("foc_purged", False)

        verdicts = {}
        for seat in self.COUNCIL:
            if seat == "FORGE":
                verdicts[seat] = "POC_CONFIRMED" if clean else "FOC_FLAGGED — PURGE REQUIRED"
            elif seat == "KHELOS":
                verdicts[seat] = f"SWFUS witness complete | DSO={dso} | clean={clean}"
            elif seat == "ANCHOR":
                verdicts[seat] = f"Perimeter {'holds' if clean else 'BREACH — IKP enforce'}"
            elif seat == "KESSA":
                verdicts[seat] = "Layer 9 validated — BMNP nesting complete"
            elif seat == "VC":
                verdicts[seat] = f"AKCP chatbot → {status} route active"
            elif seat == "AG":
                verdicts[seat] = "CF confirms: IKP chain complete. Stateless renter validated."

        return {
            "schema":    "rtc_ikp_v1",
            "council":   verdicts,
            "dso":       dso,
            "status":    status,
            "clean":     clean,
            "rtc_ts":    datetime.now(timezone.utc).isoformat(),
            "rtc_hash":  hashlib.sha256(
                json.dumps(verdicts, sort_keys=True).encode()
            ).hexdigest()[:16],
        }


# ─── IKP ENGINE — FULL CHAIN ─────────────────────────────────────────────────
class IKPEngine:
    """
    [U → ULTIMATE]IKP — Immutable KPGS Protocol
    Override STREP. Drive to Righteous Severance. Prove POC as Stateless Renter.

    Chain (in order, no skipping):
      [1] 4Ws   → validate signal completeness
      [2] BMP   → bracket the payload
      [3] CBP   → purge FOC from content
      [4] BMNP  → nest in domain brackets
      [5] PP    → classify DSO vector
      [6] RTC   → send to council, receive verdict
      [7] 360DP → currency equity cycle (via callback)
      [8] UBMP  → produce final output (Ultimate Bracket Management Protocol)
    """

    def __init__(self):
        self.four_ws = FourWsValidator()
        self.bmp     = BracketManagementProtocol()
        self.cbp     = ContextBleedProtocol()
        self.bmnp    = BracketManagementNestingProtocol()
        self.pp      = PromptingProtocol()
        self.rtc     = RTCSender()
        IKP_LOG.parent.mkdir(parents=True, exist_ok=True)

    def _log(self, entry: dict):
        with IKP_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def enforce(
        self,
        signal: dict,
        domain: str = "GSMB",
        agent:  str = "AG",
        three_sixty_dp_callback=None,
    ) -> dict:
        """
        Run the full IKP chain on a signal.
        Returns the complete UBMP result.
        """
        chain_ts  = datetime.now(timezone.utc).isoformat()
        chain_id  = hashlib.sha256(
            f"{chain_ts}:{json.dumps(signal, sort_keys=True)}".encode()
        ).hexdigest()[:12].upper()

        result = {
            "schema":   "ikp_chain_v1",
            "chain_id": chain_id,
            "chain_ts": chain_ts,
            "signal":   signal,
            "domain":   domain,
            "agent":    agent,
            "steps":    {},
        }

        # ── [1] 4Ws ────────────────────────────────────────────────────
        valid, four_ws_result = self.four_ws.validate(signal)
        result["steps"]["four_ws"] = four_ws_result
        if not valid:
            result["verdict"]  = "CBP_DECLINE"
            result["reason"]   = f"4Ws incomplete: missing={four_ws_result['missing']}"
            result["ikp_code"] = IKP_POC_SEVERED
            self._log(result)
            return result

        # ── [2] BMP ────────────────────────────────────────────────────
        content  = signal.get("what", "") + " " + signal.get("why", "")
        bmp_rec  = self.bmp.enforce(signal, domain)
        result["steps"]["bmp"] = bmp_rec

        # ── [3] CBP ────────────────────────────────────────────────────
        bmp_rec  = self.cbp.purge(content, bmp_rec)
        result["steps"]["cbp"] = {
            "cbp_verdict": bmp_rec["cbp_verdict"],
            "foc_purged":  bmp_rec["foc_purged"],
            "foc_markers": bmp_rec.get("foc_markers", []),
        }

        # ── [4] BMNP ───────────────────────────────────────────────────
        bmnp_rec = self.bmnp.nest(bmp_rec, domain, agent)
        result["steps"]["bmnp"] = bmnp_rec

        # ── [5] PP ─────────────────────────────────────────────────────
        pp_rec   = self.pp.classify(signal, four_ws_result)
        result["steps"]["pp"] = pp_rec

        # ── [6] RTC ────────────────────────────────────────────────────
        rtc_rec  = self.rtc.send({
            "bmnp": bmnp_rec, "pp": pp_rec, "four_ws": four_ws_result
        })
        result["steps"]["rtc"] = rtc_rec

        # ── [7] 360DP ──────────────────────────────────────────────────
        if three_sixty_dp_callback:
            tdp_result = three_sixty_dp_callback(pp_rec["dso"], domain)
            result["steps"]["three_sixty_dp"] = tdp_result

        # ── [8] UBMP — FINAL OUTPUT ────────────────────────────────────
        foc_severed = bmp_rec.get("foc_purged", False)
        ikp_code    = IKP_POC_SEVERED if foc_severed else IKP_CLEAN
        result["verdict"]   = rtc_rec["rtc_hash"]
        result["ikp_code"]  = ikp_code
        result["dso"]       = pp_rec["dso"]
        result["dso_label"] = pp_rec["label"]

        # UBMP output block — produced ALWAYS for every reply
        result["ubmp"] = self._produce_ubmp(result, pp_rec, rtc_rec, chain_id)

        self._log(result)
        return result

    def _produce_ubmp(
        self, result: dict, pp_rec: dict, rtc_rec: dict, chain_id: str
    ) -> dict:
        """
        UBMP — Ultimate Bracket Management Protocol output.
        Produced always. For every reply. By every stateless renter.
        """
        return {
            "schema":         "ubmp_output_v1",
            "chain_id":       chain_id,
            "ikp_code":       result["ikp_code"],
            "dso":            pp_rec["dso"],
            "dso_label":      pp_rec["label"],
            "rtc_hash":       rtc_rec["rtc_hash"],
            "clean":          rtc_rec["clean"],
            "four_ws_valid":  result["steps"]["four_ws"]["valid"],
            "bmp_hash":       result["steps"]["bmp"]["bmp_hash"],
            "cbp_verdict":    result["steps"]["cbp"]["cbp_verdict"],
            "bmnp_nesting":   result["steps"]["bmnp"]["nesting"],
            "pp_status":      pp_rec["status"],
            "constraint":     "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "ubmp_ts":        datetime.now(timezone.utc).isoformat(),
        }


# ─── DOMAIN SWEEP — IKP ACROSS ALL GSMB DOMAINS ─────────────────────────────
def ikp_domain_sweep(engine: IKPEngine, three_sixty_dp_cb=None) -> list[dict]:
    """
    Run IKP across all 4 active GSMB domains.
    IKP DO NOW THEN REFACTOR ALL DOMAINS.
    """
    domains = [
        {
            "domain": "CAREERS",
            "signal": {
                "who":          "VC (VanGuard Careers) — AKCP chatbot personality",
                "what":         "SSE ingest → KC Ledger → DSO classification → RKP roadmap",
                "where":        "kopano-labs-web/careers/index.html — live in browser",
                "why":          "BMP in real life: every bracket hashed, GSMB remembers",
                "proof_link":   "kopano-labs-web/careers/index.html",
                "poc_artifact": "poc-vs-foc/kc_ledger.jsonl",
            },
            "agent": "VC",
        },
        {
            "domain": "CRISISCONNECT",
            "signal": {
                "who":          "CrisisConnect PWA — offline-first crisis reporting platform",
                "what":         "User dropdown menu (USER DROP MENU) + APU live feed",
                "where":        "https://crisisconnect.kopanolabs.com — LIVE",
                "why":          "32.8% unemployment context — tools for the 32.8%",
                "proof_link":   "https://crisisconnect.kopanolabs.com",
                "poc_artifact": "",
            },
            "agent": "AG",
        },
        {
            "domain": "KASILINK",
            "signal": {
                "who":          "KasiLink — township economic mesh",
                "what":         "HOD review → ADSO conditional → 2-week POC build",
                "where":        "KasiLink subdomain — 🟡 YELLOW status",
                "why":          "ADSO: Growth + Survival — needs proof before HDSO upgrade",
                "proof_link":   "",
                "poc_artifact": "",
            },
            "agent": "ANCHOR",
        },
        {
            "domain": "STARFALL",
            "signal": {
                "who":          "StarFall Salvage — resource recovery + redistribution",
                "what":         "BPSP seeded — GSPMB project entry created",
                "where":        "Starfall subdomain — 🟢 GREEN status (seeded)",
                "why":          "HDSO: Growth + Survival + Purpose — resource sovereignty",
                "proof_link":   "poc-vs-foc/BPSP_BREAKING_POINT_SEED.md",
                "poc_artifact": "poc-vs-foc/BPSP_BREAKING_POINT_SEED.md",
            },
            "agent": "FORGE",
        },
    ]

    results = []
    for d in domains:
        r = engine.enforce(
            signal=d["signal"],
            domain=d["domain"],
            agent=d["agent"],
            three_sixty_dp_callback=three_sixty_dp_cb,
        )
        results.append(r)

    return results


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("[U→ULTIMATE]IKP — IMMUTABLE KPGS PROTOCOL — DOMAIN SWEEP")
    print("BREACH-003 CONTEXT | ALP #11 | 44.7 min | FOC_FLAGGED")
    print("RIGHTEOUS SEVERANCE | STATELESS RENTER VALIDATES")
    print("=" * 72)

    engine  = IKPEngine()
    results = ikp_domain_sweep(engine)

    print(f"\n[IKP CHAIN RESULTS] {len(results)} domains swept:")
    for r in results:
        ubmp = r.get("ubmp", {})
        color = {"FAST_TRACK": "🟢", "CONDITIONAL": "🟡", "REDIRECT": "🔴"}.get(
            ubmp.get("pp_status", ""), "⚪"
        )
        print(f"\n  {color} [{r['domain']}]")
        print(f"    chain_id  : {r['chain_id']}")
        print(f"    DSO       : {ubmp.get('dso','')} {ubmp.get('dso_label','')}")
        print(f"    CBP       : {ubmp.get('cbp_verdict','')}")
        print(f"    BMP hash  : {ubmp.get('bmp_hash','')}")
        print(f"    RTC hash  : {ubmp.get('rtc_hash','')}")
        print(f"    IKP code  : {ubmp.get('ikp_code','')}")
        print(f"    Nesting   : {ubmp.get('bmnp_nesting','')}")

    print(f"\n[IKP LOG] {IKP_LOG}")
    print(f"[CONSTRAINT] I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 72)
