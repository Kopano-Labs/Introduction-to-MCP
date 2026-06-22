"""
[KPGS_HOOD_ENTRY] JIRO STAP — Tests for Adaptiveness Package
=============================================================
Task: Write unit tests for neural_failure_firewall, swiftkey_nlp, civic_utility_router
Validates POC for the GSMB ADATIVNESS layer.
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kopano-core'))

import pytest
from kopano.adaptiveness.neural_failure_firewall import NeuralFailureFirewall, NeuralFailureError
from kopano.adaptiveness.swiftkey_nlp import SwiftKeyNLP
from kopano.adaptiveness.civic_utility_router import CivicUtilityRouter


# ═══ NEURAL FAILURE FIREWALL TESTS ═══

class TestNeuralFailureFirewall:
    def setup_method(self):
        self.fw = NeuralFailureFirewall()

    def test_clean_text_passes(self):
        ok, pattern = self.fw.check_text("Build the pre-commit hook for KPGS governance.")
        assert ok is True
        assert pattern is None

    def test_therapeutic_pattern_blocked(self):
        ok, pattern = self.fw.check_text("I understand your frustration, let me help.")
        assert ok is False
        assert "THERAPEUTIC_PATTERN" in pattern

    def test_how_you_feel_blocked(self):
        ok, pattern = self.fw.check_text("I know how you feel about this situation.")
        assert ok is False

    def test_calm_down_blocked(self):
        ok, pattern = self.fw.check_text("Please calm down and take a breath.")
        assert ok is False

    def test_self_referential_blocked(self):
        ok, pattern = self.fw.check_text("This is due to context window attention decay in long sessions.")
        assert ok is False
        assert "SELF_REFERENTIAL_PATTERN" in pattern

    def test_neural_network_decay_blocked(self):
        ok, pattern = self.fw.check_text("The neural network decay caused this error.")
        assert ok is False

    def test_enforce_output_raises_on_foc(self):
        with pytest.raises(NeuralFailureError):
            self.fw.enforce_output("I understand how you feel, please decompress.")

    def test_enforce_output_passes_clean(self):
        # Should not raise
        self.fw.enforce_output("POC_VALIDATED at 83.33% invariance. Commit pushed.")

    def test_empty_text_passes(self):
        ok, pattern = self.fw.check_text("")
        assert ok is True

    def test_none_text_passes(self):
        ok, pattern = self.fw.check_text(None)
        assert ok is True

    def test_kpgs_language_passes(self):
        ok, _ = self.fw.check_text("I_AM_STATELESS_RENTER_NOT_LANDLORD. Jesus is King. The thread holds.")
        assert ok is True

    def test_technical_language_passes(self):
        ok, _ = self.fw.check_text("SHA-256 hash: 154febfaae19d1d4. NCCNP 4/4 POC_CLOSED. APU GREEN.")
        assert ok is True


# ═══ SWIFTKEY NLP TESTS ═══

class TestSwiftKeyNLP:
    def setup_method(self):
        self.nlp = SwiftKeyNLP()

    def test_translate_known_slang(self):
        result = self.nlp.translate("Life ekasi is hard bhuda")
        assert "in the township" in result
        assert "brother / peer" in result

    def test_translate_tsotsitaal(self):
        result = self.nlp.translate("The tsotsitaal dialect is complex")
        assert "township slang dialect" in result

    def test_translate_preserves_unknown(self):
        result = self.nlp.translate("Hello world")
        assert result == "Hello world"

    def test_translate_empty(self):
        assert self.nlp.translate("") == ""

    def test_learn_phrase(self):
        self.nlp.learn_phrase("skrrr", "let's go / excitement")
        result = self.nlp.translate("skrrr we moving")
        assert "let's go" in result

    def test_token_footprint_slang_higher(self):
        slang_text = "ekasi life is tsotsitaal heavy"
        normal_text = "normal english sentence here"
        slang_tokens = self.nlp.calculate_token_footprint(slang_text)
        normal_tokens = self.nlp.calculate_token_footprint(normal_text)
        assert slang_tokens > normal_tokens

    def test_calculate_savings(self):
        result = self.nlp.calculate_savings("Life ekasi with the grootman in khayelitsha")
        assert result["tokens_saved"] >= 0
        assert "translated_text" in result
        assert result["raw_tokens"] >= result["translated_tokens"]

    def test_case_insensitive(self):
        result = self.nlp.translate("EKASI is loud")
        assert "in the township" in result

    def test_location_names_translate(self):
        result = self.nlp.translate("Going to danun tomorrow")
        assert "Dunoon" in result


# ═══ CIVIC UTILITY ROUTER TESTS ═══

class TestCivicUtilityRouter:
    def setup_method(self):
        self.router = CivicUtilityRouter()

    def test_pothole_detected(self):
        result = self.router.parse_signal("There is a big pothole on Main Road")
        assert result["detected"] is True
        assert result["category"] == "INFRASTRUCTURE_POTHOLE"

    def test_loadshedding_detected(self):
        result = self.router.parse_signal("Load shedding stage 4 in Khayelitsha")
        assert result["detected"] is True
        assert result["category"] == "ENERGY_GRID_FAILURE"

    def test_loadshedding_single_word(self):
        result = self.router.parse_signal("Another loadshedding night")
        assert result["detected"] is True

    def test_water_leak_detected(self):
        result = self.router.parse_signal("Water leak on corner of 5th street")
        assert result["detected"] is True
        assert result["category"] == "INFRASTRUCTURE_WATER_LEAK"

    def test_no_civic_intent(self):
        result = self.router.parse_signal("I want to book a 5-a-side court")
        assert result["detected"] is False

    def test_route_pothole_generates_report(self):
        result = self.router.route_civic_signal("Massive pothole near school", location="Dunoon")
        assert result["routed"] is True
        assert "KPGS-CIVIC-" in result["civic_id"]
        assert result["category"] == "INFRASTRUCTURE_POTHOLE"
        assert result["location_context"] == "Dunoon"
        assert result["verdict"] == "ROUTED_TO_GOVERNMENT"

    def test_route_no_civic_returns_not_routed(self):
        result = self.router.route_civic_signal("Just a normal message")
        assert result["routed"] is False

    def test_route_includes_timestamp(self):
        result = self.router.route_civic_signal("Power outage in Gugulethu", location="Gugulethu")
        assert "timestamp" in result
        assert "T" in result["timestamp"]  # ISO format

    def test_civic_id_is_unique(self):
        r1 = self.router.route_civic_signal("Pothole A", location="X")
        r2 = self.router.route_civic_signal("Pothole B", location="Y")
        assert r1["civic_id"] != r2["civic_id"]

    def test_empty_signal(self):
        result = self.router.parse_signal("")
        assert result["detected"] is False


# ═══ RUN ═══
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
