import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVERYDAY = ROOT / "governance" / "kpgs-vnext" / "everyday-mode"


class CompanionInteractionProtocolTests(unittest.TestCase):
    def setUp(self):
        self.protocol = (EVERYDAY / "COMPANION_INTERACTION_PROTOCOL.md").read_text(encoding="utf-8")
        self.contract = json.loads((EVERYDAY / "companion-interaction-contract.json").read_text(encoding="utf-8"))

    def test_companion_is_default_and_operator_is_secondary(self):
        self.assertEqual(self.contract["default_mode"], "COMPANION")
        self.assertEqual(self.contract["operator_mode"], "SECONDARY")
        self.assertIn("USER -> COMPANION", self.protocol)

    def test_security_graph_fails_closed_without_exploit_detail(self):
        graph = self.contract["public_security_graph"]
        self.assertEqual(graph["nodes"], ["YOU", "COMPANION", "GUARD", "SYSTEM", "RECEIPT"])
        self.assertEqual(graph["bypass_outcome"], "BLOCKED_AT_GUARD")
        for exclusion in ("secrets", "tokens", "private_addresses", "exploit_recipes"):
            self.assertIn(exclusion, graph["public_exclusions"])

    def test_routing_receipt_cannot_masquerade_as_execution(self):
        self.assertFalse(self.contract["authority_invariants"]["route_receipt_equals_execution_receipt"])
        self.assertEqual(
            self.contract["execution_claims"],
            ["ROUTE_ONLY", "PROVIDER_EXECUTED", "TOOL_EXECUTED", "BLOCKED"],
        )

    def test_companion_turn_remains_bounded(self):
        turn = self.contract["companion_turn"]
        self.assertEqual(turn["max_primary_actions"], 3)
        for field in ("speaker", "message", "goal_summary", "actions", "route_summary", "proof_available", "execution_claim"):
            self.assertIn(field, turn["required"])

    def test_game_language_does_not_create_authority_or_evidence(self):
        invariants = self.contract["authority_invariants"]
        self.assertFalse(invariants["preferences_grant_authority"])
        self.assertFalse(invariants["game_progress_equals_real_progress"])
        self.assertFalse(invariants["simulation_equals_physical_evidence"])


if __name__ == "__main__":
    unittest.main()
