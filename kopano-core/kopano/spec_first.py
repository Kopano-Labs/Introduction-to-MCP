"""Executable KPGS specification-first build supervision for issue #39."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

LIFECYCLE_STATES = {"draft", "verified", "approved", "released", "rejected", "rolled-back"}
ACTOR_KINDS = {"human", "agent"}
HIGH_RISK = {"R2", "R3"}


class BuildGovernanceError(ValueError):
    """Raised when a build operation violates its governing specification."""


@dataclass(frozen=True)
class VerificationResult:
    criterion_id: str
    passed: bool
    implementation_revision: str
    evidence_ref: str
    verifier: str


@dataclass(frozen=True)
class DelegationReceipt:
    spec_id: str
    actor_kind: str
    implementation_revision: str
    requested_scope: tuple[str, ...]
    requested_capabilities: tuple[str, ...]
    gate_id: str | None


class SpecificationFirstBuild:
    """Govern iterative implementation revisions through specify/delegate/verify/ship."""

    def __init__(self, spec: Mapping[str, Any]) -> None:
        self.spec = dict(spec)
        self._validate_spec()
        self.state = str(self.spec["lifecycle_state"])
        self._delegated_revision: str | None = None
        self._verification: dict[str, VerificationResult] = {}

    @property
    def criteria(self) -> dict[str, Mapping[str, Any]]:
        return {str(item["id"]): item for item in self.spec["acceptance_criteria"]}

    @property
    def declared_gates(self) -> set[str]:
        return {str(gate) for gate in self.spec.get("action_gates", [])}

    def delegate(
        self,
        *,
        actor_kind: str,
        implementation_revision: str,
        requested_scope: Iterable[str],
        requested_capabilities: Iterable[str],
        destructive: bool = False,
        gate_id: str | None = None,
    ) -> DelegationReceipt:
        if actor_kind not in ACTOR_KINDS:
            raise BuildGovernanceError(f"unsupported actor_kind: {actor_kind}")
        if not implementation_revision.strip():
            raise BuildGovernanceError("implementation_revision is required before delegation")

        scope = tuple(requested_scope)
        included = set(self.spec["scope"]["included"])
        excluded = set(self.spec["scope"]["excluded"])
        if not scope or any(item not in included or item in excluded for item in scope):
            raise BuildGovernanceError("delegation cannot broaden scope beyond the governing specification")

        allowed_capabilities = {
            str(item["capability"])
            for item in self.spec.get("required_capabilities", [])
        }
        requested = tuple(requested_capabilities)
        if not set(requested) <= allowed_capabilities:
            raise BuildGovernanceError("delegation requested capability outside the governing specification")

        gate_required = destructive or self.spec["risk_class"] in HIGH_RISK
        if gate_required and (not gate_id or gate_id not in self.declared_gates):
            raise BuildGovernanceError("high-risk/destructive delegation requires a declared action gate")

        # Every delegation is a new implementation attempt. Previous verification or
        # approval can never survive a revision/lease change and authorize the new attempt.
        self._delegated_revision = implementation_revision
        self._verification = {}
        self.state = "draft"

        return DelegationReceipt(
            spec_id=str(self.spec["spec_id"]),
            actor_kind=actor_kind,
            implementation_revision=implementation_revision,
            requested_scope=scope,
            requested_capabilities=requested,
            gate_id=gate_id,
        )

    def verify(self, results: Iterable[VerificationResult]) -> str:
        if self._delegated_revision is None:
            raise BuildGovernanceError("verification requires a delegated implementation revision")

        received: dict[str, VerificationResult] = {}
        for result in results:
            if result.criterion_id not in self.criteria:
                raise BuildGovernanceError(f"unknown acceptance criterion: {result.criterion_id}")
            if result.criterion_id in received:
                raise BuildGovernanceError(f"duplicate acceptance criterion result: {result.criterion_id}")
            if result.implementation_revision != self._delegated_revision:
                raise BuildGovernanceError("verification evidence must target the exact implementation revision")
            if not result.evidence_ref.strip() or not result.verifier.strip():
                raise BuildGovernanceError("verification requires evidence_ref and independent verifier identity")
            received[result.criterion_id] = result

        missing = set(self.criteria) - set(received)
        if missing:
            raise BuildGovernanceError(f"verification is missing acceptance criteria: {sorted(missing)}")

        self._verification = received
        hard_failure = any(
            bool(self.criteria[criterion_id]["hard_gate"]) and not result.passed
            for criterion_id, result in received.items()
        )
        self.state = "rejected" if hard_failure else "verified"
        return self.state

    def approve(self) -> str:
        if self.state != "verified":
            raise BuildGovernanceError("only a verified implementation may be approved")
        self._assert_current_verification_complete(require_all_pass=False)
        self.state = "approved"
        return self.state

    def release(self) -> str:
        if self.state not in {"verified", "approved"}:
            raise BuildGovernanceError("release requires verified or approved state")
        self._assert_current_verification_complete(require_all_pass=True)
        self.state = "released"
        return self.state

    def rollback(self) -> str:
        if self._delegated_revision is None:
            raise BuildGovernanceError("rollback requires a delegated implementation revision")
        if not self.spec.get("rollback_plan", {}).get("procedure"):
            raise BuildGovernanceError("rollback requires the declared rollback procedure")
        self.state = "rolled-back"
        return self.state

    def _assert_current_verification_complete(self, *, require_all_pass: bool) -> None:
        if self._delegated_revision is None:
            raise BuildGovernanceError("lifecycle advancement requires a delegated implementation revision")

        missing = set(self.criteria) - set(self._verification)
        if missing:
            raise BuildGovernanceError(f"lifecycle advancement is missing acceptance criteria: {sorted(missing)}")

        stale = [
            criterion_id
            for criterion_id, result in self._verification.items()
            if result.implementation_revision != self._delegated_revision
        ]
        if stale:
            raise BuildGovernanceError(
                f"lifecycle advancement has stale verification for current implementation revision: {sorted(stale)}"
            )

        if require_all_pass and any(not result.passed for result in self._verification.values()):
            raise BuildGovernanceError("failed acceptance criteria prevent released state")

    def _validate_spec(self) -> None:
        required = {
            "spec_id",
            "title",
            "outcome",
            "scope",
            "interfaces",
            "constraints",
            "acceptance_criteria",
            "verification_plan",
            "rollback_plan",
            "risk_class",
            "required_capabilities",
            "lifecycle_state",
        }
        missing = required - self.spec.keys()
        if missing:
            raise BuildGovernanceError(f"governed build cannot begin without specification fields: {sorted(missing)}")
        if not self.spec["acceptance_criteria"]:
            raise BuildGovernanceError("governed build cannot begin without acceptance criteria")
        ids = [str(item["id"]) for item in self.spec["acceptance_criteria"]]
        if len(ids) != len(set(ids)):
            raise BuildGovernanceError("acceptance criterion identifiers must be unique")
        plan_ids = {str(item["criterion_id"]) for item in self.spec["verification_plan"]}
        if not set(ids) <= plan_ids:
            raise BuildGovernanceError("verification plan must cover every acceptance criterion")
        if self.spec["lifecycle_state"] not in LIFECYCLE_STATES:
            raise BuildGovernanceError("invalid lifecycle_state")
        if self.spec["risk_class"] in HIGH_RISK and not self.declared_gates:
            raise BuildGovernanceError("R2/R3 specifications must declare at least one action gate")
