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

    def test_context_abundance_and_relevance_cannot_manufacture_mutation_authority(self):
        information = mod.InformationMembrane(
            authority=0.2,
            abundance=1.0,
            relevance=1.0,
            permission=0.2,
            observation=True,
            mutation_requested=True,
        )
        reasons = information.mutation_reasons()
        self.assertFalse(information.mutation_eligible())
        self.assertTrue(any("abundance cannot substitute for authority" in reason for reason in reasons))
        self.assertTrue(any("relevance cannot substitute for permission" in reason for reason in reasons))

    def test_observation_is_not_mutation_and_low_risk_read_remains_highway_speed(self):
        membrane = mod.StateTransitionMembrane(
            same_object=True,
            scope_match=True,
            information=mod.InformationMembrane(
                authority=1.0,
                abundance=1.0,
                relevance=1.0,
                permission=1.0,
                observation=True,
                mutation_requested=False,
            ),
            evidence=1.0,
            requested_delta=0.0,
            permitted_delta=0.0,
            state_cost=0.0,
            homeostasis=1.0,
            ambiguity=0.1,
            risk=0.1,
            irreversibility=0.0,
        )
        self.assertEqual(membrane.velocity(), mod.TransitionVelocity.HIGHWAY)
        verdict = membrane.evaluate()
        self.assertEqual(verdict.decision, mod.TransitionDecision.HOLD)
        self.assertTrue(any("Observation is not mutation authority" in reason for reason in verdict.reasons))

    def test_new_idea_is_not_current_task_without_required_change(self):
        information = mod.InformationMembrane(
            authority=1.0,
            abundance=0.5,
            relevance=0.9,
            permission=1.0,
            observation=True,
            mutation_requested=True,
            new_idea=True,
            required_change=False,
        )
        self.assertFalse(information.mutation_eligible())
        self.assertTrue(any("new idea is not the current task" in reason.lower() for reason in information.mutation_reasons()))

    def test_mutation_runs_at_school_zone_velocity_when_bounded(self):
        membrane = mod.StateTransitionMembrane(
            same_object=True,
            scope_match=True,
            information=mod.InformationMembrane(
                authority=1.0,
                abundance=0.4,
                relevance=0.9,
                permission=1.0,
                observation=True,
                mutation_requested=True,
            ),
            evidence=0.95,
            requested_delta=0.2,
            permitted_delta=0.3,
            state_cost=0.2,
            homeostasis=0.95,
            ambiguity=0.1,
            risk=0.2,
            irreversibility=0.2,
        )
        verdict = membrane.evaluate()
        self.assertEqual(verdict.velocity, mod.TransitionVelocity.SCHOOL_ZONE)
        self.assertEqual(verdict.decision, mod.TransitionDecision.EXECUTE)

    def test_membrane_holds_when_change_exceeds_permeability_or_creates_excess_state(self):
        membrane = mod.StateTransitionMembrane(
            same_object=True,
            scope_match=True,
            information=mod.InformationMembrane(
                authority=1.0,
                abundance=0.8,
                relevance=0.9,
                permission=1.0,
                observation=True,
                mutation_requested=True,
            ),
            evidence=0.95,
            requested_delta=0.8,
            permitted_delta=0.2,
            state_cost=0.9,
            homeostasis=0.95,
            ambiguity=0.1,
            risk=0.2,
            irreversibility=0.2,
        )
        verdict = membrane.evaluate()
        self.assertEqual(verdict.decision, mod.TransitionDecision.HOLD)
        self.assertTrue(any("permeability" in reason for reason in verdict.reasons))
        self.assertTrue(any("state proliferation" in reason for reason in verdict.reasons))

    def test_membrane_holds_when_transition_changes_object_or_breaks_homeostasis(self):
        membrane = mod.StateTransitionMembrane(
            same_object=False,
            scope_match=True,
            information=mod.InformationMembrane(
                authority=1.0,
                abundance=0.5,
                relevance=1.0,
                permission=1.0,
                observation=True,
                mutation_requested=True,
            ),
            evidence=1.0,
            requested_delta=0.2,
            permitted_delta=0.3,
            state_cost=0.2,
            homeostasis=0.2,
            ambiguity=0.1,
            risk=0.2,
            irreversibility=0.2,
        )
        verdict = membrane.evaluate()
        self.assertEqual(verdict.decision, mod.TransitionDecision.HOLD)
        self.assertTrue(any("repair the existing object" in reason for reason in verdict.reasons))
        self.assertTrue(any("active objective" in reason for reason in verdict.reasons))

    def test_checkpoint_transition_requires_explicit_confirmation(self):
        base = dict(
            same_object=True,
            scope_match=True,
            information=mod.InformationMembrane(
                authority=1.0,
                abundance=0.4,
                relevance=1.0,
                permission=1.0,
                observation=True,
                mutation_requested=True,
            ),
            evidence=1.0,
            requested_delta=0.2,
            permitted_delta=0.2,
            state_cost=0.2,
            homeostasis=1.0,
            ambiguity=0.1,
            risk=0.8,
            irreversibility=0.2,
        )
        unconfirmed = mod.StateTransitionMembrane(**base)
        self.assertEqual(unconfirmed.velocity(), mod.TransitionVelocity.CHECKPOINT)
        self.assertEqual(unconfirmed.evaluate().decision, mod.TransitionDecision.CONFIRM)

        confirmed = mod.StateTransitionMembrane(**base, explicit_confirmation=True)
        self.assertEqual(confirmed.evaluate().decision, mod.TransitionDecision.EXECUTE)

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
