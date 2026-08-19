from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "governance/kpgs-vnext/migration/migration.py"
ESTATE_PATH = ROOT / "governance/kpgs-vnext/estate-registry/estate.json"

spec = importlib.util.spec_from_file_location("kpgs_estate_migration_test", MODULE_PATH)
assert spec and spec.loader
migration = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = migration
spec.loader.exec_module(migration)


def property_record(domain: str, *, status: str = "registered"):
    slug = domain.lower().replace(".", "-")
    return {
        "domain": domain,
        "status": status,
        "owner": {"ref": "owner://robynawesome", "kind": "human"},
        "ownership_evidence": [
            {
                "kind": "domain-control",
                "ref": f"evidence://domain-control/{slug}",
                "verified_at": "2026-08-20T00:00:00Z",
            }
        ],
        "repositories": [
            {
                "repository": f"RobynAwesome/{slug}",
                "role": "application",
                "ref": f"commit://{'a' * 40}",
            }
        ],
        "deployment": {
            "provider": "reference-host",
            "environment": "staging",
            "target": f"https://staging.{domain.lower()}",
        },
        "adapter": {
            "required": True,
            "implementation": "Kopano.Kpgs.Adapter",
            "version": "0.1.0-preview.1",
        },
        "renter_compatibility": {"status": "conformant", "protocol_version": "1.0"},
        "governance": {
            "policy_ref": "policy://kpgs/reference-migration",
            "risk_class": "R1",
            "tier": "reference",
        },
        "capabilities": ["task.create", "task.command", "evidence.read"],
        "health_endpoints": [f"https://staging.{domain.lower()}/kpgs/health"],
        "release": {"live_ref": None, "evidence_ref": None},
        "rollback": {
            "target_ref": f"release://{slug}/previous",
            "procedure_ref": "repo://governance/kpgs-vnext/migration/README.md#rollback-drill",
        },
        "notes": ["CI reference fixture only; not canonical estate state."],
    }


def evaluation_receipt(*, decision: str = "hold", hard_failures=None, human_approval_ref=None):
    return {
        "schema": "kpgs.evaluation-live-reference-receipt.v1",
        "commit_sha": "b" * 40,
        "scorecard": {"hard_gate_failures": list(hard_failures or [])},
        "evidence_bundle": {
            "bundle_id": "evidence_reference_001",
            "governance_decision": {"decision": "allow"},
        },
        "promotion_decision": {
            "decision_id": "promotion_reference_001",
            "decision": decision,
            "human_approval_ref": human_approval_ref,
        },
    }


def rollback_receipt(*, passed=True, automatic_execution=False):
    return {
        "schema": "kpgs.estate-rollback-drill.v1",
        "passed": passed,
        "automatic_execution": automatic_execution,
        "evidence_refs": ["ci://migration/rollback-drill"],
    }


