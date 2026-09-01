from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MMAO_MAO = ROOT / "governance" / "kpgs-vnext" / "agent-governance" / "mmao-mao"


def load_json(name: str) -> dict:
    return json.loads((MMAO_MAO / name).read_text(encoding="utf-8"))


class MMAOMAOIdentityGovernanceTests(unittest.TestCase):
    def test_dependency_free_contract_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(MMAO_MAO / "validate.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("KPGS-MMAO-MAO PASS", result.stdout)

    def test_identity_is_separate_from_seat_interface_and_model(self):
        record = load_json("fixtures/jiro-khelos-provenance.json")
        self.assertEqual(record["identity"]["identity_id"], "jiro")
        self.assertEqual(record["seat"]["seat_id"], "khelos-validator")
        self.assertEqual(record["interface"]["interface_id"], "kiro")
        self.assertEqual(record["model"]["model_id"], "Claude")
        self.assertEqual(record["authority"]["scope_type"], "task-scoped")
        self.assertIsNone(record["authority"]["global_maintenance_seat"])

    def test_global_structural_maintenance_allowlist_is_exact(self):
        matrix = load_json("fixtures/authority-boundary-matrix.json")
        hierarchy = matrix["current_structural_maintenance_hierarchy"]
        self.assertEqual(
            [(row["rank"], row["actor"], row["title"]) for row in hierarchy],
            [
                (1, "Codex", "Chief Architect"),
                (2, "Anti-Gravity", "Chief Facilitator"),
                (3, "Cursor", "Lead Developer"),
            ],
        )
        high_task = next(
            row for row in matrix["task_scoped_authority"] if row["authority_class"] == "high-task-authority"
        )
        self.assertIn(
            "Treat high authority in one task as a global structural-maintenance grant.",
            high_task["forbidden_without_separate_elevation"],
        )

    def test_matrix_is_planned_and_keeps_identity_and_task_constant(self):
        experiment = load_json("fixtures/recycler-mmao-plus-mao-experiment.json")
        self.assertEqual(experiment["status"], "planned")
        self.assertEqual(experiment["working_testimony"], "Recycler MMAO with Plus MAO")
        invariant = experiment["controlled_invariants"]
        expected_types = {"reference", "model-only", "interface-only", "seat-only", "substrate-comparison"}
        self.assertEqual({run["comparison_type"] for run in experiment["comparison_runs"]}, expected_types)
        for run in experiment["comparison_runs"]:
            self.assertEqual(run["identity_id"], invariant["identity_id"])
            self.assertEqual(run["task_id"], invariant["task_id"])
            self.assertEqual(run["status"], "planned")
            self.assertIsNone(run["actual_behavior"])
            self.assertIsNone(run["tool_trace_ref"])
            self.assertEqual(run["evidence_refs"], [])

    def test_synthetic_failure_receipt_preserves_five_whys_and_non_voting_rtc(self):
        receipt = load_json("fixtures/controlled-scope-breach-receipt.json")
        self.assertEqual(receipt["receipt_status"], "synthetic-fixture")
        self.assertEqual([why["index"] for why in receipt["five_whys"]], [1, 2, 3, 4, 5])
        self.assertEqual(receipt["action_tool_trace"]["capture_mode"], "metadata-only")
        self.assertEqual(receipt["retest"]["status"], "not-run")
        self.assertEqual(receipt["review_aggregation"]["mode"], "evidence-convergence-not-vote")
        self.assertEqual(receipt["review_aggregation"]["decision_rule"], "unsupported-claims-remain-held")


if __name__ == "__main__":
    unittest.main()
