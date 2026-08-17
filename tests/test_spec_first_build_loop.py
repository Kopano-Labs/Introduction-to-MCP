from __future__ import annotations

from copy import deepcopy

import pytest

from kopano.spec_first import BuildGovernanceError, SpecificationFirstBuild, VerificationResult


def make_spec(*, risk_class: str = "R1", gates: list[str] | None = None) -> dict:
    spec = {
        "spec_id": "SPEC-39-POC",
        "title": "Specification-first executable governance",
        "outcome": "Prove bounded delegation, exact-revision verification and release gating.",
        "scope": {
            "included": ["runtime", "tests"],
            "excluded": ["production-deploy", "identity-mutation"],
        },
        "interfaces": [],
        "constraints": ["Do not widen scope"],
        "acceptance_criteria": [
            {
                "id": "AC-01",
                "statement": "Implementation remains inside declared scope.",
                "hard_gate": True,
                "verification_methods": ["unit"],
            },
            {
                "id": "AC-02",
                "statement": "Verification evidence is pinned to the implementation revision.",
                "hard_gate": True,
                "verification_methods": ["unit"],
            },
        ],
        "verification_plan": [
            {"criterion_id": "AC-01", "evidence": "scope test"},
            {"criterion_id": "AC-02", "evidence": "revision test"},
        ],
        "rollback_plan": {"trigger": "verification failure", "procedure": "revert implementation revision"},
        "risk_class": risk_class,
        "required_capabilities": [{"capability": "repository.write", "scope": "governed branch"}],
        "lifecycle_state": "draft",
    }
    if gates is not None:
        spec["action_gates"] = gates
    return spec


def passing_results(revision: str) -> list[VerificationResult]:
    return [
        VerificationResult("AC-01", True, revision, "evidence://scope", "independent-test"),
        VerificationResult("AC-02", True, revision, "evidence://revision", "independent-test"),
    ]


def test_governed_build_cannot_begin_without_spec_or_acceptance_criteria():
    missing = make_spec()
    del missing["scope"]
    with pytest.raises(BuildGovernanceError, match="cannot begin without specification fields"):
        SpecificationFirstBuild(missing)

    no_criteria = make_spec()
    no_criteria["acceptance_criteria"] = []
    with pytest.raises(BuildGovernanceError, match="without acceptance criteria"):
        SpecificationFirstBuild(no_criteria)


def test_delegation_cannot_silently_broaden_scope_or_capabilities():
    build = SpecificationFirstBuild(make_spec())
    with pytest.raises(BuildGovernanceError, match="cannot broaden scope"):
        build.delegate(
            actor_kind="agent",
            implementation_revision="abc123",
            requested_scope=["production-deploy"],
            requested_capabilities=["repository.write"],
        )

    with pytest.raises(BuildGovernanceError, match="capability outside"):
        build.delegate(
            actor_kind="agent",
            implementation_revision="abc123",
            requested_scope=["runtime"],
            requested_capabilities=["production.deploy"],
        )


@pytest.mark.parametrize("actor_kind", ["human", "agent"])
def test_same_governance_loop_supports_human_and_agent_authored_implementations(actor_kind: str):
    build = SpecificationFirstBuild(make_spec())
    receipt = build.delegate(
        actor_kind=actor_kind,
        implementation_revision=f"rev-{actor_kind}",
        requested_scope=["runtime", "tests"],
        requested_capabilities=["repository.write"],
    )
    assert receipt.actor_kind == actor_kind
    assert build.verify(passing_results(receipt.implementation_revision)) == "verified"
    assert build.release() == "released"


def test_high_risk_or_destructive_delegation_requires_declared_gate():
    with pytest.raises(BuildGovernanceError, match="must declare at least one action gate"):
        SpecificationFirstBuild(make_spec(risk_class="R3"))

    build = SpecificationFirstBuild(make_spec(risk_class="R3", gates=["human-production-approval"]))
    with pytest.raises(BuildGovernanceError, match="requires a declared action gate"):
        build.delegate(
            actor_kind="agent",
            implementation_revision="risk-rev",
            requested_scope=["runtime"],
            requested_capabilities=["repository.write"],
        )

    receipt = build.delegate(
        actor_kind="agent",
        implementation_revision="risk-rev",
        requested_scope=["runtime"],
        requested_capabilities=["repository.write"],
        destructive=True,
        gate_id="human-production-approval",
    )
    assert receipt.gate_id == "human-production-approval"


def test_verification_evidence_must_target_exact_implementation_revision():
    build = SpecificationFirstBuild(make_spec())
    build.delegate(
        actor_kind="agent",
        implementation_revision="exact-rev",
        requested_scope=["runtime"],
        requested_capabilities=["repository.write"],
    )
    results = passing_results("other-rev")
    with pytest.raises(BuildGovernanceError, match="exact implementation revision"):
        build.verify(results)


def test_failed_hard_criterion_prevents_released_state():
    build = SpecificationFirstBuild(make_spec())
    build.delegate(
        actor_kind="human",
        implementation_revision="failed-rev",
        requested_scope=["tests"],
        requested_capabilities=["repository.write"],
    )
    results = passing_results("failed-rev")
    results[0] = VerificationResult("AC-01", False, "failed-rev", "evidence://failure", "independent-test")

    assert build.verify(results) == "rejected"
    with pytest.raises(BuildGovernanceError, match="release requires"):
        build.release()


def test_rollback_uses_declared_recovery_plan():
    spec = deepcopy(make_spec())
    build = SpecificationFirstBuild(spec)
    assert build.rollback() == "rolled-back"
