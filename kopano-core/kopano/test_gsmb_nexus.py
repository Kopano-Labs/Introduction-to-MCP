"""
test_gsmb_nexus.py — STAP 054-056: GSMB Nexus Integration Tests
=================================================================
Tests the unified KPCB+ → LACP → CLAFP pipeline.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.gsmb_nexus import GSMBNexus
from kopano.kpcb_runtime_enforcer import KPCBPlusRuntime, Channel, KPCB_FORMULA, NSO_REGISTRY


# ═══════════════════════════════════════════════════════════════
# STAP 054: KPCB+ Compilation Channel Tests
# ═══════════════════════════════════════════════════════════════

class TestKPCBChannels:
    """STAP 054: Individual channel compilation."""

    def setup_method(self):
        self.rt = KPCBPlusRuntime()

    def test_has_7_channels(self):
        assert len(Channel) == 7

    def test_formula_correct(self):
        assert "KPCB+" in KPCB_FORMULA

    def test_nso_registry_has_7(self):
        assert len(NSO_REGISTRY) == 7

    def test_pp_classifies_voc(self):
        r = self.rt._compile_pp("[VOC] governance sweep")
        assert r.verdict == "COMPILED"
        assert r.data["intent_type"] == "VOC_WRAPPED"

    def test_pp_classifies_action(self):
        r = self.rt._compile_pp("deploy the careers page now")
        assert r.data["intent_type"] == "ACTION_INTENT"

    def test_bp_compiles(self):
        r = self.rt._compile_bp("[VOC] test bracket protocol")
        assert r.verdict == "COMPILED"

    def test_ep_encodes_emojis(self):
        r = self.rt._compile_ep("[VOC] deploy poc governance test sweep")
        assert r.verdict == "COMPILED"
        assert len(r.data["ep_string"]) > 0

    def test_gp_validates_4ws(self):
        r = self.rt._compile_gp("governance sweep", "CF")
        assert r.verdict == "COMPILED"
        assert r.data["four_ws"]["who"] == "CF"

    def test_sp_clean_passes(self):
        r = self.rt._compile_sp("[VOC] clean governance signal")
        assert r.verdict == "COMPILED"
        assert r.data["dlp_clean"] is True

    def test_sp_rejects_dlp(self):
        r = self.rt._compile_sp("here is my password and secret")
        assert r.verdict == "REJECTED"

    def test_sp_rejects_extractive(self):
        r = self.rt._compile_sp("steal and exploit data")
        assert r.verdict == "REJECTED"

    def test_dp_classifies(self):
        r = self.rt._compile_dp("deploy push to production kopano")
        assert r.verdict == "COMPILED"
        assert r.data["telemetry_type"] == "DEPLOYMENT"

    def test_ip_maps_cf(self):
        r = self.rt._compile_ip("CF")
        assert r.data["lpm_pattern"] == "LPM_FACILITATE"

    def test_ip_maps_sse(self):
        r = self.rt._compile_ip("SSE")
        assert r.data["lpm_pattern"] == "LPM_MASTER"


class TestKPCBCompilation:
    """STAP 054: Full 7-channel compilation."""

    def setup_method(self):
        self.rt = KPCBPlusRuntime()

    def test_clean_compiles(self):
        r = self.rt.compile("[VOC] governance sweep kopano", "CF")
        assert r["compilation_verdict"] == "KPCB_COMPILED"
        assert r["channels_compiled"] == 7

    def test_malicious_rejected(self):
        r = self.rt.compile("steal password secret exploit", "CF")
        assert r["compilation_verdict"] == "KPCB_REJECTED"
        assert r["channels_rejected"] > 0

    def test_has_schema(self):
        r = self.rt.compile("[VOC] test", "CF")
        assert r["schema"] == "kpcb_compilation_v1"

    def test_has_hash(self):
        r = self.rt.compile("[VOC] test", "CF")
        assert len(r["compilation_hash"]) == 16

    def test_tracks_tokens(self):
        self.rt.compile("one two three four five", "CF")
        assert self.rt.tokens_used == 5

    def test_compilation_count_increments(self):
        self.rt.compile("a", "CF")
        self.rt.compile("b", "CF")
        assert self.rt.compilation_count == 2


# ═══════════════════════════════════════════════════════════════
# STAP 055: Nexus Single-Task Pipeline Tests
# ═══════════════════════════════════════════════════════════════

class TestNexusSingleTask:
    """STAP 055: Full KPCB+ → LACP → CLAFP pipeline."""

    def setup_method(self):
        self.nexus = GSMBNexus(auto_commit=False)

    def test_cf_task_validates(self):
        r = self.nexus.process(
            task="[VOC] Secure Freddy Lucerne Farm Matrix — sovereign governance kopano kpgs community body spirit mind",
            source="CF",
        )
        assert r["pipeline_verdict"] in ("FULL_POC_VALIDATED", "PARTIAL_ALTAR_HOLD")

    def test_has_all_three_engines(self):
        r = self.nexus.process("[VOC] test task governance sovereign spirit body mind community", "CF")
        assert r["kpcb"] is not None
        assert r["lacp"] is not None
        assert r["clafp"] is not None

    def test_kpcb_compiled(self):
        r = self.nexus.process("[VOC] governance task kopano", "CF")
        assert r["kpcb"]["verdict"] == "KPCB_COMPILED"

    def test_lacp_poc(self):
        r = self.nexus.process("[VOC] lacp strep order test", "CF")
        assert r["lacp"]["verdict"] == "POC_VALIDATED"
        assert r["lacp"]["poc"] == 22
        assert r["lacp"]["foc"] == 0

    def test_clafp_validates(self):
        r = self.nexus.process(
            "[VOC] altar gate test sovereign governance kopano spirit body mind community",
            "CF",
        )
        assert r["clafp"]["verdict"] in ("ALTAR_POC_VALIDATED", "ALTAR_PARTIAL")

    def test_malicious_rejected_at_kpcb(self):
        r = self.nexus.process("steal password exploit secret", "CF")
        assert r["pipeline_verdict"] == "REJECTED_AT_KPCB"
        assert r["lacp"] is None
        assert r["clafp"] is None

    def test_has_constraint(self):
        r = self.nexus.process("[VOC] test", "CF")
        assert r["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_cycle_count(self):
        self.nexus.process("[VOC] a", "CF")
        self.nexus.process("[VOC] b", "CF")
        assert self.nexus.cycle_count == 2

    def test_custom_nso_group(self):
        r = self.nexus.process("[VOC] kasilink task", "CF", nso_group="GSPMB-KL")
        assert r["pipeline_verdict"] != "REJECTED_AT_KPCB"


# ═══════════════════════════════════════════════════════════════
# STAP 056: Nexus All-NSO Sweep Tests
# ═══════════════════════════════════════════════════════════════

class TestNexusAllNSO:
    """STAP 056: Full sweep across all 7 NSO groups."""

    def setup_method(self):
        self.nexus = GSMBNexus(auto_commit=False)

    def test_all_nso_returns_7(self):
        r = self.nexus.process_all_nso("[VOC] Full sweep governance")
        assert r["nso_groups"] == 7

    def test_all_nso_has_verdicts(self):
        r = self.nexus.process_all_nso("[VOC] sweep test kopano")
        assert len(r["nso_verdicts"]) == 7

    def test_all_nso_groups_named(self):
        r = self.nexus.process_all_nso("[VOC] names test")
        names = list(r["nso_verdicts"].keys())
        assert "GSMB-MAIN" in names
        assert "GSPMB-CC" in names
        assert "GSPMB-FF" in names

    def test_kpcb_compiled_for_sweep(self):
        r = self.nexus.process_all_nso("[VOC] compile test kopano")
        assert r["kpcb_verdict"] == "KPCB_COMPILED"

    def test_has_constraint(self):
        r = self.nexus.process_all_nso("[VOC] constraint check")
        assert r["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_overall_verdict_exists(self):
        r = self.nexus.process_all_nso("[VOC] verdict test")
        assert r["overall_verdict"] in ("ALL_NSO_POC_VALIDATED", "NSO_PARTIAL")


# ═══════════════════════════════════════════════════════════════
# STAP 054-056: KPCB+ Full Pipeline Integration
# ═══════════════════════════════════════════════════════════════

class TestKPCBFullPipeline:
    """Integration: KPCB+ compile_and_execute method."""

    def test_full_pipeline(self):
        from kopano.kpcb_runtime_enforcer import execute_anso
        r = execute_anso(
            target_task="[VOC] Sync Water Tensors under Solid Rock Synergy — governance kopano sovereign spirit body mind community",
            source="CF",
        )
        assert r["pipeline_verdict"] in ("FULL_POC_VALIDATED", "PARTIAL_ALTAR_HOLD")

    def test_anso_returns_all_engines(self):
        from kopano.kpcb_runtime_enforcer import execute_anso
        r = execute_anso("[VOC] ANSO test governance", "CF")
        assert "kpcb" in r
        assert "lacp" in r
        assert "clafp" in r