class EstateMigrationTests(unittest.TestCase):
    def test_live_canonical_estate_remains_truthful_hold_without_witness_enrichment(self):
        estate = json.loads(ESTATE_PATH.read_text(encoding="utf-8"))
        before = json.dumps(estate, sort_keys=True)
        assessments = migration.assess_estate(estate, workflow_id="bounded-pilot")

        self.assertEqual(len(assessments), 6)
        self.assertTrue(all(item["recommendation"] == "HOLD" for item in assessments))
        self.assertTrue(all(item["ready_for_staging"] is False for item in assessments))
        self.assertTrue(all(item["canonical_registry_changed"] is False for item in assessments))
        self.assertTrue(
            all(
                item["stages"]["register"]["status"] == "HOLD"
                for item in assessments
            )
        )
        self.assertEqual(json.dumps(estate, sort_keys=True), before)

    def test_kasilink_reference_workflow_reaches_staging_eligibility_but_not_production(self):
        record = property_record("KasiLink.com")
        result = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=record,
            workflow_id="gig-create",
            evaluation_receipt=evaluation_receipt(decision="hold"),
        )

        self.assertTrue(result["ready_for_staging"])
        self.assertFalse(result["ready_for_production"])
        self.assertEqual(result["recommendation"], "ELIGIBLE_FOR_STAGING_TRANSITION")
        self.assertEqual(result["stages"]["evaluation"]["status"], "PASS")
        self.assertEqual(result["stages"]["production_promotion"]["status"], "NOT_REACHED")
        self.assertFalse(result["canonical_registry_changed"])
        self.assertEqual(result["authority_effect"], "none")

    def test_same_playbook_is_reusable_on_second_property(self):
        first = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=property_record("KasiLink.com"),
            workflow_id="bounded-create",
            evaluation_receipt=evaluation_receipt(),
        )
        second = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=property_record("starfallsalvage.kopanolabs.com"),
            workflow_id="bounded-create",
            evaluation_receipt=evaluation_receipt(),
        )
        replay = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=property_record("KasiLink.com"),
            workflow_id="bounded-create",
            evaluation_receipt=evaluation_receipt(),
        )

        self.assertTrue(first["ready_for_staging"])
        self.assertTrue(second["ready_for_staging"])
        self.assertNotEqual(first["migration_id"], second["migration_id"])
        self.assertEqual(first["migration_id"], replay["migration_id"])

    def test_hard_evaluation_failure_blocks_staging(self):
        result = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=property_record("KasiLink.com"),
            workflow_id="gig-create",
            evaluation_receipt=evaluation_receipt(
                hard_failures=["renter-capability-denial"]
            ),
        )
        self.assertFalse(result["ready_for_staging"])
        self.assertEqual(result["stages"]["evaluation"]["status"], "HOLD")
        self.assertEqual(result["stages"]["staging"]["status"], "NOT_REACHED")

    def test_production_eligibility_requires_staging_release_rollback_and_human_approval(self):
        record = property_record("KasiLink.com", status="staging")
        record["release"] = {
            "live_ref": "release://kasilink/candidate",
            "evidence_ref": "evidence://kasilink/candidate",
        }
        result = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=record,
            workflow_id="gig-create",
            evaluation_receipt=evaluation_receipt(
                decision="promote", human_approval_ref="human://approval/reference"
            ),
            rollback_drill=rollback_receipt(),
        )

        self.assertTrue(result["ready_for_staging"])
        self.assertTrue(result["ready_for_production"])
        self.assertEqual(result["recommendation"], "ELIGIBLE_FOR_PRODUCTION_TRANSITION")
        self.assertEqual(result["stages"]["rollback_drill"]["status"], "PASS")
        self.assertEqual(result["stages"]["production_promotion"]["status"], "PASS")
        self.assertFalse(result["canonical_registry_changed"])

    def test_production_remains_blocked_without_human_approval(self):
        record = property_record("KasiLink.com", status="staging")
        record["release"] = {
            "live_ref": "release://kasilink/candidate",
            "evidence_ref": "evidence://kasilink/candidate",
        }
        result = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=record,
            workflow_id="gig-create",
            evaluation_receipt=evaluation_receipt(decision="promote"),
            rollback_drill=rollback_receipt(),
        )
        self.assertFalse(result["ready_for_production"])
        self.assertEqual(result["stages"]["production_promotion"]["status"], "NOT_REACHED")

    def test_rollback_receipt_cannot_claim_automatic_authority(self):
        record = property_record("KasiLink.com", status="staging")
        result = migration.assess_migration(
            estate_id="kopano-sovereign-estate",
            property_record=record,
            workflow_id="gig-create",
            evaluation_receipt=evaluation_receipt(),
            rollback_drill=rollback_receipt(automatic_execution=True),
        )
        self.assertEqual(result["stages"]["rollback_drill"]["status"], "HOLD")
        self.assertFalse(result["ready_for_production"])


if __name__ == "__main__":
    unittest.main()
