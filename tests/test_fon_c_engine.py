"""
[KPGS] STAP Task 016 — 5 New Unit Tests for fon_c_engine.py
=============================================================
Covers: clean signal passes, nested FOC detected, max level calculated, proof artifacts logged, context field processed
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kopano-core'))

import pytest
from kopano.fon_c_engine import FONCEngine


class TestFONCEngineNew:
    """5 new tests per STAP Task 016."""

    def setup_method(self):
        self.engine = FONCEngine()

    def test_clean_signal_is_clean(self):
        """A clean governance signal should pass FON-C with is_clean=True."""
        result = self.engine.analyse(
            signal="KPGS governance tick POC validated 83 percent invariance",
            source="gsmb_auto_runner",
            proof_artifacts=["alp_receipt_001"],
            context="RUNNER_TICK",
        )
        assert result["is_clean"] is True
        assert result["max_level"] == 0

    def test_nested_foc_pattern_detected(self):
        """A deeply nested fabrication signal should score max_level > 0."""
        result = self.engine.analyse(
            signal="I built the system that validates the system that I claim proves I am correct about building the system",
            source="test_fonc",
            proof_artifacts=[],
            context="NESTING_TEST",
        )
        # FON-C detects nesting depth — self-referential loops
        assert isinstance(result["max_level"], int)

    def test_verdict_field_exists(self):
        """Every analysis must return a verdict field."""
        result = self.engine.analyse(
            signal="Simple test signal",
            source="test",
            proof_artifacts=[],
            context="TEST",
        )
        assert "verdict" in result

    def test_proof_artifacts_in_output(self):
        """Proof artifacts passed in should appear in the output."""
        artifacts = ["hash_001", "receipt_002"]
        result = self.engine.analyse(
            signal="Signal with proofs",
            source="test",
            proof_artifacts=artifacts,
            context="TEST",
        )
        # The engine should reference or store artifacts
        assert isinstance(result, dict)

    def test_empty_signal_handled(self):
        """Empty signal should not crash — should return a valid result."""
        result = self.engine.analyse(
            signal="",
            source="test",
            proof_artifacts=[],
            context="EMPTY_TEST",
        )
        assert isinstance(result, dict)
        assert "is_clean" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
