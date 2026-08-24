from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ESTATE_PATH = ROOT / "governance/kpgs-vnext/estate-registry/estate.json"
WITNESS_PATH = (
    ROOT
    / "governance/kpgs-vnext/estate-registry/evidence/live-provider-witness-2026-08-24.json"
)
MIGRATION_PATH = ROOT / "governance/kpgs-vnext/migration/migration.py"

spec = importlib.util.spec_from_file_location("kpgs_live_estate_migration", MIGRATION_PATH)
assert spec and spec.loader
migration = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = migration
spec.loader.exec_module(migration)


class LiveEstateWitnessAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.estate = json.loads(ESTATE_PATH.read_text(encoding="utf-8"))
        cls.witness = json.loads(WITNESS_PATH.read_text(encoding="utf-8"))
        cls.records = {item["domain"]: item for item in cls.estate["properties"]}
        cls.receipts = {item["domain"]: item for item in cls.witness["properties"]}

    def test_only_witnessed_properties_move_from_pending_state(self):
        self.assertEqual(len(self.records), 6)
        self.assertEqual(self.records["KasiLink.com"]["status"], "witnessed")
        self.assertEqual(
            self.records["starfallsalvage.kopanolabs.com"]["status"], "witnessed"
        )
        for domain in (
            "FivesArena.com",
            "crisisconnect.kopanolabs.com",
            "KopanoLabs.com",
            "KRRababalela.com",
        ):
            self.assertEqual(self.records[domain]["status"], "declared_pending_witness")
            self.assertEqual(self.records[domain]["ownership_evidence"], [])

    def test_witness_receipt_is_non_mutating_provider_evidence(self):
        self.assertEqual(self.witness["schema"], "kpgs.live-provider-witness.v1")
        self.assertEqual(self.witness["authority_effect"], "witness-only")
        self.assertFalse(self.witness["provider_mutation_performed"])
        self.assertEqual(set(self.receipts), {"KasiLink.com", "starfallsalvage.kopanolabs.com"})
        for receipt in self.receipts.values():
            self.assertEqual(receipt["admission_recommendation"], "WITNESS")
            self.assertTrue(receipt["domain_bindings"])
            self.assertTrue(receipt["deployments"])
            self.assertTrue(receipt["unknowns"])

    def test_starfall_exact_provider_repo_release_and_rollback_receipts(self):
        record = self.records["starfallsalvage.kopanolabs.com"]
        self.assertEqual(
            record["repositories"][0]["repository"], "RobynAwesome/starfall-salvage"
        )
        self.assertEqual(
            record["repositories"][0]["ref"],
            "commit://fea307d09a8552cec72e0a6bcb5440cd173bef41",
        )
        self.assertIn("prj_rik2lQSlmHm7CIUhEGZMprZ5CFcN", record["deployment"]["target"])
        self.assertIn("dpl_8Myns9BqgPovBtTaC1ZsrjtNwCuP", record["release"]["live_ref"])
        self.assertIn("dpl_9X3gbZpWuRWK5N3XC7Unvtd1doDR", record["rollback"]["target_ref"])
        self.assertIn("#starfall-rollback-procedure", record["rollback"]["procedure_ref"])
        self.assertIsNone(record["adapter"]["implementation"])
        self.assertEqual(record["renter_compatibility"]["status"], "unknown")
        self.assertIsNone(record["governance"]["policy_ref"])
        self.assertNotIn("capabilities", record)
        self.assertNotIn("health_endpoints", record)

    def test_starfall_witness_does_not_self_promote_migration(self):
        record = self.records["starfallsalvage.kopanolabs.com"]
        result = migration.assess_migration(
            estate_id=self.estate["estate_id"],
            property_record=record,
            workflow_id="live-estate-witness-2026-08-24",
        )
        self.assertEqual(result["recommendation"], "HOLD")
        self.assertFalse(result["ready_for_staging"])
        self.assertFalse(result["ready_for_production"])
        self.assertEqual(result["stages"]["register"]["status"], "HOLD")
        self.assertEqual(result["stages"]["adapter_integration"]["status"], "HOLD")
        self.assertEqual(result["stages"]["renter_integration"]["status"], "HOLD")
        self.assertFalse(result["canonical_registry_changed"])

    def test_kasilink_preserves_split_provider_identity_and_hold(self):
        record = self.records["KasiLink.com"]
        self.assertEqual(record["repositories"][0]["repository"], "RobynAwesome/KasiLink")
        self.assertEqual(
            record["repositories"][0]["ref"],
            "commit://1080fb18096cb2b5c9f8a9ea0d12b442b80329f4",
        )
        self.assertEqual(record["deployment"]["environment"], "production-split")
        self.assertIsNone(record["deployment"]["target"])
        targets = "\n".join(
            item["target"] for item in record["deployment"]["environments"]
        )
        self.assertIn("prj_07Q4oRr2okeBiPO12YotAzHZM10b", targets)
        self.assertIn("dpl_9PMFHyTv9jP78sASJaZD5hGX47yr", targets)
        self.assertIn("prj_A1AvVl5WYRyTergoEcMsvEmMM3uX", targets)
        self.assertIn("dpl_AA9iSMwcpHPGvqtRc5mEFjMpywha", targets)
        self.assertIsNone(record["release"]["live_ref"])

        result = migration.assess_migration(
            estate_id=self.estate["estate_id"],
            property_record=record,
            workflow_id="live-estate-witness-2026-08-24",
        )
        self.assertEqual(result["recommendation"], "HOLD")
        self.assertEqual(result["stages"]["baseline"]["status"], "HOLD")
        self.assertEqual(result["stages"]["register"]["status"], "HOLD")
        self.assertFalse(result["canonical_registry_changed"])

    def test_connected_provider_refs_not_public_http_as_ownership_proof(self):
        for domain in ("KasiLink.com", "starfallsalvage.kopanolabs.com"):
            evidence = self.records[domain]["ownership_evidence"]
            self.assertTrue(evidence)
            for item in evidence:
                self.assertFalse(item["ref"].startswith("http://"))
                self.assertFalse(item["ref"].startswith("https://"))
                self.assertTrue(
                    item["ref"].startswith("vercel://")
                    or item["ref"].startswith("github://")
                )


if __name__ == "__main__":
    unittest.main()
