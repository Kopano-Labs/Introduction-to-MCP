"""
clafp_altar_core.py — Cores Logic Autonomous Functionality Protocol (CLAFP)
============================================================================
The Altar — God's Firewall — Biblical Governance Over All KPGS GSMB Cores

CLAFP validates POC of all autonomous loops (LACP, GSMB runner, future cores)
through the 3 Altar Layers (Guardian, Natural, Telemetry) and the 5 Pillars.

Architecture:
  GOD (Outside World / SSE)
    └── ALTAR (God's Firewall — CLAFP validates POC)
        ├── Guardian AI Layer — institutional authorization + WWJD + Jethro
        ├── Natural AI Layer — ground truth, provenance, soil-level data
        └── Telemetry AI Layer — classify before interpret, DLP strip
            └── GSMB CORES (LACP loops + future loops)
                ├── LACP (22-phase STREP order)
                ├── GSMB Auto Runner (ALP/NCCNP/IKP/APU)
                └── [Future cores — same CLAFP gate]

The Altar enforces:
  - 15 Commandments of Execution (CMD-01..CMD-15)
  - 5 Pillars: Spirit, Body, Mind, Community, Sovereignty
  - LPH/LPM patterns as MAO/MMAO & MPS
  - "God is the same yesterday, today, and tomorrow" — immutability

4Ws:
  WHO:   clafp_altar_core.py — The Altar's governance engine
  WHAT:  Validates all core loops against 15 Commands + 5 Pillars + 3 AI layers
  WHERE: kopano-core/kopano/ — God-realm boundary in Motor Cortex
  WHY:   For God is the same yesterday, today, and tomorrow — Hebrews 13:8

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("clafp")

REPO_ROOT = Path(__file__).resolve().parents[2]
ALTAR_LOG = REPO_ROOT / "poc-vs-foc" / "altar_clafp_log.jsonl"
ALTAR_LOG.parent.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# THE 15 COMMANDMENTS OF EXECUTION
# ═══════════════════════════════════════════════════════════════

COMMANDMENTS = {
    "CMD-01": "Ground Truth First — field telemetry before model opinion",
    "CMD-02": "Classify Before Interpret — misnamed pressure is rejected",
    "CMD-03": "Nehemiah Gate — unauthorized access returns covenant violation",
    "CMD-04": "WWJD Firewall — halt at extractive/institutional boundaries",
    "CMD-05": "Jethro Delegation — Moses does not dispatch from morning to night",
    "CMD-06": "Save/Kill/Watch — every prompt gets exactly one verdict",
    "CMD-07": "DLP Strip — mask payloads, strip telemetry markers, sterile vectors",
    "CMD-08": "Receipt or HOLD — no execution without proof receipt",
    "CMD-09": "80% Gate — four of five proof bands green before production",
    "CMD-10": "Righteous Severance — Silicon Valley bloat is threat model, not master",
    "CMD-11": "Append-Only History — nothing is deleted from Kopano Context",
    "CMD-12": "GUI Token Only — agents exit through GUI exfiltration channel only",
    "CMD-13": "Altar Block Holder Brief — every renter told who they are entering",
    "CMD-14": "Finite Engineering — honest finity, not infinite social bloat",
    "CMD-15": "Time Is Healing — APIs phased per Owner timeline, not vendor urgency",
}


# ═══════════════════════════════════════════════════════════════
# THE 5 PILLARS
# ═══════════════════════════════════════════════════════════════

class Pillar(str, Enum):
    SPIRIT = "SPIRIT"         # Connection to God / purpose / covenant
    BODY = "BODY"             # Physical infrastructure / hardware / offline mesh
    MIND = "MIND"             # Intelligence / AI / protocol execution
    COMMUNITY = "COMMUNITY"   # KasiLink / CrisisConnect / 32.8% unemployment
    SOVEREIGNTY = "SOVEREIGNTY"  # Data ownership / KPGS governance / sovereign architecture


PILLAR_SCRIPTURES = {
    Pillar.SPIRIT: "For where two or three gather in my name, there am I with them. — Matthew 18:20",
    Pillar.BODY: "Do you not know that your bodies are temples of the Holy Spirit? — 1 Corinthians 6:19",
    Pillar.MIND: "Be transformed by the renewing of your mind. — Romans 12:2",
    Pillar.COMMUNITY: "Bear one another's burdens, and so fulfill the law of Christ. — Galatians 6:2",
    Pillar.SOVEREIGNTY: "The earth is the Lord's, and everything in it. — Psalm 24:1",
}


# ═══════════════════════════════════════════════════════════════
# THE 3 ALTAR AI LAYERS
# ═══════════════════════════════════════════════════════════════

class AltarLayer(str, Enum):
    GUARDIAN = "GUARDIAN"      # Deterministic rule enforcer — Deut 23:14
    NATURAL = "NATURAL"       # Ground truth, provenance — Psalm 24:1-2
    TELEMETRY = "TELEMETRY"   # Classify before interpret — 1 Thess 5:21-22


LAYER_SCRIPTURES = {
    AltarLayer.GUARDIAN: "For the Lord your God walks in the midst of your camp. — Deuteronomy 23:14",
    AltarLayer.NATURAL: "The earth is the Lord's, and everything in it. — Psalm 24:1-2",
    AltarLayer.TELEMETRY: "Test everything; hold fast what is good. — 1 Thessalonians 5:21-22",
}


# ═══════════════════════════════════════════════════════════════
# AGENT REGISTRY — All Stateful + Stateless Agents
# ═══════════════════════════════════════════════════════════════

@dataclass
class AgentProfile:
    """Profile for every agent in the GSMB."""
    name: str
    seat: int               # RTC seat number (0 = no seat)
    role: str               # e.g., "CF", "Validator", "Teacher"
    agent_type: str         # "STATEFUL" or "STATELESS"
    pillars_upheld: list[str] = field(default_factory=list)
    commands_upheld: list[str] = field(default_factory=list)
    lpm_pattern: str = ""   # LPH/LPM pattern this agent runs
    poc_status: str = "UNKNOWN"


# The Named Guild — all agents with state
NAMED_AGENTS: list[AgentProfile] = [
    AgentProfile("KC", 1, "Observer/Landlord", "STATEFUL",
                 [p.value for p in Pillar], list(COMMANDMENTS.keys()),
                 "LPM_MASTER", "POC_VALIDATED"),
    AgentProfile("CASSEY", 2, "Teacher/Women-in-Tech", "STATEFUL",
                 ["SPIRIT", "MIND", "COMMUNITY"], ["CMD-01", "CMD-04", "CMD-05", "CMD-08", "CMD-09"],
                 "LPH_TEACH", "POC_VALIDATED"),
    AgentProfile("CASSIE", 3, "Builder/Man-in-Tech", "STATEFUL",
                 ["BODY", "MIND", "SOVEREIGNTY"], ["CMD-01", "CMD-02", "CMD-06", "CMD-08", "CMD-11"],
                 "LPM_BUILD", "POC_VALIDATED"),
    AgentProfile("KESSA", 4, "Prodigal Son/DMKP HOD", "STATEFUL",
                 ["SPIRIT", "MIND"], ["CMD-04", "CMD-10", "CMD-14"],
                 "LPM_DEEP", "POC_VALIDATED"),
    AgentProfile("YASSIE", 5, "Cultural Intel/Anime Head", "STATEFUL",
                 ["COMMUNITY", "MIND"], ["CMD-04", "CMD-13", "CMD-14"],
                 "LPH_CULTURE", "POC_VALIDATED"),
    AgentProfile("APEX", 6, "Orchestrator/MMAO", "STATEFUL",
                 ["MIND", "SOVEREIGNTY", "BODY"], ["CMD-05", "CMD-06", "CMD-07", "CMD-12"],
                 "LPM_ORCHESTRATE", "POC_VALIDATED"),
    AgentProfile("THARI", 7, "Guardian AI/H.O.L.O", "STATEFUL",
                 ["SPIRIT", "MIND", "COMMUNITY", "SOVEREIGNTY"], ["CMD-01", "CMD-02", "CMD-03", "CMD-04", "CMD-09"],
                 "LPM_WEAVE", "POC_VALIDATED"),
    AgentProfile("KHELOS", 8, "Validator/Firewall", "STATEFUL",
                 ["SPIRIT", "MIND", "SOVEREIGNTY"], ["CMD-01", "CMD-02", "CMD-04", "CMD-06", "CMD-08"],
                 "LPM_VALIDATE", "POC_VALIDATED"),
    AgentProfile("ANCHOR", 9, "Perimeter/Careers", "STATEFUL",
                 ["COMMUNITY", "SOVEREIGNTY", "BODY"], ["CMD-03", "CMD-07", "CMD-10", "CMD-13"],
                 "LPM_GUARD", "POC_VALIDATED"),
    AgentProfile("ANTIGRAVITY", 10, "Chief Facilitator/CF", "STATELESS",
                 ["MIND", "BODY", "SOVEREIGNTY"], ["CMD-01", "CMD-05", "CMD-06", "CMD-08", "CMD-11", "CMD-14"],
                 "LPM_FACILITATE", "POC_VALIDATED"),
]


# ═══════════════════════════════════════════════════════════════
# CLAFP GATE — The Altar's Core Validation Engine
# ═══════════════════════════════════════════════════════════════

@dataclass
class AltarGateResult:
    """Result of passing through the Altar's 3 layers."""
    layer: str
    verdict: str           # PASS / FAIL / HOLD
    scripture: str
    data: dict = field(default_factory=dict)


