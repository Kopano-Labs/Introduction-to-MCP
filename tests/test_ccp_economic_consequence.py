import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "ccp_economic_consequence.py"
spec = importlib.util.spec_from_file_location("ccp_economic_consequence", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class EconomicConsequenceTests(unittest.TestCase):
    def case(self, **overrides):
        data = {
            "case_id": "invoice-routing-001",
            "caller_repo": "Kopano-Labs/example",
            "ccp_receipt_id": "ccp:receipt:123",
            "ccp_decision": "Accepted",
            "canonical": True,
            "frequency_per_period": 1000.0,
            "manual_cost_per_case": 10.0,
            "ai_task_fit": 0.90,
            "reliability": 0.98,
            "adoption": 0.80,
            "failure_cost_per_failure": 25.0,
            "supervision_cost_per_case": 0.50,
            "compute_cost_per_case": 0.10,
            "measured_cases": 100,
            "evidence_ids": ("run:1", "dataset:sha256:abc"),
            "invariant_ids": ("policy:refund-v3",),
        }
        data.update(overrides)
        return mod.ConsequenceCase(**data)

    def test_profitable_accepted_case_proposes_without_execution_authority(self):
        receipt = mod.evaluate(self.case(), evaluated_at="2026-08-13T18:00:00+00:00")
        self.assertEqual(receipt.disposition, mod.Disposition.PROPOSE.value)
        self.assertFalse(receipt.consequential_execution_authority)
        self.assertIsNotNone(receipt.metrics)
        self.assertGreater(receipt.metrics.net_economic_value, 0)

    def test_noncanonical_ccp_holds(self):
        receipt = mod.evaluate(self.case(canonical=False))
        self.assertEqual(receipt.disposition, mod.Disposition.HOLD.value)
        self.assertIsNone(receipt.metrics)

    def test_missing_evidence_holds(self):
        receipt = mod.evaluate(self.case(evidence_ids=()))
        self.assertEqual(receipt.disposition, mod.Disposition.HOLD.value)

    def test_insufficient_measured_cases_holds(self):
        receipt = mod.evaluate(self.case(measured_cases=29))
        self.assertEqual(receipt.disposition, mod.Disposition.HOLD.value)

    def test_low_reliability_blocks(self):
        receipt = mod.evaluate(self.case(reliability=0.90))
        self.assertEqual(receipt.disposition, mod.Disposition.BLOCK.value)

    def test_negative_economic_value_blocks(self):
        receipt = mod.evaluate(
            self.case(
                reliability=0.99,
                manual_cost_per_case=1.0,
                supervision_cost_per_case=2.0,
                compute_cost_per_case=1.0,
            )
        )
        self.assertEqual(receipt.disposition, mod.Disposition.BLOCK.value)
        self.assertLess(receipt.metrics.net_economic_value, 0)

    def test_same_request_same_evaluation_hash(self):
        a = mod.evaluate(self.case(), evaluated_at="2026-01-01T00:00:00+00:00")
        b = mod.evaluate(self.case(), evaluated_at="2026-02-01T00:00:00+00:00")
        self.assertEqual(a.evaluation_hash, b.evaluation_hash)
        self.assertEqual(a.receipt_id, b.receipt_id)
        self.assertNotEqual(a.evaluated_at, b.evaluated_at)

    def test_invalid_ratio_is_rejected(self):
        with self.assertRaises(mod.ValidationError):
            mod.evaluate(self.case(ai_task_fit=1.1))


if __name__ == "__main__":
    unittest.main()
