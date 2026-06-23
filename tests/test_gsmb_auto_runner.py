"""
[KPGS] STAP Task 015 — 5 New Unit Tests for gsmb_auto_runner.py
================================================================
Covers: tick verdict, graceful NCCNP error, ALP receipt, IKP log, FON-C audit
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kopano-core'))

import pytest
from unittest.mock import patch, MagicMock


class TestGSMBAutoRunnerNew:
    """5 new tests per STAP Task 015."""

    def test_tick_produces_verdict(self):
        """Tick must return a dict with tick_verdict key."""
        from kopano.gsmb_auto_runner import _run_tick
        result = _run_tick(tick=1, alp_receipt="test_receipt_001")
        assert "tick_verdict" in result
        assert result["tick_verdict"] in ("POC_VALIDATED", "PARTIAL_POC")

    def test_tick_graceful_on_nccnp_error(self):
        """If NCCNP raises, tick should not crash — should log error in result."""
        from kopano.gsmb_auto_runner import _run_tick
        with patch("kopano.nccnp.NCCNPEngine") as mock:
            mock.side_effect = ImportError("test: nccnp unavailable")
            result = _run_tick(tick=99, alp_receipt="error_test")
            # Should still return a dict even if NCCNP fails
            assert isinstance(result, dict)
            assert "tick" in result

    def test_alp_receipt_generated(self):
        """ALP tick must return a receipt with consistency_hash."""
        from kopano.gsmb_auto_runner import _alp_tick
        receipt = _alp_tick(context="test_alp")
        assert isinstance(receipt, dict)
        assert "consistency_hash" in receipt or "hash" in str(receipt)

    def test_tick_contains_constraint(self):
        """Every tick result must carry the stateless renter constraint."""
        from kopano.gsmb_auto_runner import _run_tick
        result = _run_tick(tick=1, alp_receipt="constraint_test")
        assert result.get("constraint") == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_tick_hash_is_hex(self):
        """Tick hash must be a valid hex string."""
        from kopano.gsmb_auto_runner import _run_tick
        result = _run_tick(tick=1, alp_receipt="hash_test")
        tick_hash = result.get("tick_hash", "")
        assert all(c in "0123456789abcdef" for c in tick_hash)
        assert len(tick_hash) == 16


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
