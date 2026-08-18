import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parents[1]
LEASE_PATH = ROOT / "governance" / "kpgs-vnext" / "security" / "capability_lease.py"
REGISTRY_PATH = ROOT / "governance" / "kpgs-vnext" / "estate-registry" / "registry.py"
ESTATE_PATH = ROOT / "governance" / "kpgs-vnext" / "estate-registry" / "estate.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lease_mod = load_module("kpgs_lease_for_registry", LEASE_PATH)
registry_mod = load_module("kpgs_estate_registry", REGISTRY_PATH)


class FixedClock:
    def __init__(self):
        self.now = datetime(2026, 8, 18, 9, 30, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


class SovereignEstateRegistryTests(unittest.TestCase):
    def setUp(self):
        self.clock = FixedClock()
        self.lease_authority = lease_mod.CapabilityLeaseAuthority(
            lease_mod.KeyRing({"estate-k1": b"e" * 32}, "estate-k1"),
            clock=self.clock,
            max_ttl_seconds=900,
        )
        self.estate = json.loads(ESTATE_PATH.read_text(encoding="utf-8"))
        self.token = self.lease_authority.issue(
            subject_id="service:sovereign-hub",
            subject_kind="service",
            tenant_id="tenant:kopano",
            domain_id="KopanoLabs.com",
            task_id="task:estate-governance",
            capabilities=[
                {
                    "name": "estate.discovery.write",
                    "resource_scope": "estate:kopano-sovereign-estate",
                },
                {
                    "name": "estate.registry.witness",
                    "resource_scope": "dns:candidate.example.org",
                },
                {
                    "name": "estate.registry.classify",
                    "resource_scope": "dns:candidate.example.org",
                },
                {
                    "name": "estate.registry.write",
                    "resource_scope": "dns:candidate.example.org",
                },
                {
                    "name": "estate.registry.witness",
                    "resource_scope": "dns:KasiLink.com",
                },
                {
                    "name": "estate.registry.write",
                    "resource_scope": "dns:KasiLink.com",
                },
                {
                    "name": "estate.release.transition",
                    "resource_scope": "dns:KasiLink.com",
                },
                {
                    "name": "estate.release.rollback",
                    "resource_scope": "dns:KasiLink.com",
                },
            ],
            policy_decision_ref="policy://estate/control-plane",
            governing_spec_ref="spec://kpgs/estate-registry/v1",
            ttl_seconds=600,
            correlation_id="corr:estate-lease",
            evidence_ref="evidence://estate/lease",
        )
        self.registry = registry_mod.SovereignEstateRegistry(
            self.estate,
            self.lease_authority,
            clock=self.clock,
        )

    def context(self, nonce, *, tenant_id="tenant:kopano"):
        return registry_mod.MutationContext(
            token=self.token,
            tenant_id=tenant_id,
            domain_id="KopanoLabs.com",
            task_id="task:estate-governance",
            operation_nonce=nonce,
            correlation_id=f"corr:{nonce}",
        )

    @staticmethod
    def registered_metadata(domain):
        return {
            "domain": domain,
            "repositories": [
                {
                    "repository": "RobynAwesome/example-runtime",
                    "role": "primary",
                    "ref": "commit:abc123",
                }
            ],
            "deployment": {
                "provider": "vercel",
                "environment": "staging",
                "target": f"https://{domain}",
                "environments": [
                    {
                        "name": "staging",
                        "provider": "vercel",
                        "target": f"https://staging.{domain}",
                    },
                    {
                        "name": "production",
                        "provider": "vercel",
                        "target": f"https://{domain}",
                    },
                ],
            },
            "adapter": {
                "required": True,
                "implementation": "canonical-domain-adapter",
                "version": "contract-v1",
            },
            "renter_compatibility": {
                "status": "partial",
                "protocol_version": "1.0",
            },
            "governance": {
                "policy_ref": "policy://estate/property",
                "risk_class": "R1",
                "tier": "T1",
            },
            "owner": {"ref": "owner://declared", "kind": "declared-owner"},
            "skills": ["estate-observer"],
            "capabilities": ["domain.health.read"],
            "secret_provider_refs": ["vault://estate/runtime-reference"],
            "health_endpoints": [f"https://{domain}/health"],
            "release": {"live_ref": None, "evidence_ref": None},
            "rollback": {"target_ref": None, "procedure_ref": None},
            "notes": ["test fixture only; not ownership evidence"],
        }

    def test_initial_six_domains_remain_present_and_unpromoted(self):
        snapshot = self.registry.snapshot()
        domains = {item["domain"] for item in snapshot["properties"]}
        self.assertEqual(
            domains,
            {
                "KasiLink.com",
                "FivesArena.com",
                "starfallsalvage.kopanolabs.com",
                "crisisconnect.kopanolabs.com",
                "KopanoLabs.com",
                "KRRababalela.com",
            },
        )
        self.assertTrue(
            all(item["status"] == "declared_pending_witness" for item in snapshot["properties"])
        )

    def test_discovery_enters_unwitnessed_queue_and_does_not_register_itself(self):
        candidate = self.registry.discover_candidate(
            "candidate.example.org",
            provenance={
                "kind": "dns",
                "ref": "dns://observed/candidate.example.org",
                "observed_at": "2026-08-18T09:30:00Z",
            },
            context=self.context("discover-001"),
        )
        self.assertEqual(candidate["status"], "unwitnessed")
        self.assertEqual(len(self.registry.candidates()), 1)
        domains = {item["domain"] for item in self.registry.snapshot()["properties"]}
        self.assertNotIn("candidate.example.org", domains)

    def test_duplicate_discovery_deduplicates_candidate_but_preserves_provenance(self):
        first = self.registry.discover_candidate(
            "candidate.example.org",
            provenance={
                "kind": "dns",
                "ref": "dns://first",
                "observed_at": "2026-08-18T09:30:00Z",
            },
            context=self.context("discover-002"),
        )
        second = self.registry.discover_candidate(
            "CANDIDATE.example.org.",
            provenance={
                "kind": "repository",
                "ref": "github://second",
                "observed_at": "2026-08-18T09:31:00Z",
            },
            context=self.context("discover-003"),
        )
        self.assertEqual(first["candidate_id"], second["candidate_id"])
        self.assertEqual(len(second["provenance"]), 2)
        self.assertEqual(len(self.registry.candidates()), 1)

    def test_candidate_requires_witness_then_classification_then_registration(self):
        candidate = self.registry.discover_candidate(
            "candidate.example.org",
            provenance={
                "kind": "repository",
                "ref": "github://candidate",
                "observed_at": "2026-08-18T09:30:00Z",
            },
            context=self.context("discover-004"),
        )
        with self.assertRaises(registry_mod.RegistryTransitionDenied):
            self.registry.register_candidate(
                candidate["candidate_id"],
                self.registered_metadata("candidate.example.org"),
                context=self.context("register-too-early"),
            )

        witnessed = self.registry.witness_candidate(
            candidate["candidate_id"],
            {
                "kind": "domain-control",
                "ref": "witness://domain-control/001",
                "verified_at": "2026-08-18T09:32:00Z",
            },
            context=self.context("witness-candidate"),
        )
        self.assertEqual(witnessed["status"], "witnessed")

        classified = self.registry.classify_candidate(
            candidate["candidate_id"],
            owner_ref="owner://verified/001",
            governance_tier="T1",
            risk_class="R1",
            context=self.context("classify-candidate"),
        )
        self.assertEqual(classified["status"], "classified")

        registered = self.registry.register_candidate(
            candidate["candidate_id"],
            self.registered_metadata("candidate.example.org"),
            context=self.context("register-candidate"),
        )
        self.assertEqual(registered["status"], "registered")
        self.assertEqual(registered["owner"]["ref"], "owner://declared")
        self.assertEqual(registered["ownership_evidence"][0]["kind"], "domain-control")

    def test_cross_tenant_mutation_is_denied_by_capability_lease(self):
        with self.assertRaises(lease_mod.LeaseDenied):
            self.registry.discover_candidate(
                "candidate.example.org",
                provenance={
                    "kind": "dns",
                    "ref": "dns://candidate",
                    "observed_at": "2026-08-18T09:30:00Z",
                },
                context=self.context("cross-tenant", tenant_id="tenant:other"),
            )
        self.assertEqual(self.registry.candidates(), ())

    def test_existing_declared_property_cannot_skip_witness_or_registration(self):
        with self.assertRaises(registry_mod.RegistryTransitionDenied):
            self.registry.transition_property(
                "KasiLink.com",
                "production",
                context=self.context("skip-to-production"),
            )

        witnessed = self.registry.witness_property(
            "KasiLink.com",
            {
                "kind": "domain-control",
                "ref": "witness://kasilink/control",
                "verified_at": "2026-08-18T09:30:00Z",
            },
            context=self.context("witness-kasilink"),
        )
        self.assertEqual(witnessed["status"], "witnessed")

        registered = self.registry.register_property(
            "KasiLink.com",
            self.registered_metadata("KasiLink.com"),
            context=self.context("register-kasilink"),
        )
        self.assertEqual(registered["status"], "registered")

    def test_promotion_requires_release_evidence_and_rollback_then_rollback_is_explicit(self):
        self.registry.witness_property(
            "KasiLink.com",
            {
                "kind": "domain-control",
                "ref": "witness://kasilink/control",
                "verified_at": "2026-08-18T09:30:00Z",
            },
            context=self.context("witness-kasilink-2"),
        )
        self.registry.register_property(
            "KasiLink.com",
            self.registered_metadata("KasiLink.com"),
            context=self.context("register-kasilink-2"),
        )
        self.registry.transition_property(
            "KasiLink.com",
            "staging",
            context=self.context("stage-kasilink"),
        )
        with self.assertRaises(registry_mod.RegistryTransitionDenied):
            self.registry.transition_property(
                "KasiLink.com",
                "production",
                context=self.context("promote-without-receipts"),
            )

        production = self.registry.transition_property(
            "KasiLink.com",
            "production",
            release_ref="commit:live-002",
            evidence_ref="evidence://deploy/live-002",
            rollback_target_ref="commit:live-001",
            rollback_procedure_ref="runbook://rollback/kasilink",
            context=self.context("promote-kasilink"),
        )
        self.assertEqual(production["status"], "production")
        self.assertEqual(production["release"]["live_ref"], "commit:live-002")

        rolled_back = self.registry.rollback_property(
            "KasiLink.com",
            context=self.context("rollback-kasilink"),
        )
        self.assertEqual(rolled_back["status"], "staging")
        self.assertEqual(rolled_back["release"]["live_ref"], "commit:live-001")
        self.assertEqual(self.registry.events()[-1]["action"], "property-rollback")

    def test_plain_language_answer_exposes_location_version_and_rollback_state(self):
        text = self.registry.explain_property("FivesArena.com")
        self.assertIn("FivesArena.com is declared_pending_witness", text)
        self.assertIn("Repositories: not witnessed", text)
        self.assertIn("Deployment: not witnessed", text)
        self.assertIn("Live version: not promoted", text)
        self.assertIn("Rollback target: not recorded", text)

    def test_distribution_failure_does_not_erase_authorized_canonical_registry_commit(self):
        def fail_distribution(_event):
            raise RuntimeError("event plane unavailable")

        registry = registry_mod.SovereignEstateRegistry(
            self.estate,
            self.lease_authority,
            clock=self.clock,
            distribution_sink=fail_distribution,
        )
        result = registry.witness_property(
            "KasiLink.com",
            {
                "kind": "domain-control",
                "ref": "witness://kasilink/control",
                "verified_at": "2026-08-18T09:30:00Z",
            },
            context=self.context("witness-with-event-plane-down"),
        )
        self.assertEqual(result["status"], "witnessed")
        event = registry.events()[-1]
        self.assertEqual(event["distribution_status"], "unavailable")
        self.assertFalse(event["transport_grants_authority"])
        self.assertTrue(event["canonical_registry_changed"])


if __name__ == "__main__":
    unittest.main()
