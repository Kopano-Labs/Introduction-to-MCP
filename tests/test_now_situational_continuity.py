from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
NOW = ROOT / "NOW.md"
AGENTS = ROOT / "AGENTS.md"
ENTRYWAY_MD = (
    ROOT
    / "Schematics"
    / "21-KOPANO-PHU GOVERNACE SYSTEMS"
    / "MAIN-BRAIN"
    / "STATELESS_RENTER_ENTRYWAY.md"
)
ENTRYWAY_JSON = ENTRYWAY_MD.with_suffix(".json")
RUNTIME_ENTRYWAY_JSON = ROOT / "docs" / "swarm-ops" / "STATELESS_RENTER_ENTRYWAY.json"
CONTINUITY = ROOT / "governance" / "kpgs-vnext" / "continuity" / "README.md"
TRANSITION_SCHEMA = CONTINUITY.with_name("situational-transition.schema.json")


class NowContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.now = NOW.read_text(encoding="utf-8")
        cls.agents = AGENTS.read_text(encoding="utf-8")
        cls.entryway_md = ENTRYWAY_MD.read_text(encoding="utf-8")
        cls.entryway = json.loads(ENTRYWAY_JSON.read_text(encoding="utf-8"))
        cls.runtime_entryway = json.loads(
            RUNTIME_ENTRYWAY_JSON.read_text(encoding="utf-8")
        )
        cls.continuity = CONTINUITY.read_text(encoding="utf-8")
        cls.transition_schema = json.loads(
            TRANSITION_SCHEMA.read_text(encoding="utf-8")
        )

    def test_root_now_is_current_state_authority_and_preserves_history(self):
        self.assertIn("Current-state authority", self.now)
        self.assertIn("CURRENT STATE — 2026-08-24", self.now)
        self.assertIn("HISTORICAL LOG — PRESERVED PROVENANCE", self.now)
        self.assertIn("2026-06-22T06:39 SAST", self.now)
        self.assertIn("repo root NOW.md is the comms lane", self.now)

    def test_agent_entry_cannot_bypass_root_now(self):
        self.assertIn("Read repository-root `NOW.md` before execution", self.agents)
        self.assertIn("update repository-root `NOW.md`", self.agents)
        self.assertIn("none substitutes for repository-root `NOW.md`", self.agents)
        self.assertIn("Read repository-root `NOW.md` before execution", self.entryway_md)
        self.assertIn("update repository-root `NOW.md`", self.entryway_md)
        self.assertIn("HOLD", self.entryway_md)

    def test_machine_entryways_bind_to_same_now_authority(self):
        for entryway in (self.entryway, self.runtime_entryway):
            self.assertEqual(entryway["current_state_authority"], "NOW.md")
            contract = entryway["current_state_contract"]
            self.assertTrue(contract["must_read_before_execution"])
            self.assertTrue(
                contract["must_update_before_handoff_when_material_state_changes"]
            )
            self.assertEqual(
                contract["stale_or_contradictory_behavior"],
                "HOLD_AND_RECONCILE",
            )
            instructions = "\n".join(entryway["on_entry_you_must"])
            self.assertIn("repository-root NOW.md", instructions)

    def test_situational_transition_schema_has_no_fixed_ccp_cdp_origin(self):
        outcome = self.transition_schema["properties"]["decision"]["properties"][
            "outcome"
        ]["enum"]
        self.assertEqual(
            set(outcome),
            {"CCP", "CDP", "CONVERGE", "DIVERGE", "HOLD"},
        )
        self.assertNotIn("origin_order", self.transition_schema["properties"])

    def test_transition_receipt_requires_governed_edge_evidence(self):
        required = set(self.transition_schema["required"])
        for field in (
            "trigger",
            "evidence_refs",
            "invariant_refs",
            "authority",
            "decision",
            "receipt_refs",
        ):
            self.assertIn(field, required)

    def test_hold_is_first_class_not_poc_validated(self):
        hold_rule = self.transition_schema["allOf"][0]
        self.assertEqual(
            hold_rule["if"]["properties"]["decision"]["properties"]["outcome"][
                "const"
            ],
            "HOLD",
        )
        allowed_proof = hold_rule["then"]["properties"]["proof_state"]["enum"]
        self.assertNotIn("POC_VALIDATED", allowed_proof)

    def test_continuity_doctrine_carries_full_feedback_architecture(self):
        expected = (
            "Do not prescribe the universe. Govern the transition.",
            "KPGS Capability Factory",
            "Reusable Primitive",
            "KasiLink Employment Engine",
            "Get paid",
            "weak hardware / low bandwidth",
            "Intern Vanguard C",
            "field-validation operator",
            "Context x Persistence x Consistency x Feedback Density",
        )
        for phrase in expected:
            self.assertIn(phrase, self.continuity)


if __name__ == "__main__":
    unittest.main()
