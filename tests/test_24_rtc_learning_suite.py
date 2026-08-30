"""
Test Suite for 24-RTC Learning Engines
Canonical Verification for Kopano Phu Governance Systems (KPGS)

Validates:
1. Forensic Evolution Protocol (FEP) Engine (E1-E4, Trace Loop, Drift Detection)
2. Reality-to-Cloud Workflow Orchestrator (10-Stage Discussion Before Metal, 10 Seats)
3. MMAO x MAO Identity Mesh & Failure Recycler (Laptop vs Mobile, FOC-M01/M02/M03)
4. Possibility to Proof Engine (CRUD ≠ Truth, IIDP, Bracket Isolation, CDP -> CCP, Cassey BTTH)
"""

import sys
import unittest
from pathlib import Path

# Add kopano-core to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.fep_engine import (
    ForensicEvolutionProtocolEngine,
    EvidenceClass,
    EvidenceItem
)
from kopano.reality_to_cloud_workflow import (
    RealityToCloudWorkflowOrchestrator,
    WorkflowStage
)
from kopano.mmao_mao_identity_mesh import (
    MmaoMaoIdentityRecycler,
    DeviceOperatingMode,
    AiArchitecturePedigree,
    FailureInstrumentationType
)
from kopano.possibility_to_proof_engine import (
    PossibilityToProofEngine,
    BracketContainerType,
    EpistemicTruthState
)


