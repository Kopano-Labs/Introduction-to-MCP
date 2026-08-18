import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

MODULE_PATH = (
    Path(__file__).parents[1]
    / "governance"
    / "kpgs-vnext"
    / "security"
    / "capability_lease.py"
)
spec = importlib.util.spec_from_file_location("kpgs_capability_lease", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class MutableClock:
    def __init__(self):
        self.now = datetime(2026, 8, 18, 9, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += timedelta(seconds=seconds)


class CapabilityLeaseRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.clock = MutableClock()
        self.keys = mod.KeyRing({"k1": b"a" * 32}, "k1")
        self.authority = mod.CapabilityLeaseAuthority(
            self.keys,
            clock=self.clock,
            max_ttl_seconds=600,
        )

    def issue(self, **overrides):
        payload = dict(
            subject_id="renter:alpha",
            subject_kind="renter",
            tenant_id="tenant:kopano",
            domain_id="FivesArena.com",
            task_id="task:weather-read",
            capabilities=[
                {
                    "name": "estate.registry.read",
                    "resource_scope": "estate:kopano-labs",
                    "constraints": ["read-only"],
                },
                {
                    "name": "domain.weather.read",
                    "resource_scope": "FivesArena.com:province-context",
                },
            ],
            policy_decision_ref="policy://kpgs/allow/001",
            governing_spec_ref="spec://kpgs/task/weather-read/v1",
            ttl_seconds=300,
            secret_provider_refs=("vault://runtime/fivesarena-weather",),
            correlation_id="corr:lease-test",
            evidence_ref="evidence://lease/001",
        )
        payload.update(overrides)
        return self.authority.issue(**payload)

    def authorize(self, token, **overrides):
        payload = dict(
            tenant_id="tenant:kopano",
            domain_id="FivesArena.com",
            task_id="task:weather-read",
            capability="estate.registry.read",
            resource_scope="estate:kopano-labs",
            operation_nonce="operation-001",
            correlation_id="corr:use-001",
        )
        payload.update(overrides)
        return self.authority.authorize(token, **payload)

    def test_scoped_lease_authorizes_exact_capability_and_resource(self):
        token = self.issue()
        decision = self.authorize(token)
        self.assertEqual(decision.subject_id, "renter:alpha")
        self.assertEqual(decision.tenant_id, "tenant:kopano")
        self.assertEqual(decision.capability, "estate.registry.read")
        self.assertEqual(decision.resource_scope, "estate:kopano-labs")
        self.assertEqual(decision.key_id, "k1")

    def test_cross_tenant_domain_task_and_resource_mismatches_fail_closed(self):
        cases = [
            {"tenant_id": "tenant:other"},
            {"domain_id": "KasiLink.com"},
            {"task_id": "task:other"},
            {"resource_scope": "estate:other"},
            {"capability": "estate.registry.write"},
        ]
        for index, override in enumerate(cases):
            token = self.issue()
            with self.subTest(override=override):
                with self.assertRaises(mod.LeaseDenied):
                    self.authorize(
                        token,
                        operation_nonce=f"deny-{index:04d}",
                        **override,
                    )

    def test_expired_lease_fails_closed(self):
        token = self.issue(ttl_seconds=60)
        self.clock.advance(61)
        with self.assertRaises(mod.LeaseExpired):
            self.authorize(token)

    def test_revoked_lease_fails_closed(self):
        token = self.issue()
        lease_id = self.authority.revoke(
            token,
            reason="task cancelled",
            evidence_ref="evidence://revocation/001",
        )
        self.assertTrue(lease_id.startswith("lease_"))
        with self.assertRaises(mod.LeaseRevoked):
            self.authorize(token)

    def test_operation_nonce_replay_is_rejected_without_second_allow(self):
        token = self.issue()
        first = self.authorize(token, operation_nonce="same-operation")
        self.assertEqual(first.capability, "estate.registry.read")
        with self.assertRaises(mod.LeaseReplay):
            self.authorize(token, operation_nonce="same-operation")
        allowed = [
            event
            for event in self.authority.audit_events()
            if event["event"] == "capability-used" and event["outcome"] == "allow"
        ]
        self.assertEqual(len(allowed), 1)

    def test_signature_tamper_is_rejected(self):
        token = self.issue()
        parts = token.split(".")
        replacement = "A" if parts[1][-1] != "A" else "B"
        tampered = f"{parts[0]}.{parts[1][:-1]}{replacement}.{parts[2]}"
        with self.assertRaises(mod.LeaseSignatureError):
            self.authorize(tampered)

    def test_key_rotation_needs_no_frontend_redeploy_and_preserves_live_old_lease(self):
        old_token = self.issue()
        self.keys.rotate("k2", b"b" * 32)
        new_token = self.issue(task_id="task:weather-read")

        old_decision = self.authorize(
            old_token,
            operation_nonce="old-key-use",
        )
        new_decision = self.authorize(
            new_token,
            operation_nonce="new-key-use",
        )
        self.assertEqual(old_decision.key_id, "k1")
        self.assertEqual(new_decision.key_id, "k2")

    def test_short_lived_boundary_and_ambient_scope_are_enforced(self):
        with self.assertRaises(mod.LeaseDenied):
            self.issue(ttl_seconds=601)
        with self.assertRaises(mod.LeaseDenied):
            self.issue(
                capabilities=[
                    {"name": "admin", "resource_scope": "estate:kopano-labs"}
                ]
            )
        with self.assertRaises(mod.LeaseDenied):
            self.issue(
                capabilities=[
                    {"name": "estate.registry.read", "resource_scope": "*"}
                ]
            )

    def test_secret_provider_refs_are_references_not_raw_credentials(self):
        with self.assertRaises(mod.LeaseDenied):
            self.issue(secret_provider_refs=("sk-proj-this-is-not-a-reference",))
        token = self.issue(secret_provider_refs=("vault://runtime/reference-only",))
        lease, _ = self.authority.verify(token)
        self.assertEqual(
            lease["secret_provider_refs"],
            ["vault://runtime/reference-only"],
        )

    def test_audit_reconstructs_sensitive_use_without_token_or_secret_material(self):
        token = self.issue()
        decision = self.authorize(token)
        events = self.authority.audit_events()
        use_event = next(
            event
            for event in events
            if event["event"] == "capability-used" and event["outcome"] == "allow"
        )
        self.assertEqual(use_event["lease_id"], decision.lease_id)
        self.assertEqual(use_event["tenant_id"], "tenant:kopano")
        self.assertEqual(use_event["domain_id"], "FivesArena.com")
        self.assertEqual(use_event["task_id"], "task:weather-read")
        self.assertEqual(use_event["capability"], "estate.registry.read")
        self.assertEqual(use_event["resource_scope"], "estate:kopano-labs")
        serialized = repr(events)
        self.assertNotIn(token, serialized)
        self.assertNotIn("vault://runtime/fivesarena-weather", serialized)
        self.assertNotIn("aaaaaaaa", serialized)


if __name__ == "__main__":
    unittest.main()
