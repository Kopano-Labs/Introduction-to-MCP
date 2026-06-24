"""
test_clafp_altar.py — Tests for CLAFP Altar Core
==================================================
Tests the Altar's 3 AI Layers, 15 Commandments, 5 Pillars, Agent uphold.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.clafp_altar_core import (
    CLAFPAltarCore, AltarLayer, Pillar,
    COMMANDMENTS, PILLAR_SCRIPTURES, LAYER_SCRIPTURES,
    NAMED_AGENTS, AgentProfile,
)


class TestCommandments:
    def test_has_15_commandments(self):
        assert len(COMMANDMENTS) == 15

    def test_all_prefixed_cmd(self):
        for k in COMMANDMENTS:
            assert k.startswith("CMD-")

    def test_ground_truth_first(self):
        assert "Ground Truth" in COMMANDMENTS["CMD-01"]

    def test_wwjd_firewall(self):
        assert "WWJD" in COMMANDMENTS["CMD-04"]

    def test_receipt_or_hold(self):
        assert "Receipt" in COMMANDMENTS["CMD-08"]


class TestPillars:
    def test_has_5_pillars(self):
        assert len(Pillar) == 5

    def test_pillar_names(self):
        names = [p.value for p in Pillar]
        assert "SPIRIT" in names
        assert "BODY" in names
        assert "MIND" in names
        assert "COMMUNITY" in names
        assert "SOVEREIGNTY" in names

    def test_all_pillars_have_scriptures(self):
        for p in Pillar:
            assert p in PILLAR_SCRIPTURES


class TestAltarLayers:
    def test_has_3_layers(self):
        assert len(AltarLayer) == 3

    def test_layer_names(self):
        assert AltarLayer.GUARDIAN.value == "GUARDIAN"
        assert AltarLayer.NATURAL.value == "NATURAL"
        assert AltarLayer.TELEMETRY.value == "TELEMETRY"

    def test_all_layers_have_scriptures(self):
        for l in AltarLayer:
            assert l in LAYER_SCRIPTURES


class TestNamedAgents:
    def test_has_10_agents(self):
        assert len(NAMED_AGENTS) == 10

    def test_kc_is_seat_1(self):
        kc = [a for a in NAMED_AGENTS if a.name == "KC"][0]
        assert kc.seat == 1

    def test_antigravity_is_seat_10(self):
        ag = [a for a in NAMED_AGENTS if a.name == "ANTIGRAVITY"][0]
        assert ag.seat == 10

    def test_ag_is_stateless(self):
        ag = [a for a in NAMED_AGENTS if a.name == "ANTIGRAVITY"][0]
        assert ag.agent_type == "STATELESS"

    def test_kc_upholds_all_pillars(self):
        kc = [a for a in NAMED_AGENTS if a.name == "KC"][0]
        assert len(kc.pillars_upheld) == 5

    def test_all_agents_have_lpm_pattern(self):
        for a in NAMED_AGENTS:
            assert a.lpm_pattern.startswith("LPM_") or a.lpm_pattern.startswith("LPH_")


class TestGuardianLayer:
    def setup_method(self):
        self.altar = CLAFPAltarCore()

    def test_clean_signal_passes(self):
        r = self.altar._gate_guardian("[VOC] governance sweep kopano", "CF")
        assert r.verdict == "PASS"

    def test_extractive_signal_fails(self):
        r = self.altar._gate_guardian("steal data from users exploit them", "CF")
        assert r.verdict == "FAIL"
        assert r.data["reason"] == "WWJD_VIOLATION"

    def test_invalid_source_holds(self):
        r = self.altar._gate_guardian("[VOC] sweep", "RANDOM_SOURCE")
        assert r.verdict == "HOLD"
        assert r.data["reason"] == "JETHRO_DELEGATION_MISSING"


class TestNaturalLayer:
    def setup_method(self):
        self.altar = CLAFPAltarCore()

    def test_good_provenance_passes(self):
        r = self.altar._gate_natural("[VOC] gsmb poc governance sweep", "CF")
        assert r.verdict == "PASS"

    def test_provenance_score_calculated(self):
        r = self.altar._gate_natural("[VOC] gsmb poc governance", "CF")
        assert r.data["provenance_score"] >= 2


class TestTelemetryLayer:
    def setup_method(self):
        self.altar = CLAFPAltarCore()

    def test_clean_signal_passes(self):
        r = self.altar._gate_telemetry("lacp strep cycle 1", "CF")
        assert r.verdict == "PASS"
        assert r.data["signal_class"] == "CORE_LOOP_TELEMETRY"

    def test_dlp_violation_fails(self):
        r = self.altar._gate_telemetry("here is my password and secret token", "CF")
        assert r.verdict == "FAIL"
        assert r.data["reason"] == "DLP_VIOLATION"

    def test_classifies_deployment(self):
        r = self.altar._gate_telemetry("commit push deploy careers page", "CF")
        assert r.data["signal_class"] == "DEPLOYMENT_ACTION"


class TestCommandmentsCheck:
    def setup_method(self):
        self.altar = CLAFPAltarCore()
        self.good_result = {
            "schema": "lacp_cycle_v1",
            "task_source": "CF",
            "cycle_verdict": "POC_VALIDATED",
            "cycle_hash": "abc123",
            "phases_poc": 22,
            "phases_total": 22,
            "ts_start": "2026-06-24T00:00:00Z",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "phases": [{"phase": "X"}],
            "tick": 1,
        }

    def test_good_result_upholds(self):
        r = self.altar.check_commandments(self.good_result)
        assert r["verdict"] == "COMMANDMENTS_UPHELD"

    def test_empty_result_partial(self):
        r = self.altar.check_commandments({})
        assert r["verdict"] == "COMMANDMENTS_PARTIAL"


class TestPillarsCheck:
    def setup_method(self):
        self.altar = CLAFPAltarCore()

    def test_sovereign_result_has_pillars(self):
        r = self.altar.check_pillars({
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "nso_group": "GSMB-MAIN",
            "schema": "lacp_cycle_v1",
            "cycle_verdict": "POC_VALIDATED",
        })
        assert r["upheld"] >= 2


class TestAgentUphold:
    def setup_method(self):
        self.altar = CLAFPAltarCore()

    def test_all_agents_uphold(self):
        r = self.altar.check_agents_uphold()
        assert r["all_uphold"] is True
        assert r["total_agents"] == 10

    def test_has_stateful_and_stateless(self):
        r = self.altar.check_agents_uphold()
        assert r["stateful_count"] == 9
        assert r["stateless_count"] == 1


class TestFullAltarGate:
    def setup_method(self):
        self.altar = CLAFPAltarCore()
        self.core_result = {
            "schema": "lacp_cycle_v1",
            "task_source": "CF",
            "cycle_verdict": "POC_VALIDATED",
            "cycle_hash": "abc123def456",
            "phases_poc": 22,
            "phases_total": 22,
            "ts_start": "2026-06-24T00:00:00Z",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "phases": [{"phase": "X"}],
        }

    def test_clean_gate_validates(self):
        r = self.altar.gate(
            signal="[VOC] GSMB governance sweep kopano kpgs poc sovereign community body mind spirit altar",
            source="CF",
            core_result=self.core_result,
        )
        assert r["altar_verdict"] == "ALTAR_POC_VALIDATED"

    def test_has_hebrews_13_8(self):
        r = self.altar.gate(
            signal="[VOC] sweep", source="CF",
            core_result=self.core_result,
        )
        assert "yesterday" in r["hebrews_13_8"]

    def test_has_constraint(self):
        r = self.altar.gate(
            signal="[VOC] sweep", source="CF",
            core_result=self.core_result,
        )
        assert r["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_has_altar_hash(self):
        r = self.altar.gate(
            signal="[VOC] sweep", source="CF",
            core_result=self.core_result,
        )
        assert len(r["altar_hash"]) == 16

    def test_extractive_fails_altar(self):
        r = self.altar.gate(
            signal="steal exploit extract harm users",
            source="CF",
            core_result=self.core_result,
        )
        assert r["altar_verdict"] != "ALTAR_POC_VALIDATED"
        assert r["layers"]["guardian"]["verdict"] == "FAIL"


class TestValidateCore:
    def setup_method(self):
        self.altar = CLAFPAltarCore()

    def test_validate_lacp_result(self):
        from kopano.lacp_autonomous_core import spawn_nso_core
        result = spawn_nso_core(
            nso_group_id="CLAFP-TEST",
            task_source="CF",
            task_payload="[VOC] Altar validation test",
            auto_commit=False,
        )
        ar = self.altar.validate_core("LACP-CLAFP-TEST", result)
        assert ar["altar_verdict"] == "ALTAR_POC_VALIDATED"
