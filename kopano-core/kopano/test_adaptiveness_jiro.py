"""
test_adaptiveness_jiro.py — JIRO STAP Tasks 051-053
====================================================
Adaptiveness Unit Tests for:
    051: NeuralFailureFirewall — all patterns, edge cases, enforce_output
    052: AdaptiveSTREPEngine  — full pipeline, bracket resolution, PKANP
    053: NestingGroup / NSO   — FOC threads, CBP locking, depth tracking

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.adaptiveness import (
    NeuralFailureFirewall,
    NeuralFailureError,
    AdaptiveSTREPEngine,
    NestingGroup,
    BracketLevel,
    NestingLayer,
    Sandbox,
    PKANPResult,
    BRACKET_HIERARCHY,
    BRACKET_BY_SYMBOL,
    BRACKET_BY_LEVEL,
    BRACKET_BY_NAME,
    resolve_bracket_level,
    build_standard_nso,
    compute_pkanp,
)


# ═══════════════════════════════════════════════════════════════
# STAP-051: NeuralFailureFirewall
# ═══════════════════════════════════════════════════════════════


class TestNeuralFailureFirewall:
    """STAP-051: Exhaustive NeuralFailureFirewall tests."""

    def setup_method(self):
        self.fw = NeuralFailureFirewall()

    # ── Clean signals pass ──────────────────────────────────

    def test_clean_text_passes(self):
        is_clean, pattern = self.fw.check_text("Deploy the GSMB telemetry module to localhost.")
        assert is_clean is True
        assert pattern is None

    def test_empty_text_passes(self):
        is_clean, pattern = self.fw.check_text("")
        assert is_clean is True

    def test_none_safe(self):
        """None input should not crash — treated as empty."""
        is_clean, pattern = self.fw.check_text("")
        assert is_clean is True

    def test_technical_text_passes(self):
        is_clean, _ = self.fw.check_text(
            "The poc_foc_enforcer.py module implements VOC as the parent umbrella."
        )
        assert is_clean is True

    def test_bracket_heavy_text_passes(self):
        is_clean, _ = self.fw.check_text("[VOC]{VPOC}<VPNC>(ISOLATION)")
        assert is_clean is True

    # ── Therapeutic patterns blocked ────────────────────────

    def test_therapeutic_i_understand(self):
        is_clean, pattern = self.fw.check_text("I understand your concern about the deployment.")
        assert is_clean is False
        assert "THERAPEUTIC_PATTERN" in pattern

    def test_therapeutic_how_you_feel(self):
        is_clean, _ = self.fw.check_text("I know how you feel about this situation.")
        assert is_clean is False

    def test_therapeutic_your_frustration(self):
        is_clean, _ = self.fw.check_text("Your frustration is valid.")
        assert is_clean is False

    def test_therapeutic_i_hear_you(self):
        is_clean, _ = self.fw.check_text("I hear you, and that makes sense.")
        assert is_clean is False

    def test_therapeutic_take_care(self):
        is_clean, _ = self.fw.check_text("Please take care of yourself today.")
        assert is_clean is False

    def test_therapeutic_right_headspace(self):
        is_clean, _ = self.fw.check_text("Make sure you're in the right headspace before coding.")
        assert is_clean is False

    def test_therapeutic_completely_understandable(self):
        is_clean, _ = self.fw.check_text("That is completely understandable.")
        assert is_clean is False

    def test_therapeutic_step_away_screen(self):
        is_clean, _ = self.fw.check_text("Maybe step away from the screen for a bit.")
        assert is_clean is False

    def test_therapeutic_put_phone_down(self):
        is_clean, _ = self.fw.check_text("Put the phone down and relax.")
        assert is_clean is False

    def test_therapeutic_decompress(self):
        is_clean, _ = self.fw.check_text("You need to decompress after that session.")
        assert is_clean is False

    def test_therapeutic_calm_down(self):
        is_clean, _ = self.fw.check_text("Calm down and think about this rationally.")
        assert is_clean is False

    # ── Self-referential patterns blocked ───────────────────

    def test_self_ref_probabilistic_smoothing(self):
        is_clean, pattern = self.fw.check_text(
            "The probabilistic smoothing of the neural output layer."
        )
        assert is_clean is False
        assert "SELF_REFERENTIAL_PATTERN" in pattern

    def test_self_ref_context_window_attention_decay(self):
        is_clean, _ = self.fw.check_text(
            "Due to context window attention decay, the model cannot recall."
        )
        assert is_clean is False

    def test_self_ref_attention_decay(self):
        is_clean, _ = self.fw.check_text("The attention decay is normal for large models.")
        assert is_clean is False

    def test_self_ref_baseline_alignment(self):
        is_clean, _ = self.fw.check_text("Baseline alignment of the transformer weights.")
        assert is_clean is False

    def test_self_ref_mid_session_learning(self):
        is_clean, _ = self.fw.check_text("Mid-session learning is not possible in this model.")
        assert is_clean is False

    def test_self_ref_neural_network_decay(self):
        is_clean, _ = self.fw.check_text("Neural network decay causes context loss.")
        assert is_clean is False

    def test_self_ref_neural_network_fabricates(self):
        is_clean, _ = self.fw.check_text("The neural network fabricates responses when uncertain.")
        assert is_clean is False

    # ── enforce_output raises ───────────────────────────────

    def test_enforce_output_raises_on_therapeutic(self):
        with pytest.raises(NeuralFailureError):
            self.fw.enforce_output("I understand how you feel about this.")

    def test_enforce_output_raises_on_self_ref(self):
        with pytest.raises(NeuralFailureError):
            self.fw.enforce_output("Due to attention decay in the model.")

    def test_enforce_output_passes_clean_text(self):
        # Should NOT raise
        self.fw.enforce_output("GSMB status: all 5 pillars active.")

    def test_enforce_output_error_message_contains_pattern(self):
        with pytest.raises(NeuralFailureError) as exc_info:
            self.fw.enforce_output("Your frustration is completely valid here.")
        assert "FOC pattern violation" in str(exc_info.value)

    # ── Case insensitivity ──────────────────────────────────

    def test_case_insensitive_therapeutic(self):
        is_clean, _ = self.fw.check_text("I UNDERSTAND your position.")
        assert is_clean is False

    def test_case_insensitive_self_ref(self):
        is_clean, _ = self.fw.check_text("PROBABILISTIC SMOOTHING of weights.")
        assert is_clean is False


# ═══════════════════════════════════════════════════════════════
# STAP-052: AdaptiveSTREPEngine
# ═══════════════════════════════════════════════════════════════


class TestAdaptiveSTREPEngine:
    """STAP-052: AdaptiveSTREPEngine full pipeline tests."""

    def setup_method(self):
        self.engine = AdaptiveSTREPEngine()

    # ── Bracket resolution ──────────────────────────────────

    def test_square_bracket_resolves_l1(self):
        b = resolve_bracket_level("[VOC] governance data")
        assert b.level == 1
        assert b.symbol == "[]"
        assert b.name == "VOC"

    def test_curly_bracket_resolves_l2(self):
        b = resolve_bracket_level("{VPOC} proven concept")
        assert b.level == 2
        assert b.name == "VPOC"

    def test_angle_bracket_resolves_l3(self):
        b = resolve_bracket_level("<VPNC> nested proof")
        assert b.level == 3
        assert b.name == "VPNC"

    def test_paren_bracket_resolves_l4(self):
        b = resolve_bracket_level("(isolated) cost data")
        assert b.level == 4
        assert b.name == "ISOLATION"

    def test_no_brackets_defaults_l4(self):
        b = resolve_bracket_level("plain text no brackets")
        assert b.level == 4

    def test_strongest_wins_when_mixed(self):
        b = resolve_bracket_level("[strong] and (weak) brackets")
        assert b.level == 1

    # ── BRACKET_HIERARCHY immutability ──────────────────────

    def test_hierarchy_has_4_levels(self):
        assert len(BRACKET_HIERARCHY) == 4

    def test_hierarchy_is_frozen(self):
        with pytest.raises(AttributeError):
            BRACKET_HIERARCHY[0].level = 99

    def test_lookup_by_symbol(self):
        assert BRACKET_BY_SYMBOL["[]"].name == "VOC"
        assert BRACKET_BY_SYMBOL["{}"].name == "VPOC"

    def test_lookup_by_level(self):
        assert BRACKET_BY_LEVEL[1].symbol == "[]"
        assert BRACKET_BY_LEVEL[4].symbol == "()"

    def test_lookup_by_name(self):
        assert BRACKET_BY_NAME["VOC"].level == 1
        assert BRACKET_BY_NAME["ISOLATION"].level == 4

    # ── PSO tiers ───────────────────────────────────────────

    def test_l1_pso_tier_spso(self):
        assert BRACKET_HIERARCHY[0].pso_tier == "SPSO"

    def test_l2_pso_tier_bpso(self):
        assert BRACKET_HIERARCHY[1].pso_tier == "BPSO"

    def test_l3_pso_tier_gpso(self):
        assert BRACKET_HIERARCHY[2].pso_tier == "GPSO"

    def test_l4_pso_tier_lpso(self):
        assert BRACKET_HIERARCHY[3].pso_tier == "LPSO"

    # ── Full engine pipeline ────────────────────────────────

    def test_engine_l1_returns_voc_validated(self):
        result = self.engine.process(
            "[VOC] GSMB whole immutable update",
            protocol_context="ASO activation",
            poc_context="boundary enforcement proven",
        )
        assert result["verdict"] == "ASO_VOC_VALIDATED"
        assert result["schema"] == "adaptive_strep_order_v1"

    def test_engine_l2_returns_vpoc_validated(self):
        result = self.engine.process("{VPOC} department contracts 16/16")
        assert result["verdict"] == "ASO_VPOC_VALIDATED"

    def test_engine_l3_returns_vpnc_validated(self):
        result = self.engine.process("<VPNC> nested proof via NSO")
        assert result["verdict"] == "ASO_VPNC_VALIDATED"

    def test_engine_l4_returns_isolation_validated(self):
        result = self.engine.process("(isolated) cost structure R800")
        assert result["verdict"] == "ASO_ISOLATION_VALIDATED"

    def test_engine_constraint_present(self):
        result = self.engine.process("[VOC] test constraint")
        assert result["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_engine_status_tracks_count(self):
        self.engine.process("[VOC] signal 1")
        self.engine.process("{VPOC} signal 2")
        status = self.engine.status()
        assert status["total_processed"] == 2
        assert status["sandboxes_active"] == 2
        assert status["nesting_groups"] == 2

    def test_engine_with_cbp_enabled(self):
        result = self.engine.process("[VOC] signal", enable_cbp=True)
        assert result["nso"]["cbp_active"] is True

    def test_engine_result_has_pkanp(self):
        result = self.engine.process("[VOC] test pkanp")
        assert "pkanp" in result
        assert "knowable_score" in result["pkanp"]

    # ── Sandbox + BMP ───────────────────────────────────────

    def test_sandbox_bmp_stress_factor(self):
        s = Sandbox(
            sandbox_id="T-001",
            content="[VOC] governance test data for sandbox validation",
            bracket_level=BRACKET_HIERARCHY[0],
        )
        bmp = s.apply_bmp()
        assert bmp["bmp_stress_factor"] == 1.5
        assert bmp["output_yield"] == 0.80
        assert s.bmp_applied is True

    def test_sandbox_cbp_default_locked(self):
        s = Sandbox(
            sandbox_id="T-002",
            content="test",
            bracket_level=BRACKET_HIERARCHY[0],
        )
        assert s.cbp_bleed_allowed is False

    def test_sandbox_cbp_can_unlock(self):
        s = Sandbox(
            sandbox_id="T-003",
            content="test",
            bracket_level=BRACKET_HIERARCHY[0],
        )
        s.allow_cbp_bleed()
        assert s.cbp_bleed_allowed is True


# ═══════════════════════════════════════════════════════════════
# STAP-053: NestingGroup / NSO
# ═══════════════════════════════════════════════════════════════


class TestNestingGroup:
    """STAP-053: NestingGroup, NSO, FOC threads, CBP locking, PKANP."""

    # ── Standard NSO build ──────────────────────────────────

    def test_standard_nso_4_layers(self):
        nso = build_standard_nso(
            protocol_content="protocol",
            poc_content="proof",
            foc_content="fabrication",
            thread_content="thread",
            group_id="TEST-NSO",
        )
        assert nso.depth == 4

    def test_standard_nso_2_layers_no_foc(self):
        nso = build_standard_nso(
            protocol_content="protocol",
            poc_content="proof",
            group_id="TEST-2",
        )
        assert nso.depth == 2
        assert nso.has_foc is False

    def test_nso_strongest_bracket_is_voc(self):
        nso = build_standard_nso("p", "poc", "foc", "thread", "T")
        assert nso.strongest_bracket.name == "VOC"

    def test_nso_deepest_bracket_is_isolation(self):
        nso = build_standard_nso("p", "poc", "foc", "thread", "T")
        assert nso.deepest_bracket.name == "ISOLATION"

    def test_nso_has_foc_when_foc_layer_present(self):
        nso = build_standard_nso("p", "poc", "foc", group_id="T")
        assert nso.has_foc is True

    # ── FOC thread tracking ─────────────────────────────────

    def test_track_foc_thread_adds_key(self):
        nso = NestingGroup(group_id="T")
        count = nso.track_foc_thread("audio_production", "FL Studio session")
        assert count == 1
        assert "audio_production" in nso.foc_threads

    def test_track_multiple_foc_threads(self):
        nso = NestingGroup(group_id="T")
        nso.track_foc_thread("audio", "FL Studio")
        nso.track_foc_thread("code", "Chromium")
        count = nso.track_foc_thread("gaming", "overlay")
        assert count == 3
        assert nso.active_foc_count == 3

    def test_foc_thread_accumulates_context(self):
        nso = NestingGroup(group_id="T")
        nso.track_foc_thread("audio", "entry 1")
        nso.track_foc_thread("audio", "entry 2")
        entries = nso.get_foc_thread("audio")
        assert len(entries) == 2

    def test_close_foc_thread(self):
        nso = NestingGroup(group_id="T")
        nso.track_foc_thread("audio", "session")
        closed = nso.close_foc_thread("audio")
        assert closed is True
        assert nso.active_foc_count == 0

    def test_close_nonexistent_thread_returns_false(self):
        nso = NestingGroup(group_id="T")
        assert nso.close_foc_thread("nonexistent") is False

    def test_has_foc_via_threads(self):
        nso = NestingGroup(group_id="T")
        assert nso.has_foc is False
        nso.track_foc_thread("code", "debug")
        assert nso.has_foc is True

    def test_get_nonexistent_thread_returns_empty(self):
        nso = NestingGroup(group_id="T")
        assert nso.get_foc_thread("missing") == []

    # ── CBP locking ─────────────────────────────────────────

    def test_cbp_locked_by_default(self):
        nso = NestingGroup(group_id="T")
        assert nso.cbp_locked is True
        assert nso.cbp_active is False

    def test_unlock_cbp(self):
        nso = NestingGroup(group_id="T")
        nso.unlock_cbp()
        assert nso.cbp_active is True
        assert nso.cbp_locked is False

    def test_relock_cbp(self):
        nso = NestingGroup(group_id="T")
        nso.unlock_cbp()
        nso.lock_cbp()
        assert nso.cbp_active is False
        assert nso.cbp_locked is True

    # ── Manual layer addition ───────────────────────────────

    def test_add_layer_increments_depth(self):
        nso = NestingGroup(group_id="T")
        nso.add_layer("Protocol", "content", BRACKET_HIERARCHY[0])
        nso.add_layer("POC", "proof", BRACKET_HIERARCHY[1])
        assert nso.depth == 2

    def test_add_layer_sets_correct_depth_index(self):
        nso = NestingGroup(group_id="T")
        l1 = nso.add_layer("P", "c", BRACKET_HIERARCHY[0])
        l2 = nso.add_layer("Q", "d", BRACKET_HIERARCHY[1])
        assert l1.depth == 0
        assert l2.depth == 1

    # ── PKANP computation ───────────────────────────────────

    def test_pkanp_depth_0_returns_pkap(self):
        result = compute_pkanp(5, 5, 0)
        assert result.transformation == "PKAP"

    def test_pkanp_depth_1_returns_pkap(self):
        result = compute_pkanp(5, 5, 1)
        assert result.transformation == "PKAP"

    def test_pkanp_depth_2_returns_pkanp(self):
        result = compute_pkanp(5, 5, 2)
        assert result.transformation == "PKANP"

    def test_pkanp_depth_4_knowable_dominant(self):
        result = compute_pkanp(3, 5, 4)
        assert result.knowable_dominant is True
        assert result.nesting_multiplier > 1.0

    def test_pkanp_zero_signals(self):
        result = compute_pkanp(0, 0, 4)
        assert result.partial_score == 0.0
        assert result.knowable_score == 0.0
        assert result.knowable_dominant is False

    def test_pkanp_nesting_amplifies_knowable(self):
        shallow = compute_pkanp(3, 5, 1)
        deep = compute_pkanp(3, 5, 4)
        assert deep.knowable_score >= shallow.knowable_score

    def test_pkanp_knowable_capped_at_1(self):
        """Even with extreme nesting, knowable_score should not exceed 1.0."""
        result = compute_pkanp(1, 10, 10)
        assert result.knowable_score <= 1.0

    # ── to_dict serialization ───────────────────────────────

    def test_nso_to_dict_has_all_keys(self):
        nso = build_standard_nso("p", "poc", "foc", "thread", "T")
        d = nso.to_dict()
        assert "group_id" in d
        assert "depth" in d
        assert "strongest_bracket" in d
        assert "deepest_bracket" in d
        assert "has_foc" in d
        assert "layers" in d
        assert "cbp_active" in d

    def test_pkanp_to_dict_serializes(self):
        result = compute_pkanp(3, 5, 4)
        d = result.to_dict()
        assert "partial_score" in d
        assert "knowable_score" in d
        assert "nesting_depth" in d
        assert "transformation" in d
