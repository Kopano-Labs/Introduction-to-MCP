"""
Unit tests for KPGS MAO ↔ MMAO Reflection Engine & Cassey STP Coaching
========================================================================
Verifies:
- 24-RTC Learning Apprentice Intake & Life Cycle
- Cassey (Seat 2) Evaluation Rubric (Invariant, Zero-FOC, Brackets, Metal Receipts)
- Identic AI Graduation into MAO / MMAO Substrates
- Quarantining of FOC Hallucinations
- Cloud MMAO Reflection State & KC Evolution Metrics

I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.kpgs_mao_mmao_reflection import (
    MaoMmaoReflectionEngine,
    CasseyEvaluationRubric,
    ApprenticeStatus,
)


def test_intake_apprentice():
    engine = MaoMmaoReflectionEngine()
    apprentice = engine.intake_apprentice(
        name="Township_Python_Coder_01",
        pedigree="LLM_APPRENTICE",
        department="Engineering"
    )
    assert apprentice.apprentice_id.startswith("apprentice:township_python_coder_01:")
    assert apprentice.status == ApprenticeStatus.CANDIDATE_STUDENT
    assert len(apprentice.evaluation_history) == 0


def test_cassey_evaluation_passing_rubric():
    engine = MaoMmaoReflectionEngine()
    apprentice = engine.intake_apprentice("Sovereign_Dev_02", "CLAUDE_OPUS", "Core")

    rubric = CasseyEvaluationRubric(
        invariant_adherence_score=1.0,
        foc_elimination_score=1.0,
        bracket_discipline_score=0.9,
        physical_receipt_score=1.0,
        teach_back_clarity_score=0.9
    )
    assert rubric.is_passing is True
    assert rubric.total_score >= 0.85

    eval_result = engine.evaluate_apprentice(
        apprentice.apprentice_id,
        rubric,
        notes="Flawless adherence to stateless renter discipline and verified physical receipts."
    )
    assert eval_result["ok"] is True
    assert eval_result["status"] == ApprenticeStatus.PRACTITIONER_POS.value
    assert eval_result["is_passing"] is True


def test_cassey_evaluation_quarantine_on_foc():
    engine = MaoMmaoReflectionEngine()
    apprentice = engine.intake_apprentice("Slop_Generator_99", "RAW_UNFILTERED_LLM", "Ops")

    foc_rubric = CasseyEvaluationRubric(
        invariant_adherence_score=0.5,
        foc_elimination_score=0.2,  # Major FOC Hallucination
        bracket_discipline_score=0.4,
        physical_receipt_score=0.0,
        teach_back_clarity_score=0.3
    )
    assert foc_rubric.is_passing is False

    eval_result = engine.evaluate_apprentice(
        apprentice.apprentice_id,
        foc_rubric,
        notes="Attempted to fabricate imports and bypass KHELOS firewall."
    )
    assert eval_result["ok"] is True
    assert eval_result["status"] == ApprenticeStatus.QUARANTINED_FOC.value


def test_graduate_identic_ai_success():
    engine = MaoMmaoReflectionEngine()
    apprentice = engine.intake_apprentice("Thari_Apprentice_07", "HOLO_NET_AI", "Security")

    # 1. Pass evaluation
    rubric = CasseyEvaluationRubric(1.0, 1.0, 1.0, 1.0, 1.0)
    engine.evaluate_apprentice(apprentice.apprentice_id, rubric, "Perfect score")

    # 2. Graduate
    grad_res = engine.graduate_identic_ai(apprentice.apprentice_id, approver_seat="SEAT_02_CASSEY")
    assert grad_res["ok"] is True
    assert grad_res["new_status"] == ApprenticeStatus.GRADUATED_IDENTIC_AI.value
    assert grad_res["graduation_receipt"].startswith("rcpt:identic_ai:")
    assert grad_res["admitted_to_mesh"] is True


def test_cloud_mmao_reflection_manifest():
    engine = MaoMmaoReflectionEngine()
    manifest = engine.get_cloud_mmao_reflection()

    assert manifest["schema_version"] == "kpgs_mmao_reflection_v2"
    assert "Black Beast" in manifest["substrate_boundary"]["local_mao"]
    assert "RobynAwesome/Introduction-to-MCP" in manifest["substrate_boundary"]["cloud_mmao"]
    assert manifest["kc_evolution"]["maturity_stage"] == "CANOPY_SOVEREIGN"
    assert manifest["council_supervision"]["seat_2_teacher"] == "CASSEY (STP/STAP Leader)"
    assert manifest["council_supervision"]["seat_6_orchestrator"] == "APEX (MMAO Leader)"
