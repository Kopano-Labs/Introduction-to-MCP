"""
Test Suite for RTCP Pipeline: CRUD -> SWFUS -> BP -> BMP -> POCvsFOC vNext
Canonical Verification for Kopano Phu Governance Systems (KPGS)
"""

import sys
import unittest
from pathlib import Path

# Add kopano-core to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.rtcp_pipeline import (
    RtcpPipelineOrchestrator,
    CrudStage,
    SwfusStage,
    BracketProtocolStage,
    BlackMassProtocolStage,
    PocVsFocVnextEngine,
    ProofState,
    DirisaTier,
    FocGroup,
    SourceClass,
    EvidenceItem,
    ObservationalMembrane
)


class TestRtcpPipeline(unittest.TestCase):

    def setUp(self):
        self.orchestrator = RtcpPipelineOrchestrator()

    def test_stage_1_crud_invariant_12(self):
        """Mutating CRUD operations must be blocked until governance approval."""
        crud = CrudStage()
        
        # Read operation should be auto-approved
        read_op = crud.register("READ", "target/repo", {"path": "README.md"})
        self.assertFalse(read_op.is_mutating)
        self.assertTrue(read_op.governance_approved)
        res_read = crud.execute_if_permitted(read_op)
        self.assertEqual(res_read["status"], "EXECUTED")

        # Mutating operation must NOT be auto-approved
        write_op = crud.register("CREATE", "target/repo", {"file": "new.py"})
        self.assertTrue(write_op.is_mutating)
        self.assertFalse(write_op.governance_approved)
        res_write = crud.execute_if_permitted(write_op)
        self.assertEqual(res_write["status"], "BLOCKED_BY_INVARIANT_12")

    def test_stage_2_swfus_event_dispatch(self):
        """SWFUS must dispatch progressive sync events and support offline queues."""
        swfus = SwfusStage()
        evt_online = swfus.dispatch("kpgs/governance", "STATE_SYNC", {"branch": "master"})
        self.assertTrue(evt_online.synchronized)
        self.assertFalse(evt_online.is_offline_queued)

        evt_offline = swfus.dispatch("kpgs/pwa", "OFFLINE_OP", {"op": "create_gig"}, offline=True)
        self.assertFalse(evt_offline.synchronized)
        self.assertTrue(evt_offline.is_offline_queued)

    def test_stage_3_bracket_protocol_lane_isolation(self):
        """Bracket protocol must seal valid lanes and reject unauthorized lanes."""
        bp = BracketProtocolStage()
        res_valid = bp.isolate("concept-001", "DIRISA_RESEARCH")
        self.assertEqual(res_valid["status"], "BRACKETED")
        self.assertTrue(res_valid["boundary_sealed"])

        res_invalid = bp.isolate("concept-002", "UNAUTHORIZED_CROSS_LANE")
        self.assertEqual(res_invalid["status"], "INVALID_LANE")

    def test_stage_4_black_mass_protocol_kinetic_standards(self):
        """Black Mass Protocol must enforce wall-clock dt budget, offline resilience, and zero-PII."""
        bmp = BlackMassProtocolStage()
        
        # 60fps frame budget is <= 16.67ms
        pass_res = bmp.test("Starfall kinetic runner", dt_ms=14.2, requires_offline=True, pii_free=True)
        self.assertTrue(pass_res.passed)

        # Budget exceeded (e.g. 24ms)
        fail_dt = bmp.test("Slow animation", dt_ms=25.0)
        self.assertFalse(fail_dt.passed)
        self.assertTrue(any("Wall-Clock Timers" in f for f in fail_dt.failed_commands))

        # PII leak detected
        fail_pii = bmp.test("Extractive analytics", dt_ms=10.0, pii_free=False)
        self.assertFalse(fail_pii.passed)
        self.assertTrue(any("Sovereign Identity" in f for f in fail_pii.failed_commands))

    def test_stage_5_poc_vs_foc_vnext_grounded_validation(self):
        """Physical metal and git evidence validate a claim to POC_VALIDATED."""
        poc = PocVsFocVnextEngine()
        evidence = [
            EvidenceItem(
                source_class=SourceClass.PHYSICAL_METAL,
                authority_for=["local_filesystem"],
                reference="C:\\Users\\rkhol\\Bookit-5s-Arena",
                verified=True
            ),
            EvidenceItem(
                source_class=SourceClass.GITHUB_CLOUD,
                authority_for=["remote_head"],
                reference="Kopano-Labs/Bookit-5s-Arena@a014a98f",
                verified=True
            )
        ]
        obs = ObservationalMembrane(
            D_t=[{"metric": "git_log_depth", "val": 150}],
            F_t=[{"metric": "commit_frequency", "val": "daily"}],
            G_t=[{"metric": "estate_layer", "val": "sports_booking"}],
            R_t=[{"metric": "org_binding", "val": "Kopano-Labs"}]
        )
        ecosystem = {"E_P": "KNOWN", "E_W": "KNOWN", "E_R": "KNOWN"}

        receipt = poc.evaluate(
            concept_id="bookit-core",
            claim="Bookit 5s Arena is verified on local metal and cloud remote",
            scope="KPGS::FIVES_ARENA_SPORTS",
            lane="FIVES_ARENA_SPORTS",
            evidence=evidence,
            observation=obs,
            ecosystem_states=ecosystem
        )

        self.assertEqual(receipt.state, ProofState.POC_VALIDATED)
        self.assertEqual(len(receipt.foc_groups), 0)
        self.assertFalse(receipt.divergence.has_divergence())

    def test_stage_5_model_only_evidence_produces_framework_of_concept(self):
        """Model inference alone cannot create proof authority; it produces Framework of Concept."""
        poc = PocVsFocVnextEngine()
        evidence = [
            EvidenceItem(
                source_class=SourceClass.MODEL_INFERENCE,
                authority_for=["speculation"],
                reference="GPT-5.6 inference without receipts",
                verified=False
            )
        ]
        obs = ObservationalMembrane()
        ecosystem = {"E_P": "UNKNOWN", "E_W": "MAYBE", "E_R": "UNKNOWN"}

        receipt = poc.evaluate(
            concept_id="speculative-claim",
            claim="The rover climbs Olympus Mons in simulation",
            scope="KPGS::CARS4MARS_ROVER",
            lane="CARS4MARS_ROVER",
            evidence=evidence,
            observation=obs,
            ecosystem_states=ecosystem
        )

        self.assertEqual(receipt.state, ProofState.FOC_DIVERGENT)
        self.assertIn(FocGroup.FRAMEWORK_OF_CONCEPT, receipt.foc_groups)
        self.assertIsNotNone(receipt.divergence.delta_authority)

    def test_stage_5_dependency_nesting_law(self):
        """Rule 10: Child claims cannot inherit more certainty than parent evidence supports."""
        poc = PocVsFocVnextEngine()
        
        # Unvalidated parent
        parent_evidence = []
        parent_receipt = poc.evaluate(
            concept_id="parent-unverified",
            claim="Parent thesis is unverified",
            scope="KPGS::DIRISA_RESEARCH",
            lane="DIRISA_RESEARCH",
            evidence=parent_evidence,
            observation=ObservationalMembrane(),
            ecosystem_states={"E_P": "UNKNOWN", "E_W": "UNKNOWN", "E_R": "UNKNOWN"}
        )
        self.assertEqual(parent_receipt.state, ProofState.UNKNOWN)

        # Child claim based on unvalidated parent must fall back to UNKNOWN / Fabrication
        child_receipt = poc.evaluate(
            concept_id="child-dependent",
            claim="Child architecture derived from unverified parent",
            scope="KPGS::DIRISA_RESEARCH",
            lane="DIRISA_RESEARCH",
            evidence=[EvidenceItem(source_class=SourceClass.PHYSICAL_METAL, authority_for=["test"], reference="ref", verified=True)],
            observation=ObservationalMembrane(),
            ecosystem_states={"E_P": "KNOWN", "E_W": "KNOWN", "E_R": "KNOWN"},
            parent_receipt=parent_receipt
        )
        self.assertEqual(child_receipt.state, ProofState.UNKNOWN)
        self.assertIn(FocGroup.FABRICATION_OF_CONCEPT, child_receipt.foc_groups)
        self.assertEqual(child_receipt.dirisa_root, DirisaTier.FABRICATION)

    def test_full_pipeline_orchestration(self):
        """End-to-end execution: CRUD -> SWFUS -> BP -> BMP -> POCvsFOC."""
        evidence = [
            EvidenceItem(
                source_class=SourceClass.INSTITUTIONAL,
                authority_for=["dirisa_talk_26"],
                reference="Schematics/.../DIRISA/contribution.pdf",
                verified=True
            ),
            EvidenceItem(
                source_class=SourceClass.FOUNDER_DIRECTIVE,
                authority_for=["master_robyn_intent"],
                reference="Robyn Rababalela DIRISA Workshop 2026",
                verified=True
            )
        ]
        obs = ObservationalMembrane(
            D_t=[{"topic": "african_data_sovereignty", "weight": 1.0}],
            F_t=[{"session": "Annual DIRISA National Workshop 2026"}],
            G_t=[{"tier": "Humblebee O(N) linear paradigm"}],
            R_t=[{"membrane": "Local AI Membrane CASSY"}]
        )
        ecosystem = {"E_P": "KNOWN", "E_W": "KNOWN", "E_R": "KNOWN"}

        result = self.orchestrator.run_full_pipeline(
            concept_id="dirisa-talk-26",
            claim="POC vs FOC in Data Governance: Finding Patterns within Chaos to Reclaim African Digital Sovereignty",
            lane="DIRISA_RESEARCH",
            crud_payload={"title": "DIRISA Talk 26", "author": "Kholofelo Robyn Rababalela"},
            is_mutating=True,
            bmp_dt_ms=12.5,
            evidence=evidence,
            observation=obs,
            ecosystem_states=ecosystem
        )

        self.assertEqual(result["final_verdict"], "POC_VALIDATED")
        self.assertEqual(result["stages"]["3_BP"]["status"], "BRACKETED")
        self.assertTrue(result["stages"]["4_BMP"]["passed"])
        self.assertEqual(result["stages"]["5_POCvsFOC_vNext"]["state"], "POC_VALIDATED")
        self.assertEqual(result["post_governance_crud"]["status"], "EXECUTED")


if __name__ == "__main__":
    unittest.main()
