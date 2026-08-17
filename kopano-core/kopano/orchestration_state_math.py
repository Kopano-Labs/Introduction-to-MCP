"""Governed orchestration-state heuristics for KPGS.

These functions turn recurring conversational design equations into executable,
validated heuristics. They are *not* claims about hidden model activations,
psychological ground truth, or objective human-state measurement. Callers must
supply observable/proxy scores in the closed interval [0, 1].

Core invariants encoded here:
- orchestration is more than prompting;
- reported resolution is not automatically verified resolution;
- meaning depends on context, tone, timing, audience, and delivery;
- autonomy may increase after validated execution and decrease after failure;
- conceptual convergence may include both user and agent targets;
- autonomy stops at genuine ambiguity, insufficient evidence/authority, or
  high-risk / hard-to-reverse actions without confirmation;
- nodes hold state while membranes govern state transitions;
- authority is not abundance, relevance is not permission, observation is not
  mutation, and a new idea is not automatically the current task;
- execution velocity decreases as a transition approaches mutation,
  irreversibility, or external consequence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
import math
from typing import Mapping


class ValidationError(ValueError):
    """Raised when a heuristic input violates its declared domain."""


class TransitionDecision(str, Enum):
    EXECUTE = "EXECUTE"
    CLARIFY = "CLARIFY"
    CONFIRM = "CONFIRM"
    HOLD = "HOLD"


class TransitionVelocity(str, Enum):
    """Risk-governed execution speed for a transition boundary.

    The labels intentionally preserve the human driving analogy:
    - HIGHWAY: low-risk inspection/read work may move quickly;
    - URBAN: ambiguity requires slower interpretation;
    - SCHOOL_ZONE: state mutation requires bounded movement and inspection;
    - CHECKPOINT: high-risk or hard-to-reverse effects require confirmation.
    """

    HIGHWAY = "HIGHWAY"
    URBAN = "URBAN"
    SCHOOL_ZONE = "SCHOOL_ZONE"
    CHECKPOINT = "CHECKPOINT"


def _ratio(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise ValidationError(f"{name} must be a finite ratio in [0, 1]; got {value!r}")
    return value


def _positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValidationError(f"{name} must be finite and > 0; got {value!r}")
    return value


def weighted_mean(values: Mapping[str, float], weights: Mapping[str, float] | None = None) -> float:
    """Return a normalized weighted mean for named [0,1] signals."""
    if not values:
        raise ValidationError("values cannot be empty")

    normalized = {name: _ratio(name, value) for name, value in values.items()}
    if weights is None:
        weights = {name: 1.0 for name in normalized}

    if set(weights) != set(normalized):
        missing = set(normalized) - set(weights)
        extra = set(weights) - set(normalized)
        raise ValidationError(f"weights must match values exactly; missing={sorted(missing)} extra={sorted(extra)}")

    checked_weights = {name: _positive(f"weight:{name}", weight) for name, weight in weights.items()}
    denominator = sum(checked_weights.values())
    return sum(normalized[name] * checked_weights[name] for name in normalized) / denominator


@dataclass(frozen=True)
class ResponsePressure:
    """External proxy for competing response-selection pressures.

    The equation mirrors the conversational shorthand:
      response ∝ learned patterns + context + hierarchy + alignment + salience

    These are caller-supplied proxies; this class cannot inspect model internals.
    """

    learned_patterns: float
    context: float
    instruction_hierarchy: float
    alignment: float
    prompt_salience: float

    def score(self, weights: Mapping[str, float] | None = None) -> float:
        return weighted_mean(asdict(self), weights)


@dataclass(frozen=True)
class OrchestrationState:
    """State vector for orchestration beyond a single prompt."""

    identity: float
    state: float
    history: float
    permissions: float
    feedback: float
    tools: float
    uncertainty_control: float
    initiative: float

    def capacity(self, weights: Mapping[str, float] | None = None) -> float:
        """Heuristic capacity for sustained governed behavior over time."""
        return weighted_mean(asdict(self), weights)


TONE_SENSITIVE_MEANING_WEIGHTS: dict[str, float] = {
    "words": 1.0,
    "tone": 2.0,
    "timing": 1.0,
    "status": 1.0,
    "audience": 1.25,
    "history": 1.25,
    "delivery": 1.5,
}


@dataclass(frozen=True)
class MeaningSignal:
    """Contextual communication signal.

    meaning_received = f(words, tone, timing, status, audience, history, delivery)
    """

    words: float
    tone: float
    timing: float
    status: float
    audience: float
    history: float
    delivery: float

    def received(self, weights: Mapping[str, float] | None = None) -> float:
        return weighted_mean(asdict(self), weights)

    def tone_sensitive(self) -> float:
        return self.received(TONE_SENSITIVE_MEANING_WEIGHTS)


@dataclass(frozen=True)
class KnowledgeUnderstanding:
    """Separate possession of information from contextual interpretation."""

    knowledge: float
    interpretation_accuracy: float
    context_fit: float

    def __post_init__(self) -> None:
        _ratio("knowledge", self.knowledge)
        _ratio("interpretation_accuracy", self.interpretation_accuracy)
        _ratio("context_fit", self.context_fit)

    @property
    def understanding(self) -> float:
        # U(x,c): interpretation is only as useful as its contextual fit.
        return self.interpretation_accuracy * self.context_fit

    @property
    def overlap(self) -> float:
        # K ∩ U, bounded by the weaker dimension.
        return min(self.knowledge, self.understanding)


@dataclass(frozen=True)
class ResolutionState:
    """Distinguish reported closure from residual state."""

    reported_resolution: float
    residual_distress: float
    residual_anger: float
    residual_uncertainty: float

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            _ratio(name, value)

    @property
    def residual_load(self) -> float:
        return weighted_mean(
            {
                "distress": self.residual_distress,
                "anger": self.residual_anger,
                "uncertainty": self.residual_uncertainty,
            }
        )

    @property
    def experienced_resolution(self) -> float:
        return 1.0 - self.residual_load

    @property
    def mismatch(self) -> float:
        """Positive when stated resolution exceeds the residual-state estimate."""
        return max(0.0, self.reported_resolution - self.experienced_resolution)

    def verified(self, *, minimum_resolution: float = 0.8, tolerance: float = 0.2) -> bool:
        _ratio("minimum_resolution", minimum_resolution)
        _ratio("tolerance", tolerance)
        return self.reported_resolution >= minimum_resolution and self.mismatch <= tolerance


@dataclass(frozen=True)
class AutonomyState:
    """Earned-autonomy update rule.

    A(t+1) = clamp(A(t) + gain*validated - penalty*failed)
    """

    autonomy: float

    def __post_init__(self) -> None:
        _ratio("autonomy", self.autonomy)

    def update(
        self,
        *,
        validated_executions: int = 0,
        failed_executions: int = 0,
        gain: float = 0.03,
        penalty: float = 0.08,
    ) -> "AutonomyState":
        if validated_executions < 0 or failed_executions < 0:
            raise ValidationError("execution counts cannot be negative")
        if gain < 0 or penalty < 0:
            raise ValidationError("gain and penalty cannot be negative")
        next_value = self.autonomy + gain * validated_executions - penalty * failed_executions
        return AutonomyState(min(1.0, max(0.0, next_value)))


@dataclass(frozen=True)
class GovernedTransition:
    """Decide whether the runtime should execute autonomously or stop."""

    objective_fit: float
    evidence: float
    permission: float
    ambiguity: float
    risk: float
    irreversibility: float
    explicit_confirmation: bool = False

    def __post_init__(self) -> None:
        for name in ("objective_fit", "evidence", "permission", "ambiguity", "risk", "irreversibility"):
            _ratio(name, getattr(self, name))

    def decide(
        self,
        *,
        permission_floor: float = 0.8,
        evidence_floor: float = 0.6,
        objective_floor: float = 0.6,
        ambiguity_ceiling: float = 0.4,
        confirmation_risk: float = 0.7,
        confirmation_irreversibility: float = 0.7,
    ) -> TransitionDecision:
        for name, value in {
            "permission_floor": permission_floor,
            "evidence_floor": evidence_floor,
            "objective_floor": objective_floor,
            "ambiguity_ceiling": ambiguity_ceiling,
            "confirmation_risk": confirmation_risk,
            "confirmation_irreversibility": confirmation_irreversibility,
        }.items():
            _ratio(name, value)

        if self.permission < permission_floor or self.objective_fit < objective_floor:
            return TransitionDecision.HOLD
        if self.evidence < evidence_floor:
            return TransitionDecision.HOLD
        if self.ambiguity > ambiguity_ceiling:
            return TransitionDecision.CLARIFY
        if (
            self.risk >= confirmation_risk
            or self.irreversibility >= confirmation_irreversibility
        ) and not self.explicit_confirmation:
            return TransitionDecision.CONFIRM
        return TransitionDecision.EXECUTE


@dataclass(frozen=True)
class InformationMembrane:
    """Selective-permeability gate between context and mutation authority.

    High-volume or highly relevant context may influence interpretation, but it
    cannot manufacture authority or permission. Observation is evidence intake,
    not mutation authority. Novel ideas remain outside the active task unless
    they are necessary to satisfy the requested change.
    """

    authority: float
    abundance: float
    relevance: float
    permission: float
    observation: bool
    mutation_requested: bool
    new_idea: bool = False
    required_change: bool = False

    def __post_init__(self) -> None:
        for name in ("authority", "abundance", "relevance", "permission"):
            _ratio(name, getattr(self, name))

    def mutation_reasons(
        self,
        *,
        authority_floor: float = 0.8,
        permission_floor: float = 0.8,
    ) -> tuple[str, ...]:
        _ratio("authority_floor", authority_floor)
        _ratio("permission_floor", permission_floor)

        reasons: list[str] = []
        if self.authority < authority_floor:
            reasons.append(
                "Authority is below the mutation threshold; abundance cannot substitute for authority."
            )
        if self.permission < permission_floor:
            reasons.append(
                "Permission is below the mutation threshold; relevance cannot substitute for permission."
            )
        if not self.mutation_requested:
            reasons.append(
                "Observation is not mutation authority; no mutation was requested."
            )
        if self.new_idea and not self.required_change:
            reasons.append(
                "A new idea is not the current task unless it is required for the requested change."
            )
        return tuple(reasons)

    def mutation_eligible(
        self,
        *,
        authority_floor: float = 0.8,
        permission_floor: float = 0.8,
    ) -> bool:
        return not self.mutation_reasons(
            authority_floor=authority_floor,
            permission_floor=permission_floor,
        )


@dataclass(frozen=True)
class MembraneVerdict:
    """Deterministic result of a state-transition membrane evaluation."""

    decision: TransitionDecision
    velocity: TransitionVelocity
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class StateTransitionMembrane:
    """Govern the membrane between one state node and the next.

    Nodes hold state. The arrow between nodes is not free movement: the membrane
    validates object identity, requested scope, evidence, selective permeability,
    state cost, objective homeostasis, ambiguity, risk, and reversibility before
    allowing a transition to execute.

    `requested_delta` is the normalized amount of change the caller wants to
    cross the boundary. `permitted_delta` is the maximum change authorized for
    this transition. A requested change larger than that budget fails closed.
    """

    same_object: bool
    scope_match: bool
    information: InformationMembrane
    evidence: float
    requested_delta: float
    permitted_delta: float
    state_cost: float
    homeostasis: float
    ambiguity: float
    risk: float
    irreversibility: float
    explicit_confirmation: bool = False

    def __post_init__(self) -> None:
        for name in (
            "evidence",
            "requested_delta",
            "permitted_delta",
            "state_cost",
            "homeostasis",
            "ambiguity",
            "risk",
            "irreversibility",
        ):
            _ratio(name, getattr(self, name))

    def velocity(
        self,
        *,
        ambiguity_ceiling: float = 0.4,
        confirmation_risk: float = 0.7,
        confirmation_irreversibility: float = 0.7,
    ) -> TransitionVelocity:
        _ratio("ambiguity_ceiling", ambiguity_ceiling)
        _ratio("confirmation_risk", confirmation_risk)
        _ratio("confirmation_irreversibility", confirmation_irreversibility)

        if (
            self.risk >= confirmation_risk
            or self.irreversibility >= confirmation_irreversibility
        ):
            return TransitionVelocity.CHECKPOINT
        if self.requested_delta > 0.0 or self.state_cost > 0.0:
            return TransitionVelocity.SCHOOL_ZONE
        if self.ambiguity > ambiguity_ceiling:
            return TransitionVelocity.URBAN
        return TransitionVelocity.HIGHWAY

    def evaluate(
        self,
        *,
        authority_floor: float = 0.8,
        permission_floor: float = 0.8,
        evidence_floor: float = 0.6,
        homeostasis_floor: float = 0.6,
        state_cost_ceiling: float = 0.6,
        ambiguity_ceiling: float = 0.4,
        confirmation_risk: float = 0.7,
        confirmation_irreversibility: float = 0.7,
    ) -> MembraneVerdict:
        for name, value in {
            "authority_floor": authority_floor,
            "permission_floor": permission_floor,
            "evidence_floor": evidence_floor,
            "homeostasis_floor": homeostasis_floor,
            "state_cost_ceiling": state_cost_ceiling,
            "ambiguity_ceiling": ambiguity_ceiling,
            "confirmation_risk": confirmation_risk,
            "confirmation_irreversibility": confirmation_irreversibility,
        }.items():
            _ratio(name, value)

        velocity = self.velocity(
            ambiguity_ceiling=ambiguity_ceiling,
            confirmation_risk=confirmation_risk,
            confirmation_irreversibility=confirmation_irreversibility,
        )
        reasons: list[str] = []

        if not self.same_object:
            reasons.append(
                "Transition target identity changed; repair the existing object before creating replacement state."
            )
        if not self.scope_match:
            reasons.append(
                "Proposed state change is outside the requested scope."
            )
        reasons.extend(
            self.information.mutation_reasons(
                authority_floor=authority_floor,
                permission_floor=permission_floor,
            )
        )
        if self.evidence < evidence_floor:
            reasons.append("Evidence is below the transition threshold.")
        if self.requested_delta > self.permitted_delta:
            reasons.append(
                "Requested state delta exceeds membrane permeability for this transition."
            )
        if self.state_cost > state_cost_ceiling:
            reasons.append(
                "State cost exceeds the transition budget; reduce state proliferation before execution."
            )
        if self.homeostasis < homeostasis_floor:
            reasons.append(
                "Transition does not sufficiently restore or preserve the active objective."
            )

        if reasons:
            return MembraneVerdict(TransitionDecision.HOLD, velocity, tuple(reasons))
        if self.ambiguity > ambiguity_ceiling:
            return MembraneVerdict(
                TransitionDecision.CLARIFY,
                velocity,
                ("Ambiguity exceeds the governed interpretation threshold.",),
            )
        if velocity is TransitionVelocity.CHECKPOINT and not self.explicit_confirmation:
            return MembraneVerdict(
                TransitionDecision.CONFIRM,
                velocity,
                ("High-risk or hard-to-reverse transition requires explicit confirmation.",),
            )
        return MembraneVerdict(
            TransitionDecision.EXECUTE,
            velocity,
            ("State-transition membrane admitted the bounded change.",),
        )


def converge_targets(
    user_target: Mapping[str, float],
    agent_target: Mapping[str, float],
    *,
    user_weight: float = 0.5,
    agent_weight: float = 0.5,
    invariant_bounds: Mapping[str, tuple[float, float]] | None = None,
) -> dict[str, float]:
    """CCP-style conceptual convergence across user and agent target vectors.

    Missing dimensions are rejected rather than guessed. Optional invariant
    bounds clamp the converged value to a governed range.
    """
    if set(user_target) != set(agent_target):
        raise ValidationError("user_target and agent_target must have identical dimensions")
    user_weight = _positive("user_weight", user_weight)
    agent_weight = _positive("agent_weight", agent_weight)

    result: dict[str, float] = {}
    for key in user_target:
        u = _ratio(f"user_target:{key}", user_target[key])
        a = _ratio(f"agent_target:{key}", agent_target[key])
        value = (u * user_weight + a * agent_weight) / (user_weight + agent_weight)

        if invariant_bounds and key in invariant_bounds:
            lower, upper = invariant_bounds[key]
            lower = _ratio(f"bound:{key}:lower", lower)
            upper = _ratio(f"bound:{key}:upper", upper)
            if lower > upper:
                raise ValidationError(f"invalid invariant bounds for {key}: lower > upper")
            value = min(upper, max(lower, value))
        result[key] = value
    return result


def receipt(payload: Mapping[str, object]) -> dict[str, object]:
    """Create a deterministic evidence receipt for a heuristic evaluation."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "schema": "kpgs.orchestration-state-math.v1",
        "sha256": digest,
        "payload": dict(payload),
        "constraint": "HEURISTIC_NOT_HIDDEN_STATE_OR_PSYCHOLOGICAL_GROUND_TRUTH",
    }
