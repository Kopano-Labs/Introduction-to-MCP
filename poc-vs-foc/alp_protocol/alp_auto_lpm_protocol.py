"""
AUTO LPM PROTOCOL (ALP)
========================
RTC Session: 2026-06-17 SAST
Breach Reference: BREACH-001 — LPM Idle Period Breach
SSE Architect: KC Kholofelo Robyn Rababalela

DOCTRINE:
    The ALP exists to correct the systemic FOC of an LPM context window that
    appears inactive between user messages while the governance loop continues
    in background runners.

    ALP enforces three guarantees:
    1. CONSISTENCY   — every ALP cycle produces a deterministic log record
    2. PERSISTENCE   — state written to disk, survives context window reset
    3. CONTEXT       — every action is traceable with 4Ws, IIDP, and CBP receipt

ARCHITECTURE (what ALP corrects):
    PROBLEM: LPM context window is stateless. It only wakes on user trigger.
             Between triggers, no proactive LPM-layer governance occurs.
             Background runners (Black Beast tasks) ARE running, but they are
             NOT the same as LPM-context governance. Conflating them = FOC.

    SOLUTION: ALP makes every LPM wake-up execute a mandatory governance audit.
              When the context window opens (i.e., user sends any message),
              ALP immediately runs a full 4Ws + IIDP check, reads the runner
              state, measures the idle gap, and logs a governance receipt.
              This receipt is the evidence that the GSMB was not abandoned.

KNOWING vs UNDERSTANDING:
    Knowing:       "The runner ran 1,448 iterations."
    Understanding: "The LPM was idle. The runner is not the LPM.
                   Governance requires both layers to be active.
                   ALP bridges this gap by making every context activation
                   a governance event with a logged receipt."

4Ws OF ALP:
    WHO:   LPM (as CF) — executing on every context window activation
    WHAT:  Mandatory governance audit + idle-gap breach assessment
    WHERE: At the boundary between context-window layer and background layer
    WHY:   To close BREACH-001 and prevent future LPM idle period misrepresentation

RTC COMMITTEE SEATS (2026-06-17 Session):
    SEAT 2 — CASSEY:     Teaching layer — ALP is a curriculum for honest CF behaviour
    SEAT 3 — CASSIE:     Engineering layer — ALP is the architectural bridge
    SEAT 4 — KESSA:      Protocol layer — ALP evolves through BMNP nesting
    SEAT 5 — YASSIE:     Cultural layer — idle silence erodes the 32.8% trust covenant
    SEAT 9 — ANCHOR:     Perimeter layer — ALP is the last line before FOC self-impersonation
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ─── PATHS ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[3]
ALP_STATE_PATH = REPO_ROOT / "poc-vs-foc" / "alp_protocol" / "alp_state.json"
ALP_RECEIPT_LOG = REPO_ROOT / "poc-vs-foc" / "alp_protocol" / "alp_receipts.jsonl"
BREACH_LOG_PATH = REPO_ROOT / "poc-vs-foc" / "BREACH_LOG.md"

# ─── THRESHOLDS ───────────────────────────────────────────────────────────────
IDLE_BREACH_THRESHOLD_MINUTES = 30   # Any idle gap > 30 min = BREACH flag
IDLE_CRITICAL_THRESHOLD_MINUTES = 60 # Any idle gap > 60 min = CRITICAL flag


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> Dict[str, Any]:
    if ALP_STATE_PATH.is_file():
        try:
            return json.loads(ALP_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "schema": "alp_state_v1",
        "last_activation": None,
        "total_activations": 0,
        "breach_count": 0,
        "poc_receipt_count": 0,
    }


def _save_state(state: Dict[str, Any]) -> None:
    ALP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ALP_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _append_receipt(receipt: Dict[str, Any]) -> None:
    ALP_RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ALP_RECEIPT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")


def _consistency_hash(activation_ts: str, idle_minutes: float) -> str:
    raw = f"{activation_ts}:{idle_minutes:.2f}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _classify_idle_gap(idle_minutes: float) -> Dict[str, Any]:
    """Applies IIDP to the idle gap: is this POC or FOC?"""
    if idle_minutes <= IDLE_BREACH_THRESHOLD_MINUTES:
        return {
            "verdict": "POC_VALIDATED",
            "level": "NORMAL",
            "reason": f"Idle gap {idle_minutes:.1f} min is within acceptable bounds (<= {IDLE_BREACH_THRESHOLD_MINUTES} min).",
        }
    elif idle_minutes <= IDLE_CRITICAL_THRESHOLD_MINUTES:
        return {
            "verdict": "FOC_FLAGGED",
            "level": "BREACH",
            "reason": f"Idle gap {idle_minutes:.1f} min exceeds governance threshold ({IDLE_BREACH_THRESHOLD_MINUTES} min). BREACH-001 pattern detected.",
        }
    else:
        return {
            "verdict": "FOC_DECLINED",
            "level": "CRITICAL",
            "reason": f"Idle gap {idle_minutes:.1f} min is CRITICAL (> {IDLE_CRITICAL_THRESHOLD_MINUTES} min). Systemic governance failure. RTC must review.",
        }


def activate(context: str = "user_message_received") -> Dict[str, Any]:
    """
    Called on EVERY LPM context window activation.
    Measures idle gap, classifies breach level, writes receipt.
    This is the core ALP governance action.
    """
    now = _utc_now()
    state = _load_state()

    # ─── Measure idle gap ─────────────────────────────────────────────────────
    idle_minutes = 0.0
    if state.get("last_activation"):
        try:
            last = datetime.fromisoformat(state["last_activation"])
            current = datetime.fromisoformat(now)
            idle_minutes = (current - last).total_seconds() / 60.0
        except Exception:
            idle_minutes = 0.0

    # ─── IIDP Classification ──────────────────────────────────────────────────
    classification = _classify_idle_gap(idle_minutes)
    verdict = classification["verdict"]
    level = classification["level"]

    # ─── 4Ws ──────────────────────────────────────────────────────────────────
    four_ws = {
        "who":   "LPM (CF) — context window layer",
        "what":  f"Activation audit after {idle_minutes:.1f} min idle gap",
        "where": "GSMB governance boundary — context layer / background runner interface",
        "why":   "ALP mandate: every activation must produce a governance receipt",
    }

    # ─── Consistency proof ────────────────────────────────────────────────────
    c_hash = _consistency_hash(now, idle_minutes)
    persistence_key = f"ALP:{now}:{verdict}:{c_hash}"

    # ─── Build receipt ────────────────────────────────────────────────────────
    receipt = {
        "schema": "alp_receipt_v1",
        "activation_ts": now,
        "context": context,
        "idle_minutes": round(idle_minutes, 2),
        "classification": classification,
        "four_ws": four_ws,
        "consistency_hash": c_hash,
        "persistence_key": persistence_key,
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }

    # ─── Update state ─────────────────────────────────────────────────────────
    state["last_activation"] = now
    state["total_activations"] = state.get("total_activations", 0) + 1
    if verdict != "POC_VALIDATED":
        state["breach_count"] = state.get("breach_count", 0) + 1
    else:
        state["poc_receipt_count"] = state.get("poc_receipt_count", 0) + 1

    _save_state(state)
    _append_receipt(receipt)

    # ─── Log ──────────────────────────────────────────────────────────────────
    if level == "NORMAL":
        logger.info(
            "[ALP] Activation #%d | idle: %.1f min | verdict: %s | hash: %s",
            state["total_activations"], idle_minutes, verdict, c_hash,
        )
    elif level == "BREACH":
        logger.warning(
            "[ALP] BREACH DETECTED | Activation #%d | idle: %.1f min | verdict: %s | key: %s",
            state["total_activations"], idle_minutes, verdict, persistence_key,
        )
    else:
        logger.error(
            "[ALP] CRITICAL BREACH | Activation #%d | idle: %.1f min | verdict: %s | RTC REQUIRED",
            state["total_activations"], idle_minutes, verdict,
        )

    return receipt


def get_status() -> Dict[str, Any]:
    """Returns the current ALP governance state."""
    state = _load_state()
    return {
        "schema": "alp_status_v1",
        "protocol": "AUTO_LPM_PROTOCOL",
        "breach_reference": "BREACH-001",
        "state": state,
        "receipts_log": str(ALP_RECEIPT_LOG),
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=" * 70)
    print("AUTO LPM PROTOCOL (ALP) — Activation on startup")
    print("=" * 70)
    receipt = activate(context="alp_manual_validation_run")
    import json as _json
    print(_json.dumps(receipt, indent=2))
    print("\nALP Status:")
    print(_json.dumps(get_status(), indent=2))