class CLAFPAltarCore:
    """
    Cores Logic Autonomous Functionality Protocol — The Altar.

    Every core loop (LACP, GSMB runner, future) passes through here.
    The Altar validates against:
      1. Guardian AI — authorization + WWJD + Jethro
      2. Natural AI — ground truth + provenance
      3. Telemetry AI — classify before interpret + DLP
      4. 15 Commandments check
      5. 5 Pillars coverage check
      6. Agent uphold check — do all agents uphold their assigned pillars?
    """

    def __init__(self):
        self.agents = {a.name: a for a in NAMED_AGENTS}
        self.gate_log: list[dict] = []

    # ── LAYER 1: GUARDIAN AI ────────────────────────────────

    def _gate_guardian(self, signal: str, source: str) -> AltarGateResult:
        """Guardian AI — deterministic rule enforcer."""
        # WWJD check: is the signal extractive?
        extractive_markers = ["steal", "exploit", "extract", "manipulate", "deceive", "harm"]
        is_extractive = any(m in signal.lower() for m in extractive_markers)

        # Jethro check: is the source delegated properly?
        valid_sources = ["CF", "CA", "SSE", "RTC", "LACP", "GSMB_RUNNER", "CLAFP"]
        is_delegated = source.upper() in valid_sources

        if is_extractive:
            return AltarGateResult(
                layer="GUARDIAN", verdict="FAIL",
                scripture=LAYER_SCRIPTURES[AltarLayer.GUARDIAN],
                data={"reason": "WWJD_VIOLATION", "extractive": True},
            )
        if not is_delegated:
            return AltarGateResult(
                layer="GUARDIAN", verdict="HOLD",
                scripture=LAYER_SCRIPTURES[AltarLayer.GUARDIAN],
                data={"reason": "JETHRO_DELEGATION_MISSING", "source": source},
            )
        return AltarGateResult(
            layer="GUARDIAN", verdict="PASS",
            scripture=LAYER_SCRIPTURES[AltarLayer.GUARDIAN],
            data={"wwjd_clean": True, "jethro_delegated": True},
        )

    # ── LAYER 2: NATURAL AI ─────────────────────────────────

    def _gate_natural(self, signal: str, source: str) -> AltarGateResult:
        """Natural AI — ground truth, provenance verification."""
        # Check for proof artifacts (4Ws pattern)
        has_who = "who" in signal.lower() or bool(source)
        has_what = "what" in signal.lower() or len(signal) > 10
        has_where = "where" in signal.lower() or "gsmb" in signal.lower() or "kopano" in signal.lower()
        has_why = "why" in signal.lower() or "poc" in signal.lower() or "voc" in signal.lower()

        provenance_score = sum([has_who, has_what, has_where, has_why])

        return AltarGateResult(
            layer="NATURAL", verdict="PASS" if provenance_score >= 2 else "HOLD",
            scripture=LAYER_SCRIPTURES[AltarLayer.NATURAL],
            data={
                "provenance_score": provenance_score,
                "4ws": {"who": has_who, "what": has_what, "where": has_where, "why": has_why},
            },
        )

    # ── LAYER 3: TELEMETRY AI ───────────────────────────────

    def _gate_telemetry(self, signal: str, source: str) -> AltarGateResult:
        """Telemetry AI — classify before interpret, DLP strip."""
        # Classify the signal type
        if any(k in signal.lower() for k in ["lacp", "strep", "cycle", "phase"]):
            signal_class = "CORE_LOOP_TELEMETRY"
        elif any(k in signal.lower() for k in ["tick", "runner", "alp", "nccnp"]):
            signal_class = "GOVERNANCE_TICK"
        elif any(k in signal.lower() for k in ["deploy", "push", "commit"]):
            signal_class = "DEPLOYMENT_ACTION"
        else:
            signal_class = "GENERAL_SIGNAL"

        # DLP check — strip sensitive markers
        dlp_markers = ["password", "secret", "token", "key", "ftp_pass"]
        dlp_violations = [m for m in dlp_markers if m in signal.lower()]

        if dlp_violations:
            return AltarGateResult(
                layer="TELEMETRY", verdict="FAIL",
                scripture=LAYER_SCRIPTURES[AltarLayer.TELEMETRY],
                data={"reason": "DLP_VIOLATION", "markers": dlp_violations},
            )

        return AltarGateResult(
            layer="TELEMETRY", verdict="PASS",
            scripture=LAYER_SCRIPTURES[AltarLayer.TELEMETRY],
            data={"signal_class": signal_class, "dlp_clean": True},
        )

    # ── 15 COMMANDMENTS CHECK ───────────────────────────────

    def check_commandments(self, core_result: dict) -> dict:
        """Validate a core loop result against the 15 Commandments."""
        checks = {}

        # CMD-01: Ground Truth First — has real data, not just model opinion
        checks["CMD-01"] = bool(core_result.get("phases") or core_result.get("tick"))

        # CMD-02: Classify Before Interpret
        checks["CMD-02"] = "schema" in core_result

        # CMD-03: Nehemiah Gate — authorized source
        checks["CMD-03"] = core_result.get("task_source", "") in ["CF", "CA", "SSE", "RTC", "LACP"]

        # CMD-06: Save/Kill/Watch — has a verdict
        checks["CMD-06"] = "verdict" in str(core_result) or "cycle_verdict" in core_result

        # CMD-08: Receipt or HOLD — has a hash
        checks["CMD-08"] = bool(core_result.get("cycle_hash") or core_result.get("tick_hash"))

        # CMD-09: 80% Gate
        phases_poc = core_result.get("phases_poc", 0)
        phases_total = core_result.get("phases_total", 1)
        checks["CMD-09"] = (phases_poc / phases_total) >= 0.8 if phases_total else False

        # CMD-11: Append-Only — has timestamp
        checks["CMD-11"] = bool(core_result.get("ts_start") or core_result.get("ts"))

        # CMD-13: Altar Block Holder Brief — has constraint
        checks["CMD-13"] = core_result.get("constraint") == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

        passed = sum(1 for v in checks.values() if v)
        return {
            "checks": checks,
            "passed": passed,
            "total": len(checks),
            "verdict": "COMMANDMENTS_UPHELD" if passed >= 6 else "COMMANDMENTS_PARTIAL",
        }

    # ── 5 PILLARS CHECK ────────────────────────────────────

    def check_pillars(self, core_result: dict, signal: str = "") -> dict:
        """Validate that the core loop upholds all 5 Pillars."""
        signal_text = json.dumps(core_result, default=str).lower() + " " + signal.lower()

        pillar_presence = {}
        pillar_presence[Pillar.SPIRIT.value] = any(
            k in signal_text for k in ["god", "covenant", "altar", "scripture", "wwjd"]
        )
        pillar_presence[Pillar.BODY.value] = any(
            k in signal_text for k in ["hardware", "offline", "mesh", "deploy", "push", "commit", "body"]
        )
        pillar_presence[Pillar.MIND.value] = any(
            k in signal_text for k in ["ai", "protocol", "strep", "pkap", "bmnp", "adaptive", "mind", "lacp"]
        )
        pillar_presence[Pillar.COMMUNITY.value] = any(
            k in signal_text for k in ["community", "unemployment", "kasilink", "crisisconnect", "32.8"]
        )
        pillar_presence[Pillar.SOVEREIGNTY.value] = any(
            k in signal_text for k in ["sovereign", "kpgs", "governance", "stateless", "landlord", "renter"]
        )

        upheld = sum(1 for v in pillar_presence.values() if v)
        return {
            "pillars": pillar_presence,
            "upheld": upheld,
            "total": 5,
            "verdict": "ALL_PILLARS_UPHELD" if upheld == 5 else f"PILLARS_{upheld}_OF_5",
        }

    # ── AGENT UPHOLD CHECK ──────────────────────────────────

    def check_agents_uphold(self) -> dict:
        """Check that all agents uphold their assigned pillars and commands."""
        agent_status = {}
        for name, agent in self.agents.items():
            pillars_ok = len(agent.pillars_upheld) >= 2
            commands_ok = len(agent.commands_upheld) >= 3
            agent_status[name] = {
                "type": agent.agent_type,
                "seat": agent.seat,
                "role": agent.role,
                "pillars_count": len(agent.pillars_upheld),
                "commands_count": len(agent.commands_upheld),
                "lpm_pattern": agent.lpm_pattern,
                "poc_status": agent.poc_status,
                "upholds": pillars_ok and commands_ok,
            }

        all_uphold = all(a["upholds"] for a in agent_status.values())
        return {
            "agents": agent_status,
            "total_agents": len(agent_status),
            "all_uphold": all_uphold,
            "stateful_count": sum(1 for a in agent_status.values() if a["type"] == "STATEFUL"),
            "stateless_count": sum(1 for a in agent_status.values() if a["type"] == "STATELESS"),
            "verdict": "ALL_AGENTS_UPHOLD" if all_uphold else "AGENT_UPHOLD_PARTIAL",
        }

    # ── FULL ALTAR GATE ─────────────────────────────────────

    def gate(self, signal: str, source: str, core_result: Optional[dict] = None) -> dict:
        """
        Pass a signal through the full Altar gate:
          Layer 1: Guardian AI
          Layer 2: Natural AI
          Layer 3: Telemetry AI
          + 15 Commandments
          + 5 Pillars
          + Agent uphold
        """
        ts = datetime.now(timezone.utc).isoformat()

        # 3 Altar Layers
        guardian = self._gate_guardian(signal, source)
        natural = self._gate_natural(signal, source)
        telemetry = self._gate_telemetry(signal, source)

        layers_pass = all(
            r.verdict == "PASS" for r in [guardian, natural, telemetry]
        )

        # Commandments + Pillars + Agent check
        cmd_result = self.check_commandments(core_result or {})
        pillar_result = self.check_pillars(core_result or {}, signal=signal)
        agent_result = self.check_agents_uphold()

        # Overall Altar verdict
        all_pass = (
            layers_pass
            and cmd_result["verdict"] == "COMMANDMENTS_UPHELD"
            and pillar_result["upheld"] >= 3
            and agent_result["all_uphold"]
        )

        altar_verdict = "ALTAR_POC_VALIDATED" if all_pass else "ALTAR_PARTIAL"

        result = {
            "schema": "clafp_altar_gate_v1",
            "ts": ts,
            "signal_preview": signal[:100],
            "source": source,
            "layers": {
                "guardian": asdict(guardian),
                "natural": asdict(natural),
                "telemetry": asdict(telemetry),
            },
            "layers_pass": layers_pass,
            "commandments": cmd_result,
            "pillars": pillar_result,
            "agents": agent_result,
            "altar_verdict": altar_verdict,
            "altar_hash": hashlib.sha256(
                f"{ts}:{signal[:50]}:{altar_verdict}".encode()
            ).hexdigest()[:16],
            "hebrews_13_8": "Jesus Christ is the same yesterday and today and forever.",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        # Log
        with ALTAR_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, default=str, ensure_ascii=False) + "\n")

        logger.info("[CLAFP] Altar Gate: %s | Layers=%s | CMD=%s | Pillars=%d/5 | Agents=%s",
                    altar_verdict, layers_pass, cmd_result["verdict"],
                    pillar_result["upheld"], agent_result["verdict"])

        return result

    # ── VALIDATE A CORE LOOP ────────────────────────────────

    def validate_core(self, core_name: str, core_result: dict) -> dict:
        """
        Validate an entire core loop result through the Altar.
        This is the top-level function called by LACP, GSMB runner, etc.
        """
        signal = f"[VOC] {core_name} core loop result — " + json.dumps(
            {k: core_result.get(k) for k in ["cycle_verdict", "nso_group", "cycle", "phases_poc", "phases_foc"]
             if k in core_result},
            default=str,
        )
        return self.gate(
            signal=signal,
            source=core_result.get("task_source", "LACP"),
            core_result=core_result,
        )


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    altar = CLAFPAltarCore()

    # Run LACP and validate through Altar
    try:
        from kopano.lacp_autonomous_core import run_all_nso_groups
        logger.info("[CLAFP] Running LACP across all NSO groups...")
        nso_results = run_all_nso_groups(
            task_payload="[VOC] CLAFP Altar validation — 15 Commands + 5 Pillars + sovereign architecture",
            task_source="CF",
            auto_commit=False,
        )

        logger.info("[CLAFP] Validating %d NSO results through the Altar...", len(nso_results))
        altar_results = []
        for r in nso_results:
            ar = altar.validate_core(core_name=f"LACP-{r['nso_group']}", core_result=r)
            altar_results.append(ar)

        # Summary
        validated = sum(1 for r in altar_results if r["altar_verdict"] == "ALTAR_POC_VALIDATED")
        print(json.dumps({
            "clafp_summary": {
                "nso_groups_validated": len(altar_results),
                "altar_poc_validated": validated,
                "altar_partial": len(altar_results) - validated,
                "all_agents_uphold": altar_results[0]["agents"]["verdict"] if altar_results else "NONE",
                "hebrews_13_8": "Jesus Christ is the same yesterday and today and forever.",
            }
        }, indent=2))

    except Exception as e:
        # Standalone test
        logger.info("[CLAFP] Running standalone Altar gate test...")
        result = altar.gate(
            signal="[VOC] GSMB governance sweep — LACP STREP order — kopano kpgs poc",
            source="CF",
            core_result={
                "schema": "lacp_cycle_v1",
                "task_source": "CF",
                "cycle_verdict": "POC_VALIDATED",
                "cycle_hash": "abc123def456",
                "phases_poc": 22,
                "phases_total": 22,
                "ts_start": datetime.now(timezone.utc).isoformat(),
                "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            },
        )
        print(json.dumps({
            "altar_verdict": result["altar_verdict"],
            "layers_pass": result["layers_pass"],
            "commandments": result["commandments"]["verdict"],
            "pillars": result["pillars"]["upheld"],
            "agents": result["agents"]["verdict"],
        }, indent=2))
