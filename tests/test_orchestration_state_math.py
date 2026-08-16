import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).parents[1] / "kopano-core" / "kopano" / "orchestration_state_math.py"
spec = importlib.util.spec_from_file_location("orchestration_state_math", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class OrchestrationStateMathTests(unittest.TestCase):
    def test_response_pressure_is_bounded(self):
        signal = mod.ResponsePressure(0.9, 0.8, 1.0, 0.95, 0.7)
        self.assertGreaterEqual(signal.score(), 0.0)
        self.assertLessEqual(signal.score(), 1.0)

    def test_meaning_can_weight_tone_and_delivery_more_than_words(self):
        signal = mod.MeaningSignal(
            words=0.2,
            tone=1.0,
            timing=0.5,
            status=0.5,
            audience=0.8,
            history=0.7,
            delivery=1.0,
        )
        self.assertGreater(signal.tone_sensitive(), signal.received())

    def test_knowing_and_understanding_are_separate_dimensions(self):
        state = mod.KnowledgeUnderstanding(
            knowledge=0.95,
            interpretation_accuracy=0.6,
            context_fit=0.5,
        )
        self.assertEqual(state.knowledge, 0.95)
        self.assertAlmostEqual(state.understanding, 0.3)
        self.assertAlmostEqual(state.overlap, 0.3)

    def test_reported_resolution_is_not_automatically_verified(self):
        state = mod.ResolutionState(
            reported_resolution=0.95,
            residual_distress=0.8,
            residual_anger=0.7,
            residual_uncertainty=0.6,
        )
        self.assertGreater(state.mismatch, 0.5)
        self.assertFalse(state.verified())

    def test_low_residual_load_can_verify_reported_resolution(self):
        state = mod.ResolutionState(
            reported_resolution=0.9,
            residual_distress=0.05,
            residual_anger=0.1,
            residual_uncertainty=0.05,
        )
        self.assertTrue(state.verified())

    def test_autonomy_is_earned_and_reduced_by_failures(self):
        start = mod.AutonomyState(0.5)
        earned = start.update(validated_executions=4)
        corrected = earned.update(failed_executions=1)
        self.assertGreater(earned.autonomy, start.autonomy)
        self.assertLess(corrected.autonomy, earned.autonomy)

    def test_governed_transition_executes_when_safe_and_clear(self):
        transition = mod.GovernedTransition(
            objective_fit=0.95,
            evidence=0.9,
            permission=1.0,
            ambiguity=0.1,
            risk=0.2,
            irreversibility=0.2,
        )
        self.assertEqual(transition.decide(), mod.TransitionDecision.EXECUTE)

    def test_governed_transition_clarifies_real_ambiguity(self):
        transition = mod.GovernedTransition(
            objective_fit=0.9,
            evidence=0.9,
            permission=1.0,
            ambiguity=0.8,
            risk=0.1,
            irreversibility=0.1,
        )
        self.assertEqual(transition.decide(), mod.TransitionDecision.CLARIFY)

    def test_governed_transition_requires_confirmation_for_irreversible_action(self):
        transition = mod.GovernedTransition(
            objective_fit=0.9,
            evidence=0.9,
            permission=1.0,
            ambiguity=0.1,
            risk=0.4,
            irreversibility=0.9,
        )
        self.assertEqual(transition.decide(), mod.TransitionDecision.CONFIRM)
        confirmed = mod.GovernedTransition(
            objective_fit=0.9,
            evidence=0.9,
            permission=1.0,
            ambiguity=0.1,
            risk=0.4,
            irreversibility=0.9,
            explicit_confirmation=True,
        )
        self.assertEqual(confirmed.decide(), mod.TransitionDecision.EXECUTE)

    def test_ccp_convergence_includes_both_targets(self):
        result = mod.converge_targets(
            {"execution": 1.0, "reflection": 0.2},
            {"execution": 0.6, "reflection": 0.8},
            user_weight=0.5,
            agent_weight=0.5,
        )
        self.assertAlmostEqual(result["execution"], 0.8)
        self.assertAlmostEqual(result["reflection"], 0.5)

    def test_convergence_respects_invariant_bounds(self):
        result = mod.converge_targets(
            {"risk": 0.9},
            {"risk": 0.8},
            invariant_bounds={"risk": (0.0, 0.4)},
        )
        self.assertEqual(result["risk"], 0.4)

    def test_receipt_is_deterministic(self):
        first = mod.receipt({"a": 1, "b": 2})
        second = mod.receipt({"b": 2, "a": 1})
        self.assertEqual(first["sha256"], second["sha256"])

    def test_invalid_ratio_fails_closed(self):
        with self.assertRaises(mod.ValidationError):
            mod.ResponsePressure(1.2, 0.8, 1.0, 0.9, 0.7).score()


if __name__ == "__main__":
    unittest.main()
