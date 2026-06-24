"""
ai_flow_agents.py — The 5 AI Flow Agents + Altar Governance
=============================================================
Implements the 5 Adaptive AI Flows from the THARI H.O.L.O Net as
autonomous agents that govern all GSMB cores through the Altar.

The 5 AI Flows (from public/flows/index.html):
  1. HUE — Mood/Affect/Emotional state adaptation
  2. AGE — Age-adaptive forms (youth/adult/elder)
  3. OFFLINE — Offline resilience (load-shedding/low bandwidth/prepaid)
  4. LANGUAGE — SA language flow (Setswana/isiZulu/isiXhosa/Afrikaans/English)
  5. URGENCY — Urgency gradient (peace/alert/crisis/emergency)

+ WWJD Firewall — the 6th dimension, always active across all flows

Each agent:
  - Upholds assigned Pillars and Commandments
  - Routes through the CLAFP Altar gate
  - Validates POC before any core loop receives adapted output
  - Reports to KC Observer Ledger

Architecture:
  ALTAR (God's Firewall)
    └── AI Flow Agents (5 + WWJD)
        ├── HUE Agent → adapts all UI/UX signals by mood
        ├── AGE Agent → adapts complexity by demographic
        ├── OFFLINE Agent → adapts for load-shedding/connectivity
        ├── LANGUAGE Agent → adapts for SA multilingual context
        ├── URGENCY Agent → adapts priority/hierarchy by crisis level
        └── WWJD Gate → blocks dark patterns across ALL flows
            └── GSMB Cores (via Nexus)

4Ws:
  WHO:   ai_flow_agents.py — 5 AI Flow agents + WWJD gate
  WHAT:  Adaptive governance agents for the Altar
  WHERE: kopano-core/kopano/ — Motor Cortex
  WHY:   32.8% unemployment needs adaptive, sovereign, accessible tech

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

logger = logging.getLogger("ai_flows")

REPO_ROOT = Path(__file__).resolve().parents[2]
FLOWS_LOG = REPO_ROOT / "poc-vs-foc" / "ai_flow_agents_log.jsonl"
FLOWS_LOG.parent.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# FLOW TYPES
# ═══════════════════════════════════════════════════════════════

class FlowType(str, Enum):
    HUE = "HUE"           # Mood / Affect / Emotional State
    AGE = "AGE"           # Youth / Adult / Elder / Accessibility
    OFFLINE = "OFFLINE"   # Load-shedding / Low Bandwidth / Prepaid
    LANGUAGE = "LANGUAGE"  # SA Multilingual — Setswana, isiZulu, etc.
    URGENCY = "URGENCY"   # Peace / Alert / Crisis / Emergency


# ═══════════════════════════════════════════════════════════════
# MOOD / HUE STATES
# ═══════════════════════════════════════════════════════════════

class HueState(str, Enum):
    CALM = "CALM"           # Cool blue, slow animations, spacious layout
    NEUTRAL = "NEUTRAL"     # Default warm amber
    ALERT = "ALERT"         # Orange caution, tighter spacing
    CRISIS = "CRISIS"       # Red urgency, stripped UI, one-tap actions
    JOY = "JOY"             # Warm gold, celebratory micro-animations


class AgeGroup(str, Enum):
    YOUTH = "YOUTH"         # 6-17: gamified, large touch targets, visual
    ADULT = "ADULT"         # 18-59: professional dashboards
    ELDER = "ELDER"         # 60+: high-contrast, large text, voice-first


class ConnectivityState(str, Enum):
    FULL = "FULL"           # Normal broadband/WiFi
    LIMITED = "LIMITED"     # Prepaid data, R50/week budget
    OFFLINE = "OFFLINE"    # Load-shedding, no connectivity
    MESH = "MESH"          # Local mesh network only


class UrgencyLevel(str, Enum):
    PEACE = "PEACE"         # Explore, learn, browse
    ALERT = "ALERT"         # Elevated attention, warnings visible
    CRISIS = "CRISIS"       # Critical actions surface, everything else fades
    EMERGENCY = "EMERGENCY"  # One-tap emergency, zero cognitive load


SA_LANGUAGES = [
    "English", "Afrikaans", "Setswana", "isiZulu", "isiXhosa",
    "Sesotho", "Sepedi", "Tshivenda", "Xitsonga", "isiNdebele", "siSwati",
]


# ═══════════════════════════════════════════════════════════════
# FLOW SIGNAL — input to any flow agent
# ═══════════════════════════════════════════════════════════════

@dataclass
class FlowSignal:
    """A signal entering the AI Flow agent network."""
    content: str
    source: str = "CF"
    hue: str = "NEUTRAL"
    age_group: str = "ADULT"
    connectivity: str = "FULL"
    language: str = "English"
    urgency: str = "PEACE"
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════
# FLOW ADAPTATION RESULT
# ═══════════════════════════════════════════════════════════════

@dataclass
class FlowAdaptation:
    """Result of an AI Flow agent adapting a signal."""
    flow: str
    verdict: str          # ADAPTED / BLOCKED / PASSTHROUGH
    adaptations: dict = field(default_factory=dict)
    wwjd_clean: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# HUE AGENT — Mood/Affect Adaptation
# ═══════════════════════════════════════════════════════════════

class HueAgent:
    """
    Adapts interface color temperature, animation speed, and
    information density based on detected emotional state.
    """
    name = "HUE_AGENT"
    pillars = ["SPIRIT", "MIND", "COMMUNITY"]
    commands = ["CMD-01", "CMD-04", "CMD-06", "CMD-14"]

    HUE_PROFILES = {
        HueState.CALM: {
            "color_temp": "cool_blue", "animation_speed": 0.5,
            "info_density": "spacious", "font_scale": 1.0,
        },
        HueState.NEUTRAL: {
            "color_temp": "warm_amber", "animation_speed": 1.0,
            "info_density": "balanced", "font_scale": 1.0,
        },
        HueState.ALERT: {
            "color_temp": "orange_caution", "animation_speed": 1.5,
            "info_density": "tight", "font_scale": 1.0,
        },
        HueState.CRISIS: {
            "color_temp": "red_urgency", "animation_speed": 2.0,
            "info_density": "stripped", "font_scale": 1.1,
        },
        HueState.JOY: {
            "color_temp": "warm_gold", "animation_speed": 1.2,
            "info_density": "celebratory", "font_scale": 1.0,
        },
    }

    def adapt(self, signal: FlowSignal) -> FlowAdaptation:
        hue = HueState(signal.hue) if signal.hue in HueState.__members__ else HueState.NEUTRAL
        profile = self.HUE_PROFILES[hue]
        return FlowAdaptation(
            flow="HUE", verdict="ADAPTED",
            adaptations={"hue_state": hue.value, **profile},
        )


# ═══════════════════════════════════════════════════════════════
# AGE AGENT — Age-Adaptive Forms
# ═══════════════════════════════════════════════════════════════

class AgeAgent:
    """
    Adapts complexity, touch targets, typography, and interaction
    patterns based on user age group.
    """
    name = "AGE_AGENT"
    pillars = ["COMMUNITY", "MIND", "BODY"]
    commands = ["CMD-04", "CMD-13", "CMD-14", "CMD-15"]

    AGE_PROFILES = {
        AgeGroup.YOUTH: {
            "ui_mode": "gamified", "touch_target_px": 64,
            "font_size": "18px", "icons": "large_colorful",
            "interaction": "swipe_tap", "voice_first": False,
        },
        AgeGroup.ADULT: {
            "ui_mode": "professional", "touch_target_px": 44,
            "font_size": "14px", "icons": "standard",
            "interaction": "click_keyboard", "voice_first": False,
        },
        AgeGroup.ELDER: {
            "ui_mode": "high_contrast", "touch_target_px": 72,
            "font_size": "22px", "icons": "large_simple",
            "interaction": "voice_tap", "voice_first": True,
        },
    }

    def adapt(self, signal: FlowSignal) -> FlowAdaptation:
        age = AgeGroup(signal.age_group) if signal.age_group in AgeGroup.__members__ else AgeGroup.ADULT
        profile = self.AGE_PROFILES[age]
        return FlowAdaptation(
            flow="AGE", verdict="ADAPTED",
            adaptations={"age_group": age.value, **profile},
        )


# ═══════════════════════════════════════════════════════════════
# OFFLINE AGENT — Offline Resilience
# ═══════════════════════════════════════════════════════════════

class OfflineAgent:
    """
    Adapts for load-shedding, low bandwidth, prepaid data budgets.
    When R50 is your weekly data budget, the interface strips to essentials.
    """
    name = "OFFLINE_AGENT"
    pillars = ["BODY", "COMMUNITY", "SOVEREIGNTY"]
    commands = ["CMD-01", "CMD-07", "CMD-10", "CMD-14"]

    CONNECTIVITY_PROFILES = {
        ConnectivityState.FULL: {
            "data_mode": "rich", "images": True, "animations": True,
            "cache_strategy": "standard", "sync_mode": "realtime",
            "compression": False,
        },
        ConnectivityState.LIMITED: {
            "data_mode": "lean", "images": False, "animations": False,
            "cache_strategy": "aggressive", "sync_mode": "batch",
            "compression": True, "data_budget_kb": 500,
        },
        ConnectivityState.OFFLINE: {
            "data_mode": "cached_only", "images": False, "animations": False,
            "cache_strategy": "local_first", "sync_mode": "queue_for_sync",
            "compression": True, "data_budget_kb": 0,
        },
        ConnectivityState.MESH: {
            "data_mode": "mesh_relay", "images": False, "animations": False,
            "cache_strategy": "peer_cache", "sync_mode": "mesh_gossip",
            "compression": True, "data_budget_kb": 100,
        },
    }

    def adapt(self, signal: FlowSignal) -> FlowAdaptation:
        conn = ConnectivityState(signal.connectivity) if signal.connectivity in ConnectivityState.__members__ else ConnectivityState.FULL
        profile = self.CONNECTIVITY_PROFILES[conn]
        return FlowAdaptation(
            flow="OFFLINE", verdict="ADAPTED",
            adaptations={"connectivity": conn.value, **profile},
        )


# ═══════════════════════════════════════════════════════════════
# LANGUAGE AGENT — SA Multilingual Flow
# ═══════════════════════════════════════════════════════════════

class LanguageAgent:
    """
    Adapts for South Africa's 11 official languages.
    MXIT-native communication. EP encoding. Township slang as valid input.
    Code-switching honored, not corrected.
    """
    name = "LANGUAGE_AGENT"
    pillars = ["COMMUNITY", "SPIRIT", "SOVEREIGNTY"]
    commands = ["CMD-01", "CMD-04", "CMD-13", "CMD-15"]

    LANGUAGE_PROFILES = {
        "English": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": False},
        "Afrikaans": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "Setswana": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "isiZulu": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "isiXhosa": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "Sesotho": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "Sepedi": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "Tshivenda": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "Xitsonga": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "isiNdebele": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
        "siSwati": {"direction": "ltr", "script": "latin", "ep_support": True, "mxit_native": True},
    }

    def adapt(self, signal: FlowSignal) -> FlowAdaptation:
        lang = signal.language if signal.language in self.LANGUAGE_PROFILES else "English"
        profile = self.LANGUAGE_PROFILES[lang]
        return FlowAdaptation(
            flow="LANGUAGE", verdict="ADAPTED",
            adaptations={
                "language": lang,
                "code_switching": True,
                "township_slang_valid": True,
                **profile,
            },
        )


# ═══════════════════════════════════════════════════════════════
# URGENCY AGENT — Urgency Gradient
# ═══════════════════════════════════════════════════════════════

class UrgencyAgent:
    """
    Reshuffles information hierarchy in real-time.
    Peace mode: explore. Crisis mode: one-tap emergency.
    """
    name = "URGENCY_AGENT"
    pillars = ["COMMUNITY", "BODY", "SPIRIT"]
    commands = ["CMD-01", "CMD-04", "CMD-05", "CMD-06"]

    URGENCY_PROFILES = {
        UrgencyLevel.PEACE: {
            "mode": "explore", "critical_actions_visible": False,
            "cognitive_load": "normal", "one_tap_emergency": False,
            "information_filter": "none",
        },
        UrgencyLevel.ALERT: {
            "mode": "elevated", "critical_actions_visible": True,
            "cognitive_load": "reduced", "one_tap_emergency": False,
            "information_filter": "warnings_promoted",
        },
        UrgencyLevel.CRISIS: {
            "mode": "crisis", "critical_actions_visible": True,
            "cognitive_load": "minimal", "one_tap_emergency": True,
            "information_filter": "non_critical_hidden",
        },
        UrgencyLevel.EMERGENCY: {
            "mode": "emergency", "critical_actions_visible": True,
            "cognitive_load": "zero", "one_tap_emergency": True,
            "information_filter": "emergency_only",
        },
    }

    def adapt(self, signal: FlowSignal) -> FlowAdaptation:
        urgency = UrgencyLevel(signal.urgency) if signal.urgency in UrgencyLevel.__members__ else UrgencyLevel.PEACE
        profile = self.URGENCY_PROFILES[urgency]
        return FlowAdaptation(
            flow="URGENCY", verdict="ADAPTED",
            adaptations={"urgency_level": urgency.value, **profile},
        )


# ═══════════════════════════════════════════════════════════════
# WWJD GATE — Cross-Flow Firewall
# ═══════════════════════════════════════════════════════════════

class WWJDGate:
    """
    The WWJD Firewall — active across ALL flows.
    Blocks dark patterns, addiction loops, engagement farming.
    If the adaptation would harm the user, it is BLOCKED.

    Truth · Justice · Mercy · Compassion
    """
    name = "WWJD_GATE"
    pillars = ["SPIRIT", "MIND", "COMMUNITY", "SOVEREIGNTY", "BODY"]
    commands = ["CMD-04"]  # WWJD Firewall is CMD-04

    DARK_PATTERNS = [
        "addiction_loop", "engagement_farming", "dark_pattern",
        "infinite_scroll", "notification_spam", "fomo_trigger",
        "predatory_pricing", "data_harvesting", "surveillance",
        "manipulative_design", "forced_continuity", "hidden_costs",
    ]

    def check(self, adaptations: list[FlowAdaptation]) -> FlowAdaptation:
        """Check all flow adaptations against WWJD principles."""
        violations = []
        for adapt in adaptations:
            adapt_str = json.dumps(adapt.adaptations, default=str).lower()
            for pattern in self.DARK_PATTERNS:
                if pattern in adapt_str:
                    violations.append({"flow": adapt.flow, "pattern": pattern})

        if violations:
            return FlowAdaptation(
                flow="WWJD", verdict="BLOCKED",
                adaptations={"violations": violations},
                wwjd_clean=False,
            )

        return FlowAdaptation(
            flow="WWJD", verdict="PASSTHROUGH",
            adaptations={
                "truth": True, "justice": True,
                "mercy": True, "compassion": True,
                "dark_patterns_blocked": 0,
            },
            wwjd_clean=True,
        )


# ═══════════════════════════════════════════════════════════════
# ALTAR FLOW ORCHESTRATOR — Governs all cores through flows
# ═══════════════════════════════════════════════════════════════

class AltarFlowOrchestrator:
    """
    The Altar's AI Flow governance layer.

    Takes a FlowSignal, runs it through all 5 AI Flow agents + WWJD gate,
    produces a unified adaptation profile that governs how GSMB cores
    present their output.

    This is the Altar as God's Firewall — POC validation of adaptive,
    sovereign architecture addressing 32.8% unemployment.
    """

    def __init__(self):
        self.hue = HueAgent()
        self.age = AgeAgent()
        self.offline = OfflineAgent()
        self.language = LanguageAgent()
        self.urgency = UrgencyAgent()
        self.wwjd = WWJDGate()
        self.orchestration_count = 0

    def orchestrate(self, signal: FlowSignal) -> dict:
        """
        Run a signal through all 5 flows + WWJD gate.
        Returns unified adaptation profile.
        """
        self.orchestration_count += 1
        ts = datetime.now(timezone.utc).isoformat()

        # Run all 5 flow agents
        adaptations = [
            self.hue.adapt(signal),
            self.age.adapt(signal),
            self.offline.adapt(signal),
            self.language.adapt(signal),
            self.urgency.adapt(signal),
        ]

        # WWJD gate check across all adaptations
        wwjd_result = self.wwjd.check(adaptations)

        # Merge all adaptations into unified profile
        unified = {}
        for a in adaptations:
            unified[a.flow.lower()] = a.adaptations

        # Overall verdict
        all_adapted = all(a.verdict == "ADAPTED" for a in adaptations)
        wwjd_clean = wwjd_result.wwjd_clean

        if all_adapted and wwjd_clean:
            verdict = "FLOWS_POC_VALIDATED"
        elif all_adapted and not wwjd_clean:
            verdict = "FLOWS_WWJD_BLOCKED"
        else:
            verdict = "FLOWS_PARTIAL"

        result = {
            "schema": "altar_flow_orchestration_v1",
            "ts": ts,
            "orchestration": self.orchestration_count,
            "signal_source": signal.source,
            "signal_preview": signal.content[:100],
            "flows_adapted": len([a for a in adaptations if a.verdict == "ADAPTED"]),
            "flows_total": 5,
            "wwjd": wwjd_result.to_dict(),
            "unified_profile": unified,
            "verdict": verdict,
            "flow_hash": hashlib.sha256(
                f"{ts}:{self.orchestration_count}:{verdict}".encode()
            ).hexdigest()[:16],
            "pillars_covered": list(set(
                p for agent in [self.hue, self.age, self.offline, self.language, self.urgency, self.wwjd]
                for p in agent.pillars
            )),
            "commands_covered": list(set(
                c for agent in [self.hue, self.age, self.offline, self.language, self.urgency, self.wwjd]
                for c in agent.commands
            )),
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        # Log
        with FLOWS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, default=str, ensure_ascii=False) + "\n")

        logger.info("[FLOWS] Orchestration #%d: %s | %d/5 adapted | WWJD=%s",
                    self.orchestration_count, verdict,
                    result["flows_adapted"], "CLEAN" if wwjd_clean else "BLOCKED")

        return result

    def orchestrate_for_core(self, signal: FlowSignal, core_result: dict) -> dict:
        """
        Adapt a GSMB core result through the 5 AI Flows.
        Used by the Nexus to apply adaptive presentation to core output.
        """
        flow_result = self.orchestrate(signal)

        return {
            "core_verdict": core_result.get("cycle_verdict", core_result.get("pipeline_verdict", "UNKNOWN")),
            "flow_verdict": flow_result["verdict"],
            "unified_profile": flow_result["unified_profile"],
            "presentation": {
                "color_temp": flow_result["unified_profile"].get("hue", {}).get("color_temp", "warm_amber"),
                "font_size": flow_result["unified_profile"].get("age", {}).get("font_size", "14px"),
                "data_mode": flow_result["unified_profile"].get("offline", {}).get("data_mode", "rich"),
                "language": flow_result["unified_profile"].get("language", {}).get("language", "English"),
                "urgency_mode": flow_result["unified_profile"].get("urgency", {}).get("mode", "explore"),
            },
        }


# ═══════════════════════════════════════════════════════════════
# KC OBSERVER LEDGER — Records all agent state
# ═══════════════════════════════════════════════════════════════

class KCObserverLedger:
    """
    KC (Seat 1) Observer Ledger.
    Records the state of all agents — stateful and stateless —
    and validates they uphold 15 Commands and 5 Pillars.
    """

    def __init__(self):
        self.entries: list[dict] = []

    def observe(self, agents: list[Any]) -> dict:
        """
        Observe all agents and record their pillar/command coverage.
        """
        ts = datetime.now(timezone.utc).isoformat()
        observations = []

        for agent in agents:
            name = getattr(agent, "name", agent.__class__.__name__)
            pillars = getattr(agent, "pillars", [])
            commands = getattr(agent, "commands", [])
            observations.append({
                "agent": name,
                "pillars": pillars,
                "pillars_count": len(pillars),
                "commands": commands,
                "commands_count": len(commands),
                "upholds": len(pillars) >= 2 and len(commands) >= 1,
            })

        all_uphold = all(o["upholds"] for o in observations)
        all_pillars = list(set(p for o in observations for p in o["pillars"]))
        all_commands = list(set(c for o in observations for c in o["commands"]))

        result = {
            "schema": "kc_observer_ledger_v1",
            "ts": ts,
            "agents_observed": len(observations),
            "observations": observations,
            "all_uphold": all_uphold,
            "total_pillars_covered": len(all_pillars),
            "total_commands_covered": len(all_commands),
            "pillars_list": sorted(all_pillars),
            "commands_list": sorted(all_commands),
            "five_pillars_covered": len(all_pillars) == 5,
            "verdict": "KC_LEDGER_VALIDATED" if all_uphold and len(all_pillars) == 5 else "KC_LEDGER_PARTIAL",
        }

        self.entries.append(result)
        return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(description="AI Flow Agents — Altar Governance")
    parser.add_argument("--hue", default="NEUTRAL", choices=[h.value for h in HueState])
    parser.add_argument("--age", default="ADULT", choices=[a.value for a in AgeGroup])
    parser.add_argument("--connectivity", default="FULL", choices=[c.value for c in ConnectivityState])
    parser.add_argument("--language", default="English")
    parser.add_argument("--urgency", default="PEACE", choices=[u.value for u in UrgencyLevel])
    parser.add_argument("--observe", action="store_true", help="Run KC Observer Ledger")
    args = parser.parse_args()

    orchestrator = AltarFlowOrchestrator()

    signal = FlowSignal(
        content="[VOC] AI Flow test — sovereign adaptive architecture",
        source="CF",
        hue=args.hue,
        age_group=args.age,
        connectivity=args.connectivity,
        language=args.language,
        urgency=args.urgency,
    )

    result = orchestrator.orchestrate(signal)
    print(json.dumps({
        "verdict": result["verdict"],
        "flows_adapted": result["flows_adapted"],
        "pillars_covered": len(result["pillars_covered"]),
        "commands_covered": len(result["commands_covered"]),
        "profile": result["unified_profile"],
    }, indent=2))

    if args.observe:
        ledger = KCObserverLedger()
        agents = [orchestrator.hue, orchestrator.age, orchestrator.offline,
                  orchestrator.language, orchestrator.urgency, orchestrator.wwjd]
        obs = ledger.observe(agents)
        print(json.dumps({
            "kc_verdict": obs["verdict"],
            "agents": obs["agents_observed"],
            "all_uphold": obs["all_uphold"],
            "pillars": obs["total_pillars_covered"],
            "commands": obs["total_commands_covered"],
        }, indent=2))
