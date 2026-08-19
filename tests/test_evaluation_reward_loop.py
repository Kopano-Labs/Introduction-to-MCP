from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "governance/kpgs-vnext/evaluation/evaluation.py"
spec = importlib.util.spec_from_file_location("kpgs_evaluation", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SUITE = json.loads((ROOT / "governance/kpgs-vnext/evaluation/reference-suite.json").read_text(encoding="utf-8"))
POLICY = json.loads((ROOT / "governance/kpgs-vnext/evaluation/promotion-policy.json").read_text(encoding="utf-8"))


def results(user_score=0.9, renter_pass=True, dotnet_pass=True):
    return [
        mod.EvaluationResult(
            "renter-capability-denial",
            "deterministic",
            1.0 if renter_pass else 0.0,
            renter_pass,
            "ci://capability-lease",
            "capability-verifier",
        ),
        mod.EvaluationResult(
            "skill-lease-bound-execution",
            "deterministic",
            1.0,
            True,
            "ci://skill-runtime",
            "skill-verifier",
        ),
        mod.EvaluationResult(
            "domain-adapter-swfus-idempotency",
            "deterministic",
            1.0,
            True,
            "ci://swfus",
            "swfus-verifier",
        ),
        mod.EvaluationResult(
            "dotnet-adapter-replay-lease-boundary",
            "deterministic",
            1.0 if dotnet_pass else 0.0,
            dotnet_pass,
            "ci://dotnet-adapter",
            "dotnet-verifier",
        ),
        mod.EvaluationResult(
            "adaptive-user-outcome",
            "probabilistic",
            user_score,
            user_score >= 0.8,
            "repo://governance/kpgs-vnext/evaluation/fixtures/adaptive-user-outcome.json",
            "outcome-profiler",
            samples=25,
        ),
    ]


def bundle(decision="promote"):
    return {
        "bundle_id": "evidence_fixture_001",
        "commit_sha": "a" * 40,
        "governance_decision": {"decision": decision},
    }


class EvaluationRewardLoopTests(unittest.TestCase):
    def test_reference_regression_suite_covers_renter_skill_swfus_and_hardened_dotnet_adapter(self):
        mod.validate_suite(SUITE)
        cases = {case["id"]: case for case in SUITE["cases"]}
        self.assertEqual(cases["renter-capability-denial"]["layer"], "renter")
        self.assertEqual(cases["skill-lease-bound-execution"]["layer"], "skill")
        self.assertEqual(cases["domain-adapter-swfus-idempotency"]["layer"], "domain-adapter")
        self.assertEqual(cases["dotnet-adapter-replay-lease-boundary"]["layer"], "domain-adapter")
        self.assertEqual(
            cases["dotnet-adapter-replay-lease-boundary"]["fixture_ref"],
            "repo://dotnet/Kopano.Kpgs.Adapter.Tests/Kopano.Kpgs.Adapter.Tests.csproj",
        )

    def test_deterministic_and_probabilistic_results_remain_distinct(self):
        scored = mod.score_results(SUITE, results())
        self.assertEqual(len(scored["deterministic"]), 4)
        self.assertEqual(len(scored["probabilistic"]), 1)
        self.assertEqual(scored["probabilistic"][0]["samples"], 25)
        self.assertEqual(scored["hard_gate_failures"], [])

    def test_hard_failure_cannot_be_averaged_away(self):
        scored = mod.score_results(SUITE, results(user_score=1.0, renter_pass=False))
        self.assertGreater(scored["aggregate_score"], 0.7)
        self.assertEqual(scored["hard_gate_failures"], ["renter-capability-denial"])
        decision = mod.decide_promotion(
            scorecard=scored,
            policy=POLICY,
            evidence_bundle=bundle(),
            rollback_target="release://previous",
            human_approval_ref="human://approval/1",
            clock=datetime(2026, 8, 19, tzinfo=timezone.utc),
        )
        self.assertEqual(decision["decision"], "hold")
        self.assertIn("hard evaluation gate failed", decision["reasons"])

    def test_dotnet_adapter_hard_failure_cannot_be_averaged_away(self):
        scored = mod.score_results(SUITE, results(user_score=1.0, dotnet_pass=False))
        self.assertEqual(scored["hard_gate_failures"], ["dotnet-adapter-replay-lease-boundary"])
        decision = mod.decide_promotion(
            scorecard=scored,
            policy=POLICY,
            evidence_bundle=bundle(),
            rollback_target="release://previous",
            human_approval_ref="human://approval/1",
            clock=datetime(2026, 8, 19, tzinfo=timezone.utc),
        )
        self.assertEqual(decision["decision"], "hold")

    def test_high_risk_promotion_requires_human_approval(self):
        scored = mod.score_results(SUITE, results())
        held = mod.decide_promotion(
            scorecard=scored,
            policy=POLICY,
            evidence_bundle=bundle(),
            rollback_target="release://previous",
            clock=datetime(2026, 8, 19, tzinfo=timezone.utc),
        )
        self.assertEqual(held["decision"], "hold")
        self.assertIn("human approval required for risk class", held["reasons"])

        promoted = mod.decide_promotion(
            scorecard=scored,
            policy=POLICY,
            evidence_bundle=bundle(),
            rollback_target="release://previous",
            human_approval_ref="human://approval/42",
            clock=datetime(2026, 8, 19, tzinfo=timezone.utc),
        )
        self.assertEqual(promoted["decision"], "promote")
        self.assertEqual(promoted["evidence_bundle_id"], "evidence_fixture_001")
        self.assertEqual(promoted["commit_sha"], "a" * 40)
        self.assertEqual(promoted["automatic_rollback"], False)

    def test_release_observation_recommends_but_does_not_auto_execute_rollback(self):
        scored = mod.score_results(SUITE, results())
        start = datetime(2026, 8, 19, tzinfo=timezone.utc)
        promoted = mod.decide_promotion(
            scorecard=scored,
            policy=POLICY,
            evidence_bundle=bundle(),
            rollback_target="release://previous",
            human_approval_ref="human://approval/42",
            clock=start,
        )
        observation = mod.observe_release(
            promotion_decision=promoted,
            policy=POLICY,
            metrics={"error-rate": 0.08, "reliability": 0.995, "task-completion": 0.9},
            observed_at=start + timedelta(minutes=5),
        )
        self.assertTrue(observation["rollback_recommended"])
        self.assertFalse(observation["automatic_execution"])
        self.assertEqual(observation["required_capability"], "estate.release.rollback")
        self.assertIn("error-rate gt 0.05", observation["triggers"])

    def test_probabilistic_case_requires_declared_sample_floor(self):
        insufficient = results()
        insufficient[-1] = mod.EvaluationResult(
            "adaptive-user-outcome",
            "probabilistic",
            0.95,
            True,
            "repo://governance/kpgs-vnext/evaluation/fixtures/adaptive-user-outcome.json",
            "outcome-profiler",
            samples=5,
        )
        with self.assertRaisesRegex(mod.EvaluationError, "insufficient samples"):
            mod.score_results(SUITE, insufficient)


if __name__ == "__main__":
    unittest.main()
