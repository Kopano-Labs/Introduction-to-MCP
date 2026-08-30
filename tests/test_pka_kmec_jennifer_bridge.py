"""
Test Suite for PKA-KMEC-Jennifer Bridge
Verifies convergence bands, trust vectors, consequence journaling, and PR merge gates.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.pka_kmec_jennifer_bridge import (
    PkaKmecJenniferBridge,
    PkaConvergenceBand,
    PkaTrustVector,
    JenniferDatabaseLayer
)


class TestPkaKmecJenniferBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = PkaKmecJenniferBridge(balance_point=0.5)

    def test_pka_convergence_bands(self):
        """Founder-defined balance point at 0.5."""
        self.assertEqual(self.bridge.classify_convergence(0.2), PkaConvergenceBand.TOWARD_ZERO)
        self.assertEqual(self.bridge.classify_convergence(0.5), PkaConvergenceBand.BALANCED)
        self.assertEqual(self.bridge.classify_convergence(0.85), PkaConvergenceBand.TOWARD_ONE)
        with self.assertRaises(ValueError):
            self.bridge.classify_convergence(-0.1)

    def test_pka_trust_vectors(self):
        """Trust vector maps (verdict, disposition) to Green/Yellow/Red."""
        self.assertEqual(self.bridge.evaluate_trust_vector("POC_CANDIDATE", "PROPOSE"), PkaTrustVector.GREEN)
        self.assertEqual(self.bridge.evaluate_trust_vector("MAYBE", "HOLD"), PkaTrustVector.YELLOW)
        self.assertEqual(self.bridge.evaluate_trust_vector("FOC_CANDIDATE", "BLOCK"), PkaTrustVector.RED)

    def test_projection_requires_authoritative_receipt(self):
        """Projection state (MongoDB) cannot be updated without authoritative PostgreSQL journal receipt."""
        # Record authoritative event
        entry = self.bridge.record_authoritative_event(
            event_type="STATE_SETTLEMENT",
            actor_id="agent-001",
            scope="KPGS::CORE",
            payload={"balance": 1000, "currency": "ZAR"}
        )
        self.assertTrue(entry.verified)
        self.assertIsNotNone(entry.payload_hash)

        # Valid projection update
        proj = self.bridge.update_projection("dashboard_view", {"balance_display": "R 1,000"}, entry.entry_id)
        self.assertEqual(proj["layer"], JenniferDatabaseLayer.MONGODB_PROJECTION.value)
        self.assertEqual(proj["source_entry_id"], entry.entry_id)

        # Invalid projection update with fake receipt must fail
        with self.assertRaises(PermissionError):
            self.bridge.update_projection("dashboard_view", {"fake": True}, "fake-receipt-id")

    def test_jennifer_merge_gates(self):
        """Enforce Sprint 3 VALIDATION_POLICY.md gates."""
        # Passing gate
        passed, violations = self.bridge.validate_jennifer_merge_gates(
            declared_source="User-provided canonical architecture artifact",
            declared_by="@RobynAwesome",
            declaration_date="2026-08-29",
            validation_state="VALIDATED",
            evidence_linked=True,
            governance_signed=True
        )
        self.assertTrue(passed)
        self.assertEqual(len(violations), 0)

        # Failing gate: validated without evidence
        failed, violations = self.bridge.validate_jennifer_merge_gates(
            declared_source="Architecture Spec",
            declared_by="@RobynAwesome",
            declaration_date="2026-08-29",
            validation_state="VALIDATED",
            evidence_linked=False,
            governance_signed=True
        )
        self.assertFalse(failed)
        self.assertTrue(any("Gate 3 Failed" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
