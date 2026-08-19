"""KPGS canonical DNS estate migration readiness engine.

This module does not mutate the Sovereign Estate Registry and does not promote a
DNS property. It evaluates whether a bounded workflow has enough witnessed
state/evidence to ask the separately capability-gated registry runtime for the
next lifecycle transition.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

MIGRATION_STAGES = (
    "baseline",
    "register",
    "adapter_integration",
    "capability_map",
    "renter_integration",
    "realtime_wiring",
    "evaluation",
    "staging",
    "rollback_drill",
    "production_promotion",
    "observe",
)

ALLOWED_STAGE_STATUS = {"PASS", "HOLD", "NOT_REACHED"}


class MigrationError(ValueError):
    pass


@dataclass(frozen=True)
class StageResult:
    status: str
    detail: str
    evidence_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "detail": self.detail,
            "evidence_refs": list(self.evidence_refs),
        }


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _refs(*values: Any) -> tuple[str, ...]:
    return tuple(str(value) for value in values if isinstance(value, str) and value.strip())


def _stage(status: str, detail: str, *evidence_refs: str) -> StageResult:
    if status not in ALLOWED_STAGE_STATUS:
        raise MigrationError(f"unknown stage status: {status}")
    return StageResult(status, detail, _refs(*evidence_refs))


def _property_complete_for_registration(record: Mapping[str, Any]) -> bool:
    owner = record.get("owner")
    deployment = record.get("deployment") or {}
    governance = record.get("governance") or {}
    return all(
        (
            isinstance(record.get("ownership_evidence"), list)
            and bool(record.get("ownership_evidence")),
            isinstance(record.get("repositories"), list)
            and bool(record.get("repositories")),
            isinstance(owner, Mapping) and bool(owner.get("ref")),
            bool(deployment.get("provider")),
            bool(deployment.get("target")),
            bool(governance.get("policy_ref")),
            bool(governance.get("risk_class")),
            bool(governance.get("tier")),
            isinstance(record.get("capabilities"), list)
            and bool(record.get("capabilities")),
            isinstance(record.get("health_endpoints"), list)
            and bool(record.get("health_endpoints")),
        )
    )


def _baseline_evidence(record: Mapping[str, Any]) -> tuple[bool, list[str], list[str]]:
    deployment = record.get("deployment") or {}
    rollback = record.get("rollback") or {}
    required = {
        "repository": bool(record.get("repositories")),
        "deployment": bool(deployment.get("provider") and deployment.get("target")),
        "health": bool(record.get("health_endpoints")),
        "rollback": bool(rollback.get("target_ref") and rollback.get("procedure_ref")),
    }
    missing = [name for name, present in required.items() if not present]
    refs: list[str] = []
    for repository in record.get("repositories") or []:
        if isinstance(repository, Mapping) and repository.get("ref"):
            refs.append(str(repository["ref"]))
    refs.extend(str(item) for item in record.get("health_endpoints") or [] if item)
    refs.extend(
        str(value)
        for value in (rollback.get("target_ref"), rollback.get("procedure_ref"))
        if value
    )
    return not missing, missing, refs


def _evaluation_status(evaluation_receipt: Mapping[str, Any] | None) -> StageResult:
    if not isinstance(evaluation_receipt, Mapping):
        return _stage("HOLD", "No exact-commit evaluation receipt is attached.")

    commit_sha = evaluation_receipt.get("commit_sha")
    scorecard = evaluation_receipt.get("scorecard") or {}
    bundle = evaluation_receipt.get("evidence_bundle") or {}
    promotion = evaluation_receipt.get("promotion_decision") or {}
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        return _stage("HOLD", "Evaluation receipt does not bind an exact 40-character commit SHA.")
    if scorecard.get("hard_gate_failures"):
        return _stage("HOLD", "Evaluation hard gates failed.")
    if (bundle.get("governance_decision") or {}).get("decision") not in {"allow", "promote"}:
        return _stage("HOLD", "Evaluation evidence bundle is not governance-admitted.")

    decision = promotion.get("decision")
    if decision not in {"hold", "promote"}:
        return _stage("HOLD", "Promotion decision is missing or invalid.")

    return _stage(
        "PASS",
        f"Exact-commit evaluation evidence is admitted; release recommendation is {decision.upper()}.",
        f"commit://{commit_sha}",
        str(bundle.get("bundle_id") or ""),
        str(promotion.get("decision_id") or ""),
    )


def _rollback_status(rollback_drill: Mapping[str, Any] | None) -> StageResult:
    if not isinstance(rollback_drill, Mapping):
        return _stage("HOLD", "Rollback drill receipt is missing.")
    if rollback_drill.get("schema") != "kpgs.estate-rollback-drill.v1":
        return _stage("HOLD", "Rollback drill receipt schema is not canonical.")
    if rollback_drill.get("passed") is not True:
        return _stage("HOLD", "Rollback drill did not pass.")
    if rollback_drill.get("automatic_execution") is not False:
        return _stage("HOLD", "Rollback drill must not imply automatic rollback authority.")
    refs = rollback_drill.get("evidence_refs") or []
    if not isinstance(refs, list) or not refs:
        return _stage("HOLD", "Rollback drill has no evidence references.")
    return _stage("PASS", "Rollback drill passed without granting rollback authority.", *refs)


def assess_migration(
    *,
    estate_id: str,
    property_record: Mapping[str, Any],
    workflow_id: str,
    evaluation_receipt: Mapping[str, Any] | None = None,
    rollback_drill: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a truthful migration recommendation for one bounded workflow."""
    if not estate_id or not workflow_id:
        raise MigrationError("estate_id and workflow_id are required")
    domain = property_record.get("domain")
    if not isinstance(domain, str) or "." not in domain:
        raise MigrationError("property_record.domain is invalid")

    stages: dict[str, StageResult] = {}
    baseline_ok, baseline_missing, baseline_refs = _baseline_evidence(property_record)
    stages["baseline"] = (
        _stage("PASS", "Repository/deployment/health/rollback baseline is recorded.", *baseline_refs)
        if baseline_ok
        else _stage(
            "HOLD",
            "Baseline is incomplete: " + ", ".join(baseline_missing),
            *baseline_refs,
        )
    )

    status = property_record.get("status")
    witnessed = bool(property_record.get("ownership_evidence"))
    registration_complete = _property_complete_for_registration(property_record)
    if status == "declared_pending_witness" or not witnessed:
        stages["register"] = _stage(
            "HOLD",
            "Authoritative ownership/domain-control witness is required before registration.",
        )
    elif status in {"witnessed", "registered", "staging", "production"} and registration_complete:
        stages["register"] = _stage(
            "PASS",
            f"Property lifecycle state {status} has the required registration contract fields.",
            *[
                str(item.get("ref"))
                for item in property_record.get("ownership_evidence") or []
                if isinstance(item, Mapping) and item.get("ref")
            ],
        )
    else:
        stages["register"] = _stage(
            "HOLD",
            "Property cannot enter the migration lane until registration completeness is satisfied.",
        )

    adapter = property_record.get("adapter") or {}
    adapter_ok = bool(adapter.get("implementation") and adapter.get("version"))
    stages["adapter_integration"] = (
        _stage(
            "PASS",
            "Versioned domain adapter is declared.",
            f"adapter://{adapter.get('implementation')}@{adapter.get('version')}",
        )
        if adapter_ok
        else _stage("HOLD", "Versioned domain adapter implementation is not recorded.")
    )

    capabilities = property_record.get("capabilities") or []
    stages["capability_map"] = (
        _stage("PASS", "Property has an explicit capability map.", *[f"capability://{item}" for item in capabilities])
        if capabilities
        else _stage("HOLD", "No property capability map is recorded.")
    )

    renter = property_record.get("renter_compatibility") or {}
    renter_ok = renter.get("status") == "conformant" and bool(renter.get("protocol_version"))
    stages["renter_integration"] = (
        _stage(
            "PASS",
            "Stateless Renter protocol is conformant.",
            f"renter-protocol://{renter.get('protocol_version')}",
        )
        if renter_ok
        else _stage("HOLD", "Stateless Renter compatibility is not conformant and versioned.")
    )

    health = property_record.get("health_endpoints") or []
    stages["realtime_wiring"] = (
        _stage(
            "PASS",
            "At least one governed health/evidence endpoint is available for reconnect verification.",
            *health,
        )
        if health
        else _stage("HOLD", "No health/evidence endpoint is recorded for reconnect verification.")
    )

    stages["evaluation"] = _evaluation_status(evaluation_receipt)

    prerequisites_for_staging = (
        "baseline",
        "register",
        "adapter_integration",
        "capability_map",
        "renter_integration",
        "realtime_wiring",
        "evaluation",
    )
    staging_ready = all(stages[name].status == "PASS" for name in prerequisites_for_staging)
    stages["staging"] = (
        _stage(
            "PASS",
            "Software/evidence prerequisites are ready for a separately capability-gated staging transition.",
        )
        if staging_ready
        else _stage("NOT_REACHED", "Staging transition is not reachable until all prior gates pass.")
    )

    stages["rollback_drill"] = (
        _rollback_status(rollback_drill)
        if staging_ready
        else _stage("NOT_REACHED", "Rollback drill is not reached before staging prerequisites pass.")
    )

    release = property_record.get("release") or {}
    rollback = property_record.get("rollback") or {}
    promotion_decision = (evaluation_receipt or {}).get("promotion_decision") or {}
    production_ready = all(
        (
            stages["staging"].status == "PASS",
            stages["rollback_drill"].status == "PASS",
            status == "staging",
            bool(release.get("live_ref")),
            bool(release.get("evidence_ref")),
            bool(rollback.get("target_ref")),
            bool(rollback.get("procedure_ref")),
            promotion_decision.get("decision") == "promote",
            bool(promotion_decision.get("human_approval_ref")),
        )
    )
    stages["production_promotion"] = (
        _stage(
            "PASS",
            "Production promotion prerequisites are complete; registry transition still requires release capability authority.",
            str(release.get("live_ref")),
            str(release.get("evidence_ref")),
            str(rollback.get("target_ref")),
            str(rollback.get("procedure_ref")),
            str(promotion_decision.get("human_approval_ref")),
        )
        if production_ready
        else _stage(
            "NOT_REACHED",
            "Production remains blocked until staging, rollback drill, exact release evidence and required human approval are all present.",
        )
    )
    stages["observe"] = (
        _stage("PASS", "Production observation may begin after a separately authorized production transition.")
        if stages["production_promotion"].status == "PASS"
        else _stage("NOT_REACHED", "Observation is not reached before production promotion eligibility.")
    )

    migration_id = "migration_" + _hash(
        {"estate_id": estate_id, "domain": domain.casefold(), "workflow_id": workflow_id}
    )[:24]
    return {
        "schema": "kpgs.estate-migration-assessment.v1",
        "migration_id": migration_id,
        "estate_id": estate_id,
        "domain": domain,
        "workflow_id": workflow_id,
        "source_property_status": status,
        "stages": {name: stages[name].as_dict() for name in MIGRATION_STAGES},
        "ready_for_staging": staging_ready,
        "ready_for_production": production_ready,
        "recommendation": (
            "ELIGIBLE_FOR_PRODUCTION_TRANSITION"
            if production_ready
            else "ELIGIBLE_FOR_STAGING_TRANSITION"
            if staging_ready
            else "HOLD"
        ),
        "canonical_registry_changed": False,
        "authority_effect": "none",
        "next_action": (
            "Use the capability-gated estate registry transition only after this exact evidence set is reviewed."
            if staging_ready
            else next(
                result.detail
                for name in MIGRATION_STAGES
                if (result := stages[name]).status == "HOLD"
            )
        ),
    }


def assess_estate(
    estate_document: Mapping[str, Any],
    *,
    workflow_id: str,
) -> list[dict[str, Any]]:
    """Assess every property without enriching or mutating canonical registry state."""
    estate_id = estate_document.get("estate_id")
    properties = estate_document.get("properties")
    if not isinstance(estate_id, str) or not isinstance(properties, list):
        raise MigrationError("invalid estate document")
    return [
        assess_migration(
            estate_id=estate_id,
            property_record=deepcopy(record),
            workflow_id=workflow_id,
        )
        for record in properties
    ]
