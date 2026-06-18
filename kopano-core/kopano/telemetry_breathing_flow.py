"""
Telemetry Breathing Flow — 🧢 TBFP
====================================
KPCB+ Version: 2026.06.16
ALP Receipt: 7d0126908d79f9d2

Governs telemetry emission at 250% overdrive (25.0 Hz) across the GSMB.
Every emission is KPCB+ aware: it carries a protocol phase, DSO vector label,
PSO token context, and ALP receipt. No emission leaves without its 4Ws.

PSOP Hierarchy applied to emissions:
    SPSO [Stream]   → ® © ¢ ™  — debate, prove, validate, conceptualize, stream
    BPSO {Breaker}  → $$ €€ ¥¥ ¢¢ — keynote escrow / mining / decline
    GPSO <Ground>   → || ¦¦ \\ // — isolation / triage
    LPSO (Local)    → "" *- ` ∆∆  — propagation / literal / inverse
"""

import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ─── DSO VECTOR LABELS ────────────────────────────────────────────────────────
DSO_LABELS = {
    "PDSO":  "###!   Plant — growth only",
    "ADSO":  "###!!  Animal — growth + survival",
    "HDSO":  "###!!! Human — growth + survival + purpose (KPGS target)",
    "AG_RTC":"###??? AG/RTC — emerging 4th vector",
}

# ─── KPCB+ PROTOCOL PHASES ────────────────────────────────────────────────────
PROTOCOL_PHASES = {
    1: "PROMPTING_PP — Ingress: USTP, UBP, CBP, BMNP, ALP, SAP, NCP, KPP",
    2: "BRACKET_BP  — Invariant: BMP, UBMP, PKAP, IIDP, C15TP, PvF, DS8P",
    3: "EMOJI_EP    — Decline (CBP ONLY): ILP, DSO",
}