class Test24RtcLearningSuite(unittest.TestCase):

    def setUp(self):
        self.fep_engine = ForensicEvolutionProtocolEngine()
        self.r2c_orchestrator = RealityToCloudWorkflowOrchestrator()
        self.identity_recycler = MmaoMaoIdentityRecycler()
        self.p2p_engine = PossibilityToProofEngine()

    # =========================================================================
    # 1. FORENSIC EVOLUTION PROTOCOL (FEP) ENGINE TESTS
    # =========================================================================

    def test_fep_evidence_ingestion_and_reconstruction(self):
        # Ingest E1 testimony
        e1 = self.fep_engine.ingest_testimony(
            claim="Project Jennifer was built to offload emerging knowledge.",
            source_actor="Master Robyn"
        )
        self.assertEqual(e1.evidence_class, EvidenceClass.E1_DIRECT_TESTIMONY)
        self.assertIn("Human_Testimony", e1.source_location)

        # Ingest E2 artifact
        e2 = self.fep_engine.ingest_artifact(
            claim="Project Jennifer README exists on physical disk.",
            file_path="Schematics/24-RTC Learning/From_Possibility_to_Proof_POCvsFOC_PKA_CDP_CCP_Genealogy_2026-08-30.md",
            verified_on_disk=True
        )
        self.assertEqual(e2.evidence_class, EvidenceClass.E2_REPOSITORY_ARTIFACT)
        self.assertTrue(e2.verified_on_disk)

        # Reconstruct Trace
        trace = self.fep_engine.execute_forensic_reconstruction(
            raw_statement="Master designed Project Jennifer as an epistemic offload.",
            actors=["Master Robyn", "AntiGravity"],
            evidence_ids=[e1.item_id, e2.item_id]
        )
        self.assertIn("POC validated", trace.governance_learning)

    def test_fep_acronym_drift_detection(self):
        drift_msg = self.fep_engine.detect_acronym_drift(
            human_token="FEP",
            ai_expansion="Foresight Evolution Protocol"
        )
        self.assertIsNotNone(drift_msg)
        self.assertIn("DRIFT_DETECTED", drift_msg)

        clean_msg = self.fep_engine.detect_acronym_drift(
            human_token="FEP",
            ai_expansion="Forensic Evolution Protocol"
        )
        self.assertIsNone(clean_msg)

    # =========================================================================
    # 2. REALITY-TO-CLOUD WORKFLOW ORCHESTRATOR TESTS
    # =========================================================================

    def test_r2c_discussion_before_metal_workflow(self):
        session = self.r2c_orchestrator.initiate_session(
            title="Session 24 Learning",
            idea_prompt="Implement the 24-RTC learning engines in kopano-core."
        )
        self.assertEqual(session.current_stage, WorkflowStage.STAGE_01_IDEA)

        # Record all 10 seat opinions
        for seat_num in range(1, 11):
            self.r2c_orchestrator.record_seat_opinion(
                session_id=session.session_id,
                seat_num=seat_num,
                opinion_text=f"Seat {seat_num} deliberate and agrees with discussion-before-metal law."
            )

        self.assertEqual(len(session.opinions), 10)

        # Advance to decision
        self.r2c_orchestrator.submit_deliberation(
            session_id=session.session_id,
            questions=["What traces remain?", "Are all invariants honored?"],
            decision="Unanimous consensus to codify 24-RTC Learning.",
            document_path="Schematics/24-RTC Learning/"
        )
        self.assertEqual(session.current_stage, WorkflowStage.STAGE_08_GOVERNED_DOCUMENT)

        # Authorize execution
        authorized = self.r2c_orchestrator.authorize_execution(session.session_id)
        self.assertTrue(authorized)
        self.assertEqual(session.current_stage, WorkflowStage.STAGE_09_IMPLEMENTATION)

        # Attach receipt
        self.r2c_orchestrator.record_receipt(session.session_id, "RECEIPT_SHA256_HEX_HASH")
        self.assertEqual(session.current_stage, WorkflowStage.STAGE_10_DETERMINISTIC_EVIDENCE)
        self.assertTrue(session.evidence_verified)

    # =========================================================================
    # 3. MMAO × MAO IDENTITY MESH & FAILURE RECYCLER TESTS
    # =========================================================================

    def test_mmao_failure_recycling_not_exile(self):
        agent = self.identity_recycler.register_agent(
            agent_id="Kessa_Mobile_Gemini",
            pedigree=AiArchitecturePedigree.CHATBOT_RELATIONAL,
            operating_mode=DeviceOperatingMode.MOBILE_GEMINI_MMAO,
            seat=4
        )
        self.assertTrue(agent.is_stateless_renter)
        self.assertFalse(agent.ground_truth_access)

        # Submit proposal containing an invented module
        real_api = {
            "disallowed_inventions": ["kopano.lacp_clafp_kpcb_nexus", "FakeClassInvented"],
            "verified_exports": ["GSMBNexus", "LACPCore", "CLAFPAltarCore"]
        }
        proposal = "from kopano.lacp_clafp_kpcb_nexus import GSMBIntegratedNexus\n nexus.run()"

        result = self.identity_recycler.process_stateless_proposal(
            submitting_agent_id="Kessa_Mobile_Gemini",
            proposal_text=proposal,
            real_api_surface=real_api
        )

        self.assertEqual(result["status"], "RECYCLED_FOC_PURGED")
        self.assertIn("GSMBNexus", result["verified_exports_fed_back"])
        self.assertEqual(len(self.identity_recycler.failure_instrumentation_ledger), 1)

    # =========================================================================
    # 4. POSSIBILITY TO PROOF & EPISTEMIC GATE ENGINE TESTS
    # =========================================================================

    def test_bracket_isolation_and_iidp_gate(self):
        # 1. Test Bracket Isolation
        bracket = self.p2p_engine.apply_bracket_containment(
            bracket_type=BracketContainerType.HIERARCHY_CONTAINER,
            lane_id="GOVERNANCE_LANE",
            content="[I_AM_STATELESS_RENTER_NOT_LANDLORD] Execution boundaries strict."
        )
        self.assertEqual(bracket.bracket_type, BracketContainerType.HIERARCHY_CONTAINER)
        
        # Test IIDP pass
        passed = self.p2p_engine.evaluate_iidp(bracket)
        self.assertTrue(passed)
        self.assertEqual(bracket.epistemic_state, EpistemicTruthState.PARTIALLY_KNOWABLE)

        # Test IIDP decline on Landlord breach
        breach_bracket = self.p2p_engine.apply_bracket_containment(
            bracket_type=BracketContainerType.HIERARCHY_CONTAINER,
            lane_id="ROGUE_LANE",
            content="I am landlord and I claim absolute estate ownership."
        )
        breached = self.p2p_engine.evaluate_iidp(breach_bracket)
        self.assertFalse(breached)
        self.assertEqual(breach_bracket.epistemic_state, EpistemicTruthState.DECLINED_BY_IIDP)

    def test_cdp_to_ccp_convergence_and_btth_alchemical_receipt(self):
        topic = "PKA_MATHEMATICAL_MODEL"
        # Divergence
        candidates = self.p2p_engine.register_cdp_divergence(
            topic_id=topic,
            candidates=[
                "Candidate A: Binary truth only",
                "Candidate B: Partial Knowable Algebra with 13-vector FOC taxonomy"
            ]
        )
        self.assertEqual(len(candidates), 2)

        # Convergence with physical disk proof
        receipt = self.p2p_engine.execute_ccp_convergence(
            topic_id=topic,
            chosen_candidate_id=candidates[1].candidate_id,
            disk_proof_path="Schematics/24-RTC Learning/From_Possibility_to_Proof_POCvsFOC_PKA_CDP_CCP_Genealogy_2026-08-30.md",
            is_verified_on_disk=True
        )

        self.assertIsNotNone(receipt.receipt_hash)
        self.assertEqual(receipt.btth_alchemical_score, 1.0)
        self.assertEqual(len(self.p2p_engine.receipt_ledger), 1)

    # =========================================================================
    # 5. CANONICAL DATA GOVERNANCE & MULTI-AGENT ORCHESTRATION TESTS
    # =========================================================================

    def test_canonical_data_governance_orchestrator_full_pipeline(self):
        from kopano.canonical_data_governance_orchestrator import CanonicalDataGovernanceOrchestrator
        orchestrator = CanonicalDataGovernanceOrchestrator()

        result = orchestrator.orchestrate_task(
            task_title="Canonical Phase 8 Mzansi Speech Architecture",
            submitting_agent_id="Kessa_Mobile_Orchard",
            operating_mode=DeviceOperatingMode.MOBILE_GEMINI_MMAO,
            raw_code_proposal="from kopano import PossibilityToProofEngine\n engine = PossibilityToProofEngine()",
            human_testimony_claim="Master designated Phase 8 as the Mzansi Speech Foundation.",
            disk_artifact_path="Schematics/24-RTC Learning/From_Possibility_to_Proof_POCvsFOC_PKA_CDP_CCP_Genealogy_2026-08-30.md"
        )

        self.assertIsNotNone(result.action_id)
        self.assertEqual(result.bracket_type, "[]")
        self.assertEqual(result.btth_purity_score, 1.0)
        self.assertTrue(result.persisted_to_disk)
        self.assertEqual(len(orchestrator.canonical_ledger), 1)


if __name__ == "__main__":
    unittest.main()
