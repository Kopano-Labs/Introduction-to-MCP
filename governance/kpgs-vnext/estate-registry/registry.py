"""Executable KPGS Sovereign DNS Estate Registry reference runtime.

The registry is canonical control-plane state. Mutations require an injected
KPGS capability-lease authority and an exact request context. Discovery never
self-promotes: unknown domains first enter an unwitnessed review queue.

Realtime/SWFUS distribution is optional projection alignment. A failed
transport does not roll back an already-authorized canonical registry commit;
availability and synchronization remain separate from authority.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import secrets
from typing import Any, Callable, Mapping, MutableMapping

PROPERTY_STATUSES = {
    "declared_pending_witness",
    "witnessed",
    "registered",
    "staging",
    "production",
    "suspended",
    "decommissioned",
}
CANDIDATE_STATUSES = {
    "unwitnessed",
    "witnessed",
    "classified",
    "rejected",
    "registered",
}
ALLOWED_TRANSITIONS = {
    "registered": {"staging", "suspended", "decommissioned"},
    "staging": {"production", "registered", "suspended"},
    "production": {"staging", "suspended"},
    "suspended": {"registered", "decommissioned"},
    "decommissioned": set(),
}
SOURCE_KINDS = {
    "registrar",
    "dns",
    "deployment",
    "repository",
    "domain-control",
    "other",
}
RISK_CLASSES = {"R0", "R1", "R2", "R3"}


class RegistryError(Exception):
    pass


class RegistryConflict(RegistryError):
    pass


class RegistryTransitionDenied(RegistryError):
    pass


@dataclass(frozen=True)
class MutationContext:
    token: str
    tenant_id: str
    domain_id: str
    task_id: str
    operation_nonce: str
    correlation_id: str


def _parse_iso8601(value: Any, field_name: str) -> str:
    """Validate and normalize an ISO-8601 timestamp to UTC text."""

    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{field_name} is required")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryError(f"{field_name} is not valid ISO-8601") from exc
    if parsed.tzinfo is None:
        raise RegistryError(f"{field_name} must include timezone")
    return (
        parsed.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class SovereignEstateRegistry:
    """Governed canonical registry plus explicit unwitnessed discovery queue."""

    def __init__(
        self,
        registry_document: Mapping[str, Any],
        lease_authority: Any,
        *,
        clock: Callable[[], datetime] | None = None,
        distribution_sink: Callable[[dict[str, Any]], None] | None = None,
    ):
        self._document = deepcopy(dict(registry_document))
        self.lease_authority = lease_authority
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._distribution_sink = distribution_sink
        self._candidates: MutableMapping[str, dict[str, Any]] = {}
        self._candidate_by_domain: dict[str, str] = {}
        self._events: list[dict[str, Any]] = []
        self._validate_seed()

    @staticmethod
    def _domain_key(domain: str) -> str:
        return domain.strip().rstrip(".").casefold()

    @staticmethod
    def _clean_domain(domain: str) -> str:
        if not isinstance(domain, str):
            raise RegistryError("domain must be a string")
        cleaned = domain.strip().rstrip(".")
        if (
            len(cleaned) < 3
            or "." not in cleaned
            or " " in cleaned
            or cleaned.startswith(".")
            or cleaned.endswith(".")
        ):
            raise RegistryError("domain is invalid")
        labels = cleaned.split(".")
        if any(not label or len(label) > 63 for label in labels):
            raise RegistryError("domain labels are invalid")
        return cleaned

    @staticmethod
    def _now(clock: Callable[[], datetime]) -> str:
        return (
            clock()
            .astimezone(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    def _validate_seed(self) -> None:
        if not isinstance(self._document.get("estate_id"), str):
            raise RegistryError("estate_id is required")
        properties = self._document.get("properties")
        if not isinstance(properties, list) or not properties:
            raise RegistryError("registry requires properties")
        seen: set[str] = set()
        for record in properties:
            domain = self._clean_domain(record.get("domain", ""))
            key = self._domain_key(domain)
            if key in seen:
                raise RegistryConflict(f"duplicate domain: {domain}")
            seen.add(key)
            if record.get("status") not in PROPERTY_STATUSES:
                raise RegistryError(
                    f"invalid property status: {record.get('status')}"
                )

    @property
    def estate_id(self) -> str:
        return self._document["estate_id"]

    def _estate_scope(self) -> str:
        return f"estate:{self.estate_id}"

    @staticmethod
    def _property_scope(domain: str) -> str:
        return f"dns:{domain}"

    def _authorize(
        self,
        context: MutationContext,
        *,
        capability: str,
        resource_scope: str,
    ) -> Any:
        return self.lease_authority.authorize(
            context.token,
            tenant_id=context.tenant_id,
            domain_id=context.domain_id,
            task_id=context.task_id,
            capability=capability,
            resource_scope=resource_scope,
            operation_nonce=context.operation_nonce,
            correlation_id=context.correlation_id,
        )

    def _property(self, domain: str) -> dict[str, Any]:
        key = self._domain_key(self._clean_domain(domain))
        for record in self._document["properties"]:
            if self._domain_key(record["domain"]) == key:
                return record
        raise RegistryError(f"unknown property: {domain}")

    @staticmethod
    def _witness(evidence: Mapping[str, Any]) -> dict[str, Any]:
        kind = evidence.get("kind")
        ref = evidence.get("ref")
        verified_at = evidence.get("verified_at")
        if kind not in SOURCE_KINDS:
            raise RegistryError("witness kind is invalid")
        if not isinstance(ref, str) or not ref.strip():
            raise RegistryError("witness ref is required")
        normalized_time = (
            None
            if verified_at is None
            else _parse_iso8601(verified_at, "verified_at")
        )
        return {
            "kind": kind,
            "ref": ref.strip(),
            "verified_at": normalized_time,
        }

    def _emit(
        self,
        *,
        action: str,
        decision: Any,
        correlation_id: str,
        domain: str | None = None,
        candidate_id: str | None = None,
        before_status: str | None = None,
        after_status: str | None = None,
        evidence_refs: list[str] | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        canonical_registry_changed = action.startswith("property-") or action in {
            "candidate-registered"
        }
        event = {
            "schema": "kpgs.estate-registry.event.v1",
            "event_id": "estate_evt_" + secrets.token_urlsafe(12),
            "estate_id": self.estate_id,
            "action": action,
            "domain": domain,
            "candidate_id": candidate_id,
            "before_status": before_status,
            "after_status": after_status,
            "lease_id": getattr(decision, "lease_id", None),
            "correlation_id": correlation_id,
            "evidence_refs": list(evidence_refs or []),
            "details": deepcopy(dict(details or {})),
            "canonical_registry_changed": canonical_registry_changed,
            "transport_grants_authority": False,
            "distribution_status": "not-configured",
            "created_at": self._now(self._clock),
        }
        if self._distribution_sink is not None:
            try:
                self._distribution_sink(deepcopy(event))
                event["distribution_status"] = "distributed"
            except Exception as exc:
                event["distribution_status"] = "unavailable"
                event["distribution_error"] = type(exc).__name__
        self._events.append(event)
        return deepcopy(event)

    def discover_candidate(
        self,
        domain: str,
        *,
        provenance: Mapping[str, Any],
        context: MutationContext,
    ) -> dict[str, Any]:
        decision = self._authorize(
            context,
            capability="estate.discovery.write",
            resource_scope=self._estate_scope(),
        )
        cleaned = self._clean_domain(domain)
        key = self._domain_key(cleaned)
        try:
            known = self._property(cleaned)
        except RegistryError:
            known = None
        if known is not None:
            raise RegistryConflict("domain already exists in canonical registry")

        source_kind = provenance.get("kind")
        source_ref = provenance.get("ref")
        observed_at = provenance.get("observed_at")
        if source_kind not in SOURCE_KINDS:
            raise RegistryError("discovery source kind is invalid")
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise RegistryError("discovery source ref is required")
        source = {
            "kind": source_kind,
            "ref": source_ref.strip(),
            "observed_at": _parse_iso8601(observed_at, "observed_at"),
        }

        existing_id = self._candidate_by_domain.get(key)
        if existing_id:
            candidate = self._candidates[existing_id]
            if source not in candidate["provenance"]:
                candidate["provenance"].append(source)
            self._emit(
                action="candidate-observed",
                decision=decision,
                correlation_id=context.correlation_id,
                domain=candidate["domain"],
                candidate_id=existing_id,
                before_status=candidate["status"],
                after_status=candidate["status"],
            )
            return deepcopy(candidate)

        candidate_id = (
            "candidate_"
            + hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
        )
        candidate = {
            "schema": "kpgs.estate-candidate.v1",
            "candidate_id": candidate_id,
            "domain": cleaned,
            "status": "unwitnessed",
            "provenance": [source],
            "witness_evidence": [],
            "classification": None,
            "discovered_at": self._now(self._clock),
            "registered_at": None,
        }
        self._candidates[candidate_id] = candidate
        self._candidate_by_domain[key] = candidate_id
        self._emit(
            action="candidate-discovered",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=cleaned,
            candidate_id=candidate_id,
            after_status="unwitnessed",
        )
        return deepcopy(candidate)

    def witness_candidate(
        self,
        candidate_id: str,
        evidence: Mapping[str, Any],
        *,
        context: MutationContext,
    ) -> dict[str, Any]:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise RegistryError("unknown discovery candidate")
        decision = self._authorize(
            context,
            capability="estate.registry.witness",
            resource_scope=self._property_scope(candidate["domain"]),
        )
        if candidate["status"] not in {"unwitnessed", "witnessed"}:
            raise RegistryTransitionDenied(
                "candidate cannot be witnessed from current state"
            )
        witness = self._witness(evidence)
        if witness not in candidate["witness_evidence"]:
            candidate["witness_evidence"].append(witness)
        before = candidate["status"]
        candidate["status"] = "witnessed"
        self._emit(
            action="candidate-witnessed",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=candidate["domain"],
            candidate_id=candidate_id,
            before_status=before,
            after_status="witnessed",
            evidence_refs=[witness["ref"]],
        )
        return deepcopy(candidate)

    def classify_candidate(
        self,
        candidate_id: str,
        *,
        owner_ref: str,
        governance_tier: str,
        risk_class: str,
        context: MutationContext,
    ) -> dict[str, Any]:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise RegistryError("unknown discovery candidate")
        decision = self._authorize(
            context,
            capability="estate.registry.classify",
            resource_scope=self._property_scope(candidate["domain"]),
        )
        if candidate["status"] != "witnessed":
            raise RegistryTransitionDenied(
                "candidate must be witnessed before classification"
            )
        if not isinstance(owner_ref, str) or not owner_ref.strip():
            raise RegistryError("owner reference is required")
        if not isinstance(governance_tier, str) or not governance_tier.strip():
            raise RegistryError("governance tier is required")
        if risk_class not in RISK_CLASSES:
            raise RegistryError("risk class is invalid")
        candidate["classification"] = {
            "owner_ref": owner_ref.strip(),
            "governance_tier": governance_tier.strip(),
            "risk_class": risk_class,
        }
        candidate["status"] = "classified"
        self._emit(
            action="candidate-classified",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=candidate["domain"],
            candidate_id=candidate_id,
            before_status="witnessed",
            after_status="classified",
            details=candidate["classification"],
        )
        return deepcopy(candidate)

    @staticmethod
    def _validate_registered_record(record: Mapping[str, Any]) -> None:
        for field_name in (
            "ownership_evidence",
            "repositories",
            "capabilities",
            "health_endpoints",
        ):
            value = record.get(field_name)
            if not isinstance(value, list) or not value:
                raise RegistryError(
                    f"registered property requires {field_name}"
                )

        deployment = record.get("deployment")
        if (
            not isinstance(deployment, dict)
            or not deployment.get("provider")
            or not deployment.get("target")
        ):
            raise RegistryError(
                "registered property requires deployment provider and target"
            )

        governance = record.get("governance")
        if (
            not isinstance(governance, dict)
            or not governance.get("policy_ref")
            or governance.get("risk_class") not in RISK_CLASSES
            or not governance.get("tier")
        ):
            raise RegistryError(
                "registered property requires governance policy, risk class and tier"
            )

        owner = record.get("owner")
        if not isinstance(owner, dict) or not owner.get("ref"):
            raise RegistryError("registered property requires owner reference")

        for ref in record.get("secret_provider_refs", []):
            if not isinstance(ref, str) or "://" not in ref:
                raise RegistryError(
                    "secret provider entries must be references, never raw secrets"
                )

    @staticmethod
    def _apply_candidate_classification(
        property_record: dict[str, Any],
        classification: Mapping[str, Any],
    ) -> None:
        """Make witnessed classification authoritative over submitted metadata."""

        supplied_owner = property_record.get("owner")
        if (
            isinstance(supplied_owner, dict)
            and supplied_owner.get("ref")
            and supplied_owner.get("ref") != classification["owner_ref"]
        ):
            raise RegistryConflict(
                "registration owner conflicts with witnessed classification"
            )
        property_record["owner"] = {
            "ref": classification["owner_ref"],
            "kind": "classified-owner",
        }

        governance = property_record.setdefault("governance", {})
        supplied_risk = governance.get("risk_class")
        supplied_tier = governance.get("tier")
        if supplied_risk not in {None, classification["risk_class"]}:
            raise RegistryConflict(
                "registration risk class conflicts with classification"
            )
        if supplied_tier not in {None, classification["governance_tier"]}:
            raise RegistryConflict(
                "registration governance tier conflicts with classification"
            )
        governance["risk_class"] = classification["risk_class"]
        governance["tier"] = classification["governance_tier"]

    def register_candidate(
        self,
        candidate_id: str,
        record: Mapping[str, Any],
        *,
        context: MutationContext,
    ) -> dict[str, Any]:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise RegistryError("unknown discovery candidate")
        if candidate["status"] != "classified":
            raise RegistryTransitionDenied(
                "candidate must be classified before registration"
            )
        decision = self._authorize(
            context,
            capability="estate.registry.write",
            resource_scope=self._property_scope(candidate["domain"]),
        )
        property_record = deepcopy(dict(record))
        if self._domain_key(property_record.get("domain", "")) != self._domain_key(
            candidate["domain"]
        ):
            raise RegistryConflict(
                "candidate and property domain must match"
            )
        property_record["domain"] = candidate["domain"]
        property_record["status"] = "registered"
        property_record["ownership_evidence"] = deepcopy(
            candidate["witness_evidence"]
        )
        classification = candidate.get("classification")
        if not isinstance(classification, dict):
            raise RegistryTransitionDenied(
                "candidate classification is missing"
            )
        self._apply_candidate_classification(
            property_record,
            classification,
        )
        self._validate_registered_record(property_record)

        try:
            self._property(candidate["domain"])
        except RegistryError:
            pass
        else:
            raise RegistryConflict(
                "candidate domain already exists in registry"
            )

        self._document["properties"].append(property_record)
        candidate["status"] = "registered"
        candidate["registered_at"] = self._now(self._clock)
        self._emit(
            action="candidate-registered",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=candidate["domain"],
            candidate_id=candidate_id,
            before_status="classified",
            after_status="registered",
            evidence_refs=[
                item["ref"] for item in candidate["witness_evidence"]
            ],
        )
        return deepcopy(property_record)

    def witness_property(
        self,
        domain: str,
        evidence: Mapping[str, Any],
        *,
        context: MutationContext,
    ) -> dict[str, Any]:
        record = self._property(domain)
        decision = self._authorize(
            context,
            capability="estate.registry.witness",
            resource_scope=self._property_scope(record["domain"]),
        )
        if record["status"] not in {
            "declared_pending_witness",
            "witnessed",
        }:
            raise RegistryTransitionDenied(
                "property cannot accept witness in current state"
            )
        witness = self._witness(evidence)
        if witness not in record["ownership_evidence"]:
            record["ownership_evidence"].append(witness)
        before = record["status"]
        record["status"] = "witnessed"
        self._emit(
            action="property-witnessed",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=record["domain"],
            before_status=before,
            after_status="witnessed",
            evidence_refs=[witness["ref"]],
        )
        return deepcopy(record)

    def register_property(
        self,
        domain: str,
        metadata: Mapping[str, Any],
        *,
        context: MutationContext,
    ) -> dict[str, Any]:
        record = self._property(domain)
        decision = self._authorize(
            context,
            capability="estate.registry.write",
            resource_scope=self._property_scope(record["domain"]),
        )
        if record["status"] != "witnessed":
            raise RegistryTransitionDenied(
                "property must be witnessed before registration"
            )
        before = deepcopy(record)
        preserved_evidence = deepcopy(record["ownership_evidence"])
        for key, value in metadata.items():
            if key in {"domain", "status", "ownership_evidence"}:
                continue
            record[key] = deepcopy(value)
        record["ownership_evidence"] = preserved_evidence
        record["status"] = "registered"
        try:
            self._validate_registered_record(record)
        except Exception:
            record.clear()
            record.update(before)
            raise
        self._emit(
            action="property-registered",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=record["domain"],
            before_status="witnessed",
            after_status="registered",
            evidence_refs=[
                item["ref"] for item in record["ownership_evidence"]
            ],
        )
        return deepcopy(record)

    def transition_property(
        self,
        domain: str,
        target_status: str,
        *,
        context: MutationContext,
        release_ref: str | None = None,
        evidence_ref: str | None = None,
        rollback_target_ref: str | None = None,
        rollback_procedure_ref: str | None = None,
    ) -> dict[str, Any]:
        record = self._property(domain)
        decision = self._authorize(
            context,
            capability="estate.release.transition",
            resource_scope=self._property_scope(record["domain"]),
        )
        current = record["status"]
        if target_status not in PROPERTY_STATUSES:
            raise RegistryTransitionDenied("target status is invalid")
        if target_status not in ALLOWED_TRANSITIONS.get(current, set()):
            raise RegistryTransitionDenied(
                f"transition {current} -> {target_status} is not admitted"
            )

        if target_status == "production":
            release_ref = release_ref or record.get("release", {}).get(
                "live_ref"
            )
            evidence_ref = evidence_ref or record.get("release", {}).get(
                "evidence_ref"
            )
            rollback_target_ref = rollback_target_ref or record.get(
                "rollback", {}
            ).get("target_ref")
            rollback_procedure_ref = rollback_procedure_ref or record.get(
                "rollback", {}
            ).get("procedure_ref")
            if not all(
                [
                    release_ref,
                    evidence_ref,
                    rollback_target_ref,
                    rollback_procedure_ref,
                ]
            ):
                raise RegistryTransitionDenied(
                    "production promotion requires live/evidence and rollback receipts"
                )
            record.setdefault("release", {})["live_ref"] = release_ref
            record["release"]["evidence_ref"] = evidence_ref
            record.setdefault("rollback", {})[
                "target_ref"
            ] = rollback_target_ref
            record["rollback"][
                "procedure_ref"
            ] = rollback_procedure_ref

        record["status"] = target_status
        self._emit(
            action="property-transitioned",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=record["domain"],
            before_status=current,
            after_status=target_status,
            evidence_refs=[evidence_ref] if evidence_ref else [],
            details={"release_ref": release_ref} if release_ref else {},
        )
        return deepcopy(record)

    def rollback_property(
        self,
        domain: str,
        *,
        context: MutationContext,
    ) -> dict[str, Any]:
        record = self._property(domain)
        decision = self._authorize(
            context,
            capability="estate.release.rollback",
            resource_scope=self._property_scope(record["domain"]),
        )
        if record["status"] != "production":
            raise RegistryTransitionDenied(
                "rollback requires a production property"
            )
        rollback = record.get("rollback", {})
        target = rollback.get("target_ref")
        procedure = rollback.get("procedure_ref")
        if not target or not procedure:
            raise RegistryTransitionDenied(
                "rollback target and procedure are required"
            )
        previous_live = record.get("release", {}).get("live_ref")
        record.setdefault("release", {})["live_ref"] = target
        record["status"] = "staging"
        self._emit(
            action="property-rollback",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=record["domain"],
            before_status="production",
            after_status="staging",
            evidence_refs=[procedure],
            details={
                "from_live_ref": previous_live,
                "to_ref": target,
            },
        )
        return deepcopy(record)

    def reject_candidate(
        self,
        candidate_id: str,
        *,
        reason: str,
        context: MutationContext,
    ) -> dict[str, Any]:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise RegistryError("unknown discovery candidate")
        decision = self._authorize(
            context,
            capability="estate.registry.classify",
            resource_scope=self._property_scope(candidate["domain"]),
        )
        if candidate["status"] == "registered":
            raise RegistryTransitionDenied(
                "registered candidate cannot be rejected"
            )
        if not isinstance(reason, str) or not reason.strip():
            raise RegistryError("rejection reason is required")
        before = candidate["status"]
        candidate["status"] = "rejected"
        candidate["rejection_reason"] = reason.strip()
        self._emit(
            action="candidate-rejected",
            decision=decision,
            correlation_id=context.correlation_id,
            domain=candidate["domain"],
            candidate_id=candidate_id,
            before_status=before,
            after_status="rejected",
            details={"reason": reason.strip()},
        )
        return deepcopy(candidate)

    def candidates(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            deepcopy(item) for item in self._candidates.values()
        )

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(event) for event in self._events)

    def snapshot(self) -> dict[str, Any]:
        document = deepcopy(self._document)
        document["generated_at"] = self._now(self._clock)
        return document

    def explain_property(self, domain: str) -> str:
        record = self._property(domain)
        repos = record.get("repositories", [])
        repo_text = (
            ", ".join(
                item.get("repository", "unknown") for item in repos
            )
            or "not witnessed"
        )
        deployment = record.get("deployment", {})
        deployment_text = (
            f"{deployment.get('provider')}:{deployment.get('target')}"
            if deployment.get("provider") and deployment.get("target")
            else "not witnessed"
        )
        adapter = record.get("adapter", {})
        adapter_text = adapter.get("version") or (
            "required / version unknown"
            if adapter.get("required")
            else "not required"
        )
        renter_text = record.get("renter_compatibility", {}).get(
            "status", "unknown"
        )
        governance_text = record.get("governance", {}).get(
            "policy_ref"
        ) or "not classified"
        capabilities = record.get("capabilities", [])
        capability_text = ", ".join(capabilities) or "not granted"
        health = record.get("health_endpoints", [])
        health_text = ", ".join(health) or "not witnessed"
        live_ref = record.get("release", {}).get(
            "live_ref"
        ) or "not promoted"
        evidence_ref = record.get("release", {}).get(
            "evidence_ref"
        ) or "not recorded"
        rollback_ref = record.get("rollback", {}).get(
            "target_ref"
        ) or "not recorded"
        return (
            f"{record['domain']} is {record['status']}. "
            f"Repositories: {repo_text}. Deployment: {deployment_text}. "
            f"Adapter: {adapter_text}. Stateless Renter compatibility: "
            f"{renter_text}. Governance policy: {governance_text}. "
            f"Capabilities: {capability_text}. Health/evidence endpoints: "
            f"{health_text}. Live version: {live_ref}. Release evidence: "
            f"{evidence_ref}. Rollback target: {rollback_ref}."
        )


def registry_digest(document: Mapping[str, Any]) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
