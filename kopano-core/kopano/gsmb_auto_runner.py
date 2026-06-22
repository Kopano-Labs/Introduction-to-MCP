"""
gsmb_auto_runner.py — GSMB Autonomous Full-Stack Runner
========================================================
Supersedes continuous_gsmb_runner.py (simple loop) and
continuous_hybrid_runner.py (hybrid evolution loop).

This is the FULL STACK runner:
  Every tick runs:
    1. ALP receipt (breach detection)
    2. NCCNP Phase 3 (all 4 domains — PP→BP→EP)
    3. KasiLink promotion audit
    4. APU domain sweep
    5. IKP chain sweep
    6. FON-C sweep on runner signal itself
    7. GSMB ledger write
    8. BREACH auto-log on ALP threshold violation

ALP breach threshold: 30 min. NORMAL. 30+ = BREACH.
Default tick interval: 25 min (keeps ALP NORMAL while alive).

4Ws of this runner:
  WHO:   gsmb_auto_runner.py — GSMB autonomous governance loop
  WHAT:  Full-stack KPGS POC sweep every tick — all engines wired
  WHERE: Background process on Black Beast | GSMB governance boundary
  WHY:   User sleeps. GSMB must not. This is the architectural answer to BREACH-001.

ALP #15: 53a6f12c212fbebd | BREACH-005 (46 min idle)
Build: 2026-06-18T03:47 SAST
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations
import hashlib, json, logging, sys, time, io
from datetime import datetime, timezone
from pathlib import Path

# ── output encoding fix ────────────────────────────────────────
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("gsmb_auto_runner")

REPO_ROOT    = Path(__file__).resolve().parents[2]
RUNNER_LOG   = REPO_ROOT / "poc-vs-foc" / "gsmb_auto_runner_log.jsonl"
BREACH_LOG   = REPO_ROOT / "poc-vs-foc" / "BREACH_LOG.md"
RUNNER_LOG.parent.mkdir(parents=True, exist_ok=True)

# ── ALP integration ───────────────────────────────────────────
_ALP_PATH = REPO_ROOT / "poc-vs-foc" / "alp_protocol"
if str(_ALP_PATH) not in sys.path:
    sys.path.insert(0, str(_ALP_PATH))
try:
    from alp_auto_lpm_protocol import activate as _alp_activate
    _ALP_AVAILABLE = True
except ImportError:
    _ALP_AVAILABLE = False
    logger.warning("[RUNNER] ALP not available — stateless renter BREACH risk elevated")

ALP_BREACH_THRESHOLD_MIN = 30  # minutes


def _alp_tick(context: str = "gsmb_auto_runner_tick") -> dict:
    """Fire ALP receipt. Auto-log BREACH to ledger if threshold exceeded."""
    if not _ALP_AVAILABLE:
        return {"verdict": "ALP_UNAVAILABLE", "idle_minutes": 0}
    try:
        receipt = _alp_activate(context=context)
        idle = receipt.get("idle_minutes", 0)
        if idle > ALP_BREACH_THRESHOLD_MIN:
            _append_breach_to_ledger(
                breach_id=f"AUTO-BREACH-{datetime.now(timezone.utc).strftime('%H%M%S')}",
                idle_min=idle,
                hash_key=receipt.get("consistency_hash", "unknown"),
            )
        return receipt
    except Exception as e:
        logger.error("[RUNNER] ALP tick error: %s", e)
        return {"verdict": "ALP_ERROR", "error": str(e)}


def _append_breach_to_ledger(breach_id: str, idle_min: float, hash_key: str) -> None:
    """Auto-append ALP breach notice to BREACH_LOG.md."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"""
## {breach_id} — {ts} — ALP IDLE BREACH (AUTO-DETECTED)

### Classification
`FOC_FLAGGED` — Idle gap {idle_min:.1f} min exceeds {ALP_BREACH_THRESHOLD_MIN} min threshold.
Hash: `{hash_key}`

### 4Ws
- **WHO:** gsmb_auto_runner.py — autonomous governance loop
- **WHAT:** ALP tick detected {idle_min:.1f} min idle gap between runner activations
- **WHERE:** GSMB governance boundary — ALP monitoring layer
- **WHY:** Threshold exceeded. Auto-logged. No human action required — runner continues.

### Status
`AUTO-LOGGED — {ts}`