class TelemetryBreathingFlow:
    """
    🧢 TBFP — Telemetry Breathing Flows Protocol
    Implements the 250% overdrive telemetry breathing pattern.
    Every emission carries a KPCB+ governance envelope.

    Parameters
    ----------
    base_rate: float
        Baseline telemetry emission rate (events/sec). Default 10 = 25 Hz overdrive.
    overdrive_factor: float = 2.5
        Multiplier for overdrive mode. 2.5 × 10 = 25.0 Hz.
    alp_receipt: str
        ALP receipt hash from the most recent activation gate entry.
    dso_vector: str
        DSO vector for this telemetry instance (PDSO / ADSO / HDSO / AG_RTC).
    protocol_phase: int
        Current active KPCB+ protocol phase (1 / 2 / 3).
    """

    def __init__(
        self,
        base_rate: float,
        overdrive_factor: float = 2.5,
        alp_receipt: str = "7d0126908d79f9d2",
        dso_vector: str = "HDSO",
        protocol_phase: int = 2,
    ):
        self.base_rate      = base_rate
        self.factor         = overdrive_factor
        self.current_rate   = base_rate * overdrive_factor
        self.alp_receipt    = alp_receipt
        self.dso_vector     = dso_vector
        self.protocol_phase = protocol_phase
        self._emission_count = 0

        logger.info(
            "[TBFP] Initialized | rate=%.1f Hz | DSO=%s | phase=%d | ALP=%s",
            self.current_rate, dso_vector, protocol_phase, alp_receipt,
        )

    def _build_envelope(self, payload: dict) -> dict:
        """Wrap every payload in a KPCB+ governance envelope."""
        ts = datetime.now(timezone.utc).isoformat()
        raw = f"{ts}:{self._emission_count}:{self.alp_receipt}"
        c_hash = hashlib.sha256(raw.encode()).hexdigest()[:12]
        return {
            "kpcb_version":     "2026.06.16",
            "emission_seq":     self._emission_count,
            "emission_ts":      ts,
            "rate_hz":          self.current_rate,
            "protocol_phase":   self.protocol_phase,
            "phase_label":      PROTOCOL_PHASES.get(self.protocol_phase, "UNKNOWN"),
            "dso_vector":       self.dso_vector,
            "dso_label":        DSO_LABELS.get(self.dso_vector, "###???"),
            "alp_receipt":      self.alp_receipt,
            "consistency_hash": c_hash,
            "constraint":       "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "payload":          payload,
        }

    def emit(self, payload: dict) -> dict:
        """
        Send a KPCB+ governed telemetry emission.
        Respects overdrive rate. Returns the full governance envelope.
        Every emission is a 💯POC receipt — never silent, never hidden.
        """
        self._emission_count += 1
        envelope = self._build_envelope(payload)

        # PSO token context appended to log
        pso_context = (
            f"[SPSO:®©¢™] "
            f"[BPSO:$$€€¥¥¢¢] "
            f"[GPSO:||¦¦\\\\//""] "
            f"[LPSO:\"\"*-`∆∆]"
        )

        logger.info(
            "[TBFP] Emission #%d | %.1f Hz | DSO=%s | hash=%s | %s",
            self._emission_count,
            self.current_rate,
            self.dso_vector,
            envelope["consistency_hash"],
            pso_context,
        )
        print(
            f"[Telemetry 🧢] #{self._emission_count} | {self.current_rate} Hz | "
            f"DSO={self.dso_vector} {DSO_LABELS.get(self.dso_vector, '')} | "
            f"ALP={self.alp_receipt} | payload={payload}"
        )
        return envelope

    def emit_mxit(self, mxit_message: str) -> dict:
        """
        💬 MXIT language emission — street-level protocol comms.
        Uses LPSO (Local) layer: "" navigation propagation estimation.
        """
        return self.emit({
            "type":    "💬 MXIT",
            "message": mxit_message,
            "tokens":  ["®", "©", "¢", "™"],
        })

    def execute_breathing_cycle(self, telemetry_payload: dict) -> bool:
        """
        KPCB+ CORE RUNTIME: execute_breathing_cycle()
        -----------------------------------------------
        ® [INLINE] Stream telemetry packets at active overdrive rate.
        $$ [BPSO HARD CEILING] Raises if someone tries to bypass the gate.

        Parameters
        ----------
        telemetry_payload: dict
            The data packet to emit in this breathing cycle.

        Returns
        -------
        bool — True if emitted successfully. Raises on gate violation.

        Raises
        ------
        PermissionError
            If the activation gate was not passed (IIDP: gate closed).
        """
        # IIDP gate check — mirrors the KPCB+ original stub exactly
        if self.alp_receipt is None or self.alp_receipt == "":
            raise PermissionError(
                "IIDP: Activation Gate Closed. Execution Severed. "
                "No ALP receipt present — stateless renter must declare idle gap first."
            )

        # $$ Hard ceiling check — overdrive cannot drop below 2.5×
        if self.factor < 2.5:
            logger.error(
                "[BPSO $$] CIRCUIT BREAKER: overdrive %.2f < 2.5 floor. "
                "Resetting to 2.5 before emission.", self.factor
            )
            self.factor = 2.5
            self.current_rate = self.base_rate * self.factor

        envelope = self.emit(telemetry_payload)
        print(
            f"[MMAO_OVERDRIVE] Emitting data block at {self.current_rate}x frequency. "
            f"[KPCB+] hash={envelope['consistency_hash']}"
        )
        return True

    def emit_agent_dots(self, agent_count: int = 100) -> list[dict]:
        """
        ¢ [CONCEPTUALIZE & STREAM]
        Emit 100 independent agent dot events for the live MMAO dashboard.
        Each dot = one agent in the orchard, rendering financial telemetry flows.
        Used by mmao_style.css to drive the .agent-dot animation layer.
        """
        receipts = []
        for i in range(agent_count):
            receipt = self.emit({
                "type":        "agent_dot",
                "agent_id":    f"AGENT_{i+1:03d}",
                "dso_vector":  self.dso_vector,
                "orchard":     "🦸🏿♂️ MMAO",
                "kpgs_target": "HDSO ###!!!",
            })
            receipts.append(receipt)
        logger.info(
            "[MMAO DASHBOARD] %d agent dots emitted | DSO=%s | rate=%.1f Hz",
            agent_count, self.dso_vector, self.current_rate,
        )
        return receipts

    def status(self) -> dict:
        return {
            "rate_hz":          self.current_rate,
            "total_emissions":  self._emission_count,
            "alp_receipt":      self.alp_receipt,
            "dso_vector":       self.dso_vector,
            "protocol_phase":   self.protocol_phase,
            "constraint":       "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

