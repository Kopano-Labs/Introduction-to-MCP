import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parents[1]
MODULE_PATH = (
    ROOT
    / "governance"
    / "kpgs-vnext"
    / "evidence"
    / "evidence.py"
)
spec = importlib.util.spec_from_file_location(
    "kpgs_evidence_runtime",
    MODULE_PATH,
)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class FixedClock:
    def __init__(self):
        self.now = datetime(
            2026,
            8,
            18,
            10,
            0,
            tzinfo=timezone.utc,
        )

    def __call__(self):
        return self.now


class EvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.clock = FixedClock()

    def builder(self, **overrides):
        payload = dict(
            estate_property="FivesArena.com",
            release_ref="release://fivesarena/2026-08-18",
            commit_sha="a" * 40,
            adapter={
                "implementation": "canonical-domain-adapter",
                "version": "contract-v1",
            },
            renter={
                "renter_id": "renter:fivesarena:001",
                "protocol_version": "1.0",
            },
            skills=[
                {
                    "name": "arena-weather-context",
                    "version": "1.0.0",
                }
            ],
            task_id="task:article-focus-weather",
            session_id="session:user-001",
            correlation_id="corr:evidence-001",
            governing_spec_ref="spec://fivesarena/focus-weather/v1",
            retention_policy_ref="retention://kopano/release-evidence/v1",
            redaction_policy_ref="redaction://kopano/no-secrets/v1",
            clock=self.clock,
        )
        payload.update(overrides)
        return mod.EvidenceBundleBuilder(**payload)

    @staticmethod
    def add_trace(builder):
        for index, layer in enumerate(
            [
                "pwa",
                "adapter",
                "sovereign-hub",
                "renter",
                "skill",
            ]
        ):
            builder.add_trace_hop(
                layer=layer,
                ref=f"{layer}://trace/{index}",
                status="succeeded",
                at=f"2026-08-18T10:00:0{index}Z",
                duration_ms=10 + index,
                metadata={"attempt": 1},
            )
        builder.add_trace_hop(
            layer="verifier",
            ref="verifier:release-gate",
            status="succeeded",
            at="2026-08-18T10:00:06Z",
            duration_ms=21,
        )
        builder.add_trace_hop(
            layer="deployment",
            ref="deployment://vercel/fivesarena",
            status="succeeded",
            at="2026-08-18T10:00:07Z",
            duration_ms=33,
        )
        return builder

    @staticmethod
    def add_promotion_artifacts(builder):
        kinds = [
            "specification",
            "policy-decision",
            "capability-lease",
            "execution",
            "verification",
            "security",
            "accessibility",
            "deployment",
            "user-outcome",
        ]
        for index, kind in enumerate(kinds):
            builder.add_artifact(
                kind=kind,
                ref=f"evidence://artifact/{kind}/{index}",
                sha256=(f"{index:x}" * 64)[:64],
            )
        return builder

    @staticmethod
    def add_promotion_metrics(builder):
        values = {
            "latency": (120.0, "ms"),
            "realtime-health": (True, None),
            "reliability": (0.999, "ratio"),
            "error-rate": (0.001, "ratio"),
            "task-completion": (0.94, "ratio"),
            "task-abandonment": (0.06, "ratio"),
            "accessibility": (True, None),
            "mobile": (True, None),
        }
        for name, (value, unit) in values.items():
            builder.add_metric(
                name=name,
                value=value,
                unit=unit,
                evidence_ref=f"metric://{name}/001",
            )
        return builder

    def complete_builder(self):
        builder = self.builder()
        builder.add_capability_lease_ref(
            "lease://kpgs/fivesarena/001"
        )
        self.add_trace(builder)
        self.add_promotion_artifacts(builder)
        self.add_promotion_metrics(builder)
        builder.add_verification(
            verifier_id="verifier:release-gate",
            criterion_id="security-hard-gate",
            method="security",
            hard_gate=True,
            passed=True,
            score=1.0,
            evidence_ref="verification://security/001",
        )
        builder.add_verification(
            verifier_id="verifier:quality",
            criterion_id="mobile-quality",
            method="e2e",
            hard_gate=False,
            passed=True,
            score=0.93,
            evidence_ref="verification://mobile/001",
        )
        builder.set_aggregate_score("quality", 0.97)
        return builder

    def test_valid_production_bundle_has_exact_release_commit_and_shared_scorecards(self):
        bundle = self.complete_builder().finalize(
            decision="promote",
            reason="All hard gates and required release evidence passed.",
            decision_ref="decision://release/allow/001",
            next_action="Observe production health and retain rollback readiness.",
        )
        self.assertTrue(bundle["bundle_id"].startswith("evidence_"))
        self.assertEqual(bundle["release_ref"], "release://fivesarena/2026-08-18")
        self.assertEqual(bundle["commit_sha"], "a" * 40)
        self.assertEqual(bundle["governance_decision"]["decision"], "promote")

        engineering = mod.engineering_scorecard(bundle)
        everyday = mod.everyday_scorecard(bundle)
        self.assertEqual(engineering["bundle_id"], bundle["bundle_id"])
        self.assertEqual(everyday["bundle_id"], bundle["bundle_id"])
        self.assertEqual(engineering["correlation_id"], everyday["correlation_id"])
        self.assertTrue(engineering["hard_gate_clear"])
        self.assertEqual(everyday["status"], "ready")
        self.assertEqual(everyday["risk"], "governed")
        self.assertIn("aaaaaaaaaaaa", everyday["what_changed"])

    def test_failed_hard_gate_cannot_be_hidden_by_high_aggregate_score(self):
        builder = self.complete_builder()
        builder.add_verification(
            verifier_id="verifier:release-gate",
            criterion_id="tenant-isolation",
            method="security",
            hard_gate=True,
            passed=False,
            score=0.0,
            evidence_ref="verification://security/fail",
        )
        builder.set_aggregate_score("health", 0.9999)
        with self.assertRaises(mod.HardGateFailure):
            builder.finalize(
                decision="promote",
                reason="Aggregate score is high.",
            )
        with self.assertRaises(mod.HardGateFailure):
            builder.finalize(
                decision="allow",
                reason="Aggregate score is high.",
            )

        held = builder.finalize(
            decision="hold",
            reason="Tenant isolation hard gate failed.",
            next_action="Repair tenant isolation and re-run verification.",
        )
        engineering = mod.engineering_scorecard(held)
        everyday = mod.everyday_scorecard(held)
        self.assertEqual(engineering["aggregate_scores"]["health"], 0.9999)
        self.assertFalse(engineering["hard_gate_clear"])
        self.assertEqual(
            engineering["hard_gate_failures"][0]["criterion_id"],
            "tenant-isolation",
        )
        self.assertEqual(everyday["status"], "blocked")
        self.assertIn("tenant-isolation", everyday["hard_gate_failures"])

    def test_security_verification_cannot_be_downgraded_to_soft_gate(self):
        builder = self.builder()
        with self.assertRaises(mod.EvidenceError):
            builder.add_verification(
                verifier_id="verifier:security",
                criterion_id="tenant-isolation",
                method="security",
                hard_gate=False,
                passed=False,
                evidence_ref="verification://security/softened",
            )

    def test_trace_must_cover_pwa_adapter_hub_renter_skill_and_verifier(self):
        builder = self.builder()
        builder.add_capability_lease_ref("lease://kpgs/001")
        for layer in ["pwa", "adapter", "renter", "skill"]:
            builder.add_trace_hop(
                layer=layer,
                ref=f"{layer}://trace",
                status="succeeded",
                at="2026-08-18T10:00:00Z",
            )
        builder.add_verification(
            verifier_id="verifier:release-gate",
            criterion_id="criterion",
            method="unit",
            hard_gate=False,
            passed=True,
            evidence_ref="verification://criterion",
        )
        with self.assertRaises(mod.EvidenceCorrelationError) as captured:
            builder.finalize(decision="hold", reason="Trace incomplete")
        self.assertIn("sovereign-hub", str(captured.exception))
        self.assertIn("verifier", str(captured.exception))

    def test_verifier_trace_must_correlate_to_real_verification(self):
        builder = self.builder()
        builder.add_capability_lease_ref("lease://kpgs/001")
        self.add_trace(builder)
        builder.add_verification(
            verifier_id="verifier:different",
            criterion_id="criterion",
            method="unit",
            hard_gate=False,
            passed=True,
            evidence_ref="verification://criterion",
        )
        with self.assertRaises(mod.EvidenceCorrelationError):
            builder.finalize(decision="hold", reason="Verifier mismatch")

    def test_promotion_requires_complete_artifact_and_metric_surface(self):
        builder = self.builder()
        builder.add_capability_lease_ref("lease://kpgs/001")
        self.add_trace(builder)
        builder.add_verification(
            verifier_id="verifier:release-gate",
            criterion_id="release-gate",
            method="security",
            hard_gate=True,
            passed=True,
            evidence_ref="verification://release",
        )
        builder.add_artifact(
            kind="deployment",
            ref="deployment://only",
        )
        builder.add_metric(
            name="latency",
            value=100.0,
            unit="ms",
            evidence_ref="metric://latency",
        )
        with self.assertRaises(mod.EvidenceCorrelationError):
            builder.finalize(decision="promote", reason="Evidence incomplete")

    def test_secret_like_material_is_rejected_from_trace_and_artifacts(self):
        builder = self.builder()
        with self.assertRaises(mod.EvidenceError):
            builder.add_trace_hop(
                layer="pwa",
                ref="pwa://trace",
                status="started",
                at="2026-08-18T10:00:00Z",
                metadata={"authorization": "Bearer abcdefghijklmnop"},
            )
        with self.assertRaises(mod.EvidenceError):
            builder.add_artifact(
                kind="security",
                ref="log://contains/sk-proj-abcdefghijklmnop",
            )
        with self.assertRaises(mod.EvidenceError):
            builder.add_capability_lease_ref(
                "lease://eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyLTEyMyJ9.signature12345678"
            )

    def test_policy_and_lease_fields_must_be_references_not_embedded_values(self):
        with self.assertRaises(mod.EvidenceError):
            self.builder(retention_policy_ref="thirty-days")
        builder = self.builder()
        with self.assertRaises(mod.EvidenceError):
            builder.add_capability_lease_ref(
                "eyJhbGciOiJIUzI1NiJ9.payload.signature"
            )

    def test_commit_sha_is_exact_release_provenance(self):
        with self.assertRaises(mod.EvidenceCorrelationError):
            self.builder(commit_sha="main")
        with self.assertRaises(mod.EvidenceCorrelationError):
            self.builder(commit_sha="abc123")

    def test_rollback_recommendation_never_executes_rollback_itself(self):
        builder = self.complete_builder()
        bundle = builder.finalize(
            decision="hold",
            reason="Observe reliability before promotion.",
        )
        recommendation = mod.rollback_recommendation(
            bundle,
            metric_thresholds={
                "error-rate": {
                    "operator": "gt",
                    "value": 0.0005,
                }
            },
        )
        self.assertTrue(recommendation["triggered"])
        self.assertFalse(recommendation["automatic_execution"])
        self.assertEqual(
            recommendation["required_capability"],
            "estate.release.rollback",
        )
        self.assertTrue(
            any("error-rate" in reason for reason in recommendation["reasons"])
        )

    def test_hard_failure_alone_triggers_rollback_recommendation(self):
        builder = self.complete_builder()
        builder.add_verification(
            verifier_id="verifier:release-gate",
            criterion_id="security-regression",
            method="security",
            hard_gate=True,
            passed=False,
            evidence_ref="verification://security/regression",
        )
        bundle = builder.finalize(
            decision="rollback",
            reason="Security regression detected after release.",
        )
        recommendation = mod.rollback_recommendation(bundle)
        self.assertTrue(recommendation["triggered"])
        self.assertIn(
            "hard gate failed: security-regression",
            recommendation["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