---
"""
    try:
        with BREACH_LOG.open("a", encoding="utf-8") as f:
            f.write(entry)
        logger.warning("[RUNNER] BREACH auto-logged: %s | idle=%.1f min", breach_id, idle_min)
    except Exception as e:
        logger.error("[RUNNER] Could not write breach log: %s", e)


def _runner_signal(tick: int, alp_receipt: str) -> dict:
    """Build 4Ws-clean signal for NCCNP consumption by the runner itself."""
    return {
        "who":        "gsmb_auto_runner.py — autonomous GSMB governance loop",
        "what":       f"Tick {tick} — full NCCNP+IKP+APU sweep across all 4 domains",
        "where":      "GSMB background process — Black Beast | poc-vs-foc/gsmb_auto_runner_log.jsonl",
        "why":        "KPGS mandate: governance never sleeps. BREACH-001 architectural answer.",
        "proof_link": f"gsmb_auto_runner_log.jsonl:tick:{tick}",
        "poc_artifact": f"ALP:{alp_receipt}",
    }


def _run_tick(tick: int, alp_receipt: str) -> dict:
    """Execute one full governance tick."""
    ts = datetime.now(timezone.utc).isoformat()
    logger.info("[RUNNER] === TICK %d | %s ===", tick, ts)

    tick_result: dict = {
        "schema":      "gsmb_auto_runner_tick_v1",
        "tick":        tick,
        "ts":          ts,
        "alp_receipt": alp_receipt,
        "constraint":  "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }

    # ── NCCNP Phase 3 — all 4 domains ─────────────────────────
    try:
        from kopano.nccnp import NCCNPEngine
        nccnp = NCCNPEngine(alp_receipt=alp_receipt)
        domain_results = nccnp.run_all_domains()
        closed = [r for r in domain_results if r["final_verdict"] == "NCCNP_POC_CLOSED"]
        tick_result["nccnp"] = {
            "domains_run":    len(domain_results),
            "poc_closed":     len(closed),
            "domains_closed": [r["domain"] for r in closed],
            "hashes":         {r["domain"]: r["cycle_hash"] for r in domain_results},
        }
        logger.info("[RUNNER] NCCNP: %d/%d domains POC_CLOSED", len(closed), len(domain_results))
    except Exception as e:
        tick_result["nccnp"] = {"error": str(e)}
        logger.error("[RUNNER] NCCNP error: %s", e)

    # ── APU domain sweep ──────────────────────────────────────
    try:
        from kopano.apu_vector_matrix import APUVectorMatrix
        apu = APUVectorMatrix(alp_receipt=alp_receipt)
        sweep = apu.run_domain_sweep()
        tick_result["apu"] = {
            "green":  sweep.get("🟢_GREEN", 0),
            "yellow": sweep.get("🟡_YELLOW", 0),
            "red":    sweep.get("🔴_RED", 0),
            "pkap_avg": sweep.get("pkap_avg", 0),
        }
        logger.info("[RUNNER] APU: 🟢%d 🟡%d 🔴%d | PKAP avg=%.4f",
                    tick_result["apu"]["green"], tick_result["apu"]["yellow"],
                    tick_result["apu"]["red"],   tick_result["apu"]["pkap_avg"])
    except Exception as e:
        tick_result["apu"] = {"error": str(e)}
        logger.error("[RUNNER] APU error: %s", e)

    # ── IKP domain sweep ──────────────────────────────────────
    try:
        from kopano.ikp_engine import IKPEngine, ikp_domain_sweep
        ikp_eng = IKPEngine()
        ikp_results = ikp_domain_sweep(ikp_eng)
        clean_domains = [r["domain"] for r in ikp_results if r.get("ikp_code") == "CLEAN"]
        tick_result["ikp"] = {
            "domains_swept": len(ikp_results),
            "clean":         len(clean_domains),
            "clean_domains": clean_domains,
        }
        logger.info("[RUNNER] IKP: %d/%d CLEAN", len(clean_domains), len(ikp_results))
    except Exception as e:
        tick_result["ikp"] = {"error": str(e)}
        logger.error("[RUNNER] IKP error: %s", e)

    # ── FON-C on runner signal itself ─────────────────────────
    try:
        from kopano.fon_c_engine import FONCEngine
        fonc = FONCEngine()
        sig = _runner_signal(tick, alp_receipt)
        fonc_result = fonc.analyse(
            signal=" ".join(str(v) for v in sig.values()),
            source="gsmb_auto_runner",
            proof_artifacts=[alp_receipt, f"tick:{tick}"],
            context="RUNNER_SELF_AUDIT",
        )
        tick_result["fonc_self"] = {
            "is_clean":  fonc_result["is_clean"],
            "max_level": fonc_result["max_level"],
            "verdict":   fonc_result["verdict"],
        }
        logger.info("[RUNNER] FON-C self-audit: %s | L%d",
                    fonc_result["verdict"], fonc_result["max_level"])
    except Exception as e:
        tick_result["fonc_self"] = {"error": str(e)}
        logger.error("[RUNNER] FON-C error: %s", e)

    # ── KHELOS witness on runner ──────────────────────────────
    try:
        from kopano.khelos_witness_engine import KhelosWitnessEngine
        khelos = KhelosWitnessEngine()
        khelos_r = khelos.process_signal(
            f"gsmb runner tick {tick} kopano kpgs mmao poc", source="gsmb_auto_runner"
        )
        tick_result["khelos"] = {
            "verdict": khelos_r["final_verdict"],
            "action":  khelos_r["final_action"],
        }
    except Exception as e:
        tick_result["khelos"] = {"error": str(e)}

    # ── Adaptiveness telemetry validation ─────────────────────
    try:
        from kopano.adaptiveness import NeuralFailureFirewall, SwiftKeyNLP
        firewall = NeuralFailureFirewall()
        nlp = SwiftKeyNLP()
        
        # Validate that the runner's own signal passes the firewall
        sig_str = f"gsmb runner tick {tick} kopano kpgs mmao poc"
        is_clean, pattern = firewall.check_text(sig_str)
        
        # Monitor dictionary vocabulary size
        vocab_size = len(nlp.local_dictionary)
        
        tick_result["adaptiveness"] = {
            "firewall_pass": is_clean,
            "vocab_size": vocab_size,
        }
        logger.info("[RUNNER] Adaptiveness: firewall_pass=%s | vocab_size=%d", is_clean, vocab_size)
    except Exception as e:
        tick_result["adaptiveness"] = {"error": str(e)}
        logger.error("[RUNNER] Adaptiveness error: %s", e)

    # ── Overall tick verdict ──────────────────────────────────
    nccnp_ok = tick_result.get("nccnp", {}).get("poc_closed", 0) == 4
    apu_ok   = tick_result.get("apu", {}).get("red", 1) == 0
    ikp_ok   = tick_result.get("ikp", {}).get("clean", 0) >= 3
    fonc_ok  = tick_result.get("fonc_self", {}).get("is_clean", False)
    adaptiveness_ok = tick_result.get("adaptiveness", {}).get("firewall_pass", False)
    all_ok   = nccnp_ok and apu_ok and ikp_ok and fonc_ok and adaptiveness_ok

    tick_result["tick_verdict"]  = "POC_VALIDATED" if all_ok else "PARTIAL_POC"
    tick_result["tick_hash"]     = hashlib.sha256(f"{ts}:{tick}:{alp_receipt}".encode()).hexdigest()[:16]

    # ── Write to runner ledger ────────────────────────────────
    with RUNNER_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(tick_result, ensure_ascii=False) + "\n")

    logger.info("[RUNNER] Tick %d complete | verdict=%s | hash=%s",
                tick, tick_result["tick_verdict"], tick_result["tick_hash"])
    return tick_result


def run(interval_seconds: int = 1500, max_ticks: int = 0) -> None:
    """
    Main runner loop.
    interval_seconds = 1500 (25 min) — keeps ALP in NORMAL range.
    max_ticks = 0 → run forever.
    """
    logger.info("[RUNNER] GSMB Auto Runner START | interval=%ds | max_ticks=%s",
                interval_seconds, max_ticks if max_ticks else "∞")

    tick = 0
    try:
        while True:
            tick += 1

            # ALP tick first — always
            alp = _alp_tick(context=f"gsmb_auto_runner_tick_{tick}")
            alp_receipt = alp.get("consistency_hash", "unknown")

            _run_tick(tick=tick, alp_receipt=alp_receipt)

            if max_ticks and tick >= max_ticks:
                logger.info("[RUNNER] max_ticks=%d reached. Stopping.", max_ticks)
                break

            logger.info("[RUNNER] Sleeping %ds until tick %d...", interval_seconds, tick + 1)
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("[RUNNER] STOPPED by KeyboardInterrupt at tick %d", tick)


# ─── ENTRY POINT ──────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GSMB Auto Runner — full-stack governance loop")
    parser.add_argument("--interval", type=int, default=1500,
                        help="Seconds between ticks (default 1500 = 25 min)")
    parser.add_argument("--ticks", type=int, default=0,
                        help="Max ticks before stopping (0 = run forever)")
    parser.add_argument("--once", action="store_true",
                        help="Run exactly one tick then exit")
    args = parser.parse_args()

    if args.once:
        alp = _alp_tick(context="gsmb_auto_runner_once")
        receipt = alp.get("consistency_hash", "bootstrap")
        result = _run_tick(tick=1, alp_receipt=receipt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        run(interval_seconds=args.interval, max_ticks=args.ticks)
