from kopano.agent_failure_training import (
    FailureClass,
    KCDecision,
    ReplayStatus,
    build_failure_receipt,
    decide_promotion,
)


def _receipt():
    return build_failure_receipt(
        receipt_id="INC-TEST-001",
        agent_id="cassy",
        model_provider="test",
        model_name="test-model",
        model_version="1",
        prompt_context="sensitive prompt context",
        system_controls_expected=["ground-truth verification"],
        actual_output="claimed a test passed without running it",
        violated_governance_rules=["no fabricated execution evidence"],
        failure_classes=[FailureClass.FOC_M03_VALIDATION_THEATER],
        downstream_effects=["false confidence"],
        evidence_refs=["tests/test_agent_failure_training.py"],
        correction_candidate="run the real test before claiming PASS",
    )


def test_receipt_hashes_prompt_context_and_does_not_store_raw_prompt():
    receipt = _receipt()
    payload = receipt.to_dict()

    assert payload["schema"] == "kpgs_agent_failure_receipt_v1"
    assert payload["prompt_context_sha256"] != "sensitive prompt context"
    assert "sensitive prompt context" not in receipt.to_json()
    assert payload["failure_classes"] == ("FOC-M03",)


def test_unknown_failure_class_is_rejected():
    try:
        build_failure_receipt(
            receipt_id="INC-TEST-002",
            agent_id="cassy",
            model_provider="test",
            model_name="test-model",
            prompt_context="x",
            system_controls_expected=["control"],
            actual_output="output",
            violated_governance_rules=["rule"],
            failure_classes=["FOC-X99"],
        )
    except ValueError as exc:
        assert "Unknown failure class" in str(exc)
    else:
        raise AssertionError("unknown failure class should fail")


def test_promotion_requires_all_independent_gates():
    receipt = _receipt()
    decision = decide_promotion(
        receipt=receipt,
        student_agent_id="cassy",
        teacher_agent_id="cassey",
        kc_agent_id="kc",
        teacher_reviewed=True,
        blackmask_passed=True,
        replay_status=ReplayStatus.PASS,
        kc_decision=KCDecision.SAVE,
    )

    assert decision.promoted is True
    assert decision.reason == "all promotion gates passed"


def test_failed_replay_blocks_promotion():
    receipt = _receipt()
    decision = decide_promotion(
        receipt=receipt,
        student_agent_id="cassy",
        teacher_agent_id="cassey",
        kc_agent_id="kc",
        teacher_reviewed=True,
        blackmask_passed=True,
        replay_status=ReplayStatus.FAIL,
        kc_decision=KCDecision.SAVE,
    )

    assert decision.promoted is False
    assert "replay_passed" in decision.reason


def test_student_cannot_be_teacher_or_ledger():
    receipt = _receipt()

    try:
        decide_promotion(
            receipt=receipt,
            student_agent_id="cassy",
            teacher_agent_id="cassy",
            kc_agent_id="kc",
            teacher_reviewed=True,
            blackmask_passed=True,
            replay_status=ReplayStatus.PASS,
            kc_decision=KCDecision.SAVE,
        )
    except ValueError as exc:
        assert "must be distinct" in str(exc)
    else:
        raise AssertionError("self-promotion identity overlap should fail")
