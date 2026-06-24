"""
test_ai_flow_agents.py — STAP 057-062: AI Flow Agent Tests
============================================================
Tests for all 5 AI Flow agents + WWJD gate + Orchestrator + KC Ledger.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.ai_flow_agents import (
    FlowType, HueState, AgeGroup, ConnectivityState, UrgencyLevel,
    SA_LANGUAGES, FlowSignal, FlowAdaptation,
    HueAgent, AgeAgent, OfflineAgent, LanguageAgent, UrgencyAgent,
    WWJDGate, AltarFlowOrchestrator, KCObserverLedger,
)


# ═══════════════════════════════════════════════════════════════
# STAP 057: Flow Types & Enums
# ═══════════════════════════════════════════════════════════════

class TestFlowEnums:
    def test_5_flow_types(self):
        assert len(FlowType) == 5

    def test_5_hue_states(self):
        assert len(HueState) == 5

    def test_3_age_groups(self):
        assert len(AgeGroup) == 3

    def test_4_connectivity_states(self):
        assert len(ConnectivityState) == 4

    def test_4_urgency_levels(self):
        assert len(UrgencyLevel) == 4

    def test_11_sa_languages(self):
        assert len(SA_LANGUAGES) == 11
        assert "Setswana" in SA_LANGUAGES
        assert "isiZulu" in SA_LANGUAGES
        assert "isiXhosa" in SA_LANGUAGES


class TestFlowSignal:
    def test_default_signal(self):
        s = FlowSignal(content="test")
        assert s.source == "CF"
        assert s.hue == "NEUTRAL"
        assert s.age_group == "ADULT"

    def test_custom_signal(self):
        s = FlowSignal(content="test", hue="CRISIS", language="Setswana")
        assert s.hue == "CRISIS"
        assert s.language == "Setswana"


# ═══════════════════════════════════════════════════════════════
# STAP 058: Individual Flow Agent Tests
# ═══════════════════════════════════════════════════════════════

class TestHueAgent:
    def setup_method(self):
        self.agent = HueAgent()

    def test_calm_adaptation(self):
        r = self.agent.adapt(FlowSignal(content="test", hue="CALM"))
        assert r.verdict == "ADAPTED"
        assert r.adaptations["color_temp"] == "cool_blue"

    def test_crisis_adaptation(self):
        r = self.agent.adapt(FlowSignal(content="test", hue="CRISIS"))
        assert r.adaptations["color_temp"] == "red_urgency"
        assert r.adaptations["info_density"] == "stripped"

    def test_joy_adaptation(self):
        r = self.agent.adapt(FlowSignal(content="test", hue="JOY"))
        assert r.adaptations["color_temp"] == "warm_gold"

    def test_has_pillars(self):
        assert len(self.agent.pillars) >= 2

    def test_has_commands(self):
        assert len(self.agent.commands) >= 1


class TestAgeAgent:
    def setup_method(self):
        self.agent = AgeAgent()

    def test_youth_gamified(self):
        r = self.agent.adapt(FlowSignal(content="test", age_group="YOUTH"))
        assert r.adaptations["ui_mode"] == "gamified"
        assert r.adaptations["touch_target_px"] == 64

    def test_elder_high_contrast(self):
        r = self.agent.adapt(FlowSignal(content="test", age_group="ELDER"))
        assert r.adaptations["ui_mode"] == "high_contrast"
        assert r.adaptations["voice_first"] is True
        assert r.adaptations["font_size"] == "22px"

    def test_adult_professional(self):
        r = self.agent.adapt(FlowSignal(content="test", age_group="ADULT"))
        assert r.adaptations["ui_mode"] == "professional"

    def test_has_pillars(self):
        assert "COMMUNITY" in self.agent.pillars


class TestOfflineAgent:
    def setup_method(self):
        self.agent = OfflineAgent()

    def test_full_connectivity(self):
        r = self.agent.adapt(FlowSignal(content="test", connectivity="FULL"))
        assert r.adaptations["images"] is True
        assert r.adaptations["data_mode"] == "rich"

    def test_offline_strips(self):
        r = self.agent.adapt(FlowSignal(content="test", connectivity="OFFLINE"))
        assert r.adaptations["images"] is False
        assert r.adaptations["data_mode"] == "cached_only"
        assert r.adaptations["data_budget_kb"] == 0

    def test_limited_compresses(self):
        r = self.agent.adapt(FlowSignal(content="test", connectivity="LIMITED"))
        assert r.adaptations["compression"] is True
        assert r.adaptations["sync_mode"] == "batch"

    def test_mesh_relay(self):
        r = self.agent.adapt(FlowSignal(content="test", connectivity="MESH"))
        assert r.adaptations["data_mode"] == "mesh_relay"
        assert r.adaptations["sync_mode"] == "mesh_gossip"

    def test_has_sovereignty_pillar(self):
        assert "SOVEREIGNTY" in self.agent.pillars


class TestLanguageAgent:
    def setup_method(self):
        self.agent = LanguageAgent()

    def test_setswana(self):
        r = self.agent.adapt(FlowSignal(content="test", language="Setswana"))
        assert r.adaptations["language"] == "Setswana"
        assert r.adaptations["mxit_native"] is True

    def test_english(self):
        r = self.agent.adapt(FlowSignal(content="test", language="English"))
        assert r.adaptations["language"] == "English"

    def test_code_switching_honored(self):
        r = self.agent.adapt(FlowSignal(content="test", language="isiZulu"))
        assert r.adaptations["code_switching"] is True

    def test_township_slang_valid(self):
        r = self.agent.adapt(FlowSignal(content="test", language="isiXhosa"))
        assert r.adaptations["township_slang_valid"] is True

    def test_supports_all_11(self):
        for lang in SA_LANGUAGES:
            r = self.agent.adapt(FlowSignal(content="test", language=lang))
            assert r.verdict == "ADAPTED"
            assert r.adaptations["language"] == lang

    def test_fallback_to_english(self):
        r = self.agent.adapt(FlowSignal(content="test", language="Klingon"))
        assert r.adaptations["language"] == "English"


class TestUrgencyAgent:
    def setup_method(self):
        self.agent = UrgencyAgent()

    def test_peace_mode(self):
        r = self.agent.adapt(FlowSignal(content="test", urgency="PEACE"))
        assert r.adaptations["mode"] == "explore"
        assert r.adaptations["one_tap_emergency"] is False

    def test_emergency_mode(self):
        r = self.agent.adapt(FlowSignal(content="test", urgency="EMERGENCY"))
        assert r.adaptations["mode"] == "emergency"
        assert r.adaptations["one_tap_emergency"] is True
        assert r.adaptations["cognitive_load"] == "zero"

    def test_crisis_strips(self):
        r = self.agent.adapt(FlowSignal(content="test", urgency="CRISIS"))
        assert r.adaptations["information_filter"] == "non_critical_hidden"


# ═══════════════════════════════════════════════════════════════
# STAP 059: WWJD Gate Tests
# ═══════════════════════════════════════════════════════════════

class TestWWJDGate:
    def setup_method(self):
        self.gate = WWJDGate()

    def test_clean_adaptations_pass(self):
        adaptations = [
            FlowAdaptation(flow="HUE", verdict="ADAPTED", adaptations={"color": "blue"}),
            FlowAdaptation(flow="AGE", verdict="ADAPTED", adaptations={"mode": "adult"}),
        ]
        r = self.gate.check(adaptations)
        assert r.verdict == "PASSTHROUGH"
        assert r.wwjd_clean is True

    def test_has_all_5_pillars(self):
        assert len(self.gate.pillars) == 5

    def test_has_dark_patterns_list(self):
        assert len(self.gate.DARK_PATTERNS) > 0
        assert "addiction_loop" in self.gate.DARK_PATTERNS


# ═══════════════════════════════════════════════════════════════
# STAP 060: Altar Flow Orchestrator Tests
# ═══════════════════════════════════════════════════════════════

class TestAltarFlowOrchestrator:
    def setup_method(self):
        self.orch = AltarFlowOrchestrator()

    def test_default_orchestration(self):
        r = self.orch.orchestrate(FlowSignal(content="test"))
        assert r["verdict"] == "FLOWS_POC_VALIDATED"
        assert r["flows_adapted"] == 5

    def test_crisis_elder_offline_setswana_emergency(self):
        signal = FlowSignal(
            content="[VOC] Crisis in Dunoon",
            hue="CRISIS", age_group="ELDER",
            connectivity="OFFLINE", language="Setswana",
            urgency="EMERGENCY",
        )
        r = self.orch.orchestrate(signal)
        assert r["verdict"] == "FLOWS_POC_VALIDATED"
        profile = r["unified_profile"]
        assert profile["hue"]["color_temp"] == "red_urgency"
        assert profile["age"]["voice_first"] is True
        assert profile["offline"]["data_mode"] == "cached_only"
        assert profile["language"]["language"] == "Setswana"
        assert profile["urgency"]["one_tap_emergency"] is True

    def test_covers_all_5_pillars(self):
        r = self.orch.orchestrate(FlowSignal(content="test"))
        assert len(r["pillars_covered"]) == 5

    def test_covers_commands(self):
        r = self.orch.orchestrate(FlowSignal(content="test"))
        assert len(r["commands_covered"]) >= 5

    def test_has_schema(self):
        r = self.orch.orchestrate(FlowSignal(content="test"))
        assert r["schema"] == "altar_flow_orchestration_v1"

    def test_has_hash(self):
        r = self.orch.orchestrate(FlowSignal(content="test"))
        assert len(r["flow_hash"]) == 16

    def test_has_constraint(self):
        r = self.orch.orchestrate(FlowSignal(content="test"))
        assert r["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_orchestration_count(self):
        self.orch.orchestrate(FlowSignal(content="a"))
        self.orch.orchestrate(FlowSignal(content="b"))
        assert self.orch.orchestration_count == 2


# ═══════════════════════════════════════════════════════════════
# STAP 061: KC Observer Ledger Tests
# ═══════════════════════════════════════════════════════════════

class TestKCObserverLedger:
    def setup_method(self):
        self.ledger = KCObserverLedger()
        self.orch = AltarFlowOrchestrator()

    def test_observe_all_flow_agents(self):
        agents = [self.orch.hue, self.orch.age, self.orch.offline,
                  self.orch.language, self.orch.urgency, self.orch.wwjd]
        r = self.ledger.observe(agents)
        assert r["verdict"] == "KC_LEDGER_VALIDATED"
        assert r["all_uphold"] is True
        assert r["agents_observed"] == 6

    def test_all_5_pillars_covered(self):
        agents = [self.orch.hue, self.orch.age, self.orch.offline,
                  self.orch.language, self.orch.urgency, self.orch.wwjd]
        r = self.ledger.observe(agents)
        assert r["five_pillars_covered"] is True
        assert r["total_pillars_covered"] == 5

    def test_commands_covered(self):
        agents = [self.orch.hue, self.orch.age, self.orch.offline,
                  self.orch.language, self.orch.urgency, self.orch.wwjd]
        r = self.ledger.observe(agents)
        assert r["total_commands_covered"] >= 5

    def test_entries_appended(self):
        agents = [self.orch.hue]
        self.ledger.observe(agents)
        self.ledger.observe(agents)
        assert len(self.ledger.entries) == 2


# ═══════════════════════════════════════════════════════════════
# STAP 062: Orchestrate For Core Integration
# ═══════════════════════════════════════════════════════════════

class TestOrchestrateForCore:
    def test_adapts_core_result(self):
        orch = AltarFlowOrchestrator()
        signal = FlowSignal(content="test", hue="CALM", language="isiZulu", urgency="ALERT")
        core_result = {"cycle_verdict": "POC_VALIDATED", "phases_poc": 22}
        r = orch.orchestrate_for_core(signal, core_result)
        assert r["core_verdict"] == "POC_VALIDATED"
        assert r["flow_verdict"] == "FLOWS_POC_VALIDATED"
        assert r["presentation"]["language"] == "isiZulu"
        assert r["presentation"]["color_temp"] == "cool_blue"
