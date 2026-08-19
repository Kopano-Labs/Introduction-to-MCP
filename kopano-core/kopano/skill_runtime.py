"""Canonical KPGS skill-package execution membrane.

Skills describe bounded procedures; they never grant themselves authority. This
runtime deliberately depends on an injected capability authorizer so the
Sovereign Hub remains the landlord of leases while Stateless Renters stay
replaceable execution tenants.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
from typing import Any, Callable, Mapping, Protocol

PRODUCTION_STATES = {"validated", "approved"}
PRODUCTION_LICENSE_STATUS = "verified-compatible"


class SkillRuntimeError(Exception):
    """Base class for fail-closed skill runtime errors."""


class SkillNotFound(SkillRuntimeError):
    pass


class SkillNotLoadable(SkillRuntimeError):
    pass


class SkillAuthorizationDenied(SkillRuntimeError):
    pass


class SkillValidationFailed(SkillRuntimeError):
    pass


class CapabilityAuthorizer(Protocol):
    def __call__(
        self,
        token: str,
        *,
        tenant_id: str,
        domain_id: str,
        task_id: str,
        capability: str,
        resource_scope: str,
        operation_nonce: str,
        correlation_id: str,
    ) -> Any: ...


SkillHandler = Callable[[Any], Any]
OutputValidator = Callable[[Any], tuple[bool, str]]
EvidenceSink = Callable[[Mapping[str, Any]], None]


@dataclass(frozen=True)
class SkillSelection:
    name: str
    version: str
    package_path: str
    authority_class: str
    manifest: Mapping[str, Any]


@dataclass(frozen=True)
class SkillExecutionResult:
    output: Any
    receipt: Mapping[str, Any]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _decision_dict(decision: Any) -> dict[str, Any]:
    if is_dataclass(decision):
        return asdict(decision)
    if isinstance(decision, Mapping):
        return dict(decision)
    return {
        key: getattr(decision, key)
        for key in (
            "lease_id",
            "subject_id",
            "subject_kind",
            "tenant_id",
            "domain_id",
            "task_id",
            "capability",
            "resource_scope",
            "correlation_id",
            "key_id",
        )
        if hasattr(decision, key)
    }


class CanonicalSkillRuntime:
    """Discover, authorize, execute, validate and receipt one registered skill.

    The runtime never interprets registry presence as permission. A package must
    already be in a production-loadable state with verified-compatible licensing,
    and every non-optional capability must be authorized by the injected lease
    authority before the handler runs.
    """

    def __init__(
        self,
        *,
        repo_root: Path,
        capability_authorizer: CapabilityAuthorizer,
        registry_path: Path | None = None,
        evidence_sink: EvidenceSink | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.registry_path = (
            Path(registry_path).resolve()
            if registry_path
            else self.repo_root / "governance/kpgs-vnext/skills/registry.json"
        )
        self.capability_authorizer = capability_authorizer
        self.evidence_sink = evidence_sink
        self._handlers: dict[tuple[str, str], SkillHandler] = {}
        self._validators: dict[tuple[str, str], OutputValidator] = {}

    def register_handler(
        self,
        name: str,
        version: str,
        handler: SkillHandler,
        *,
        output_validator: OutputValidator | None = None,
    ) -> None:
        identity = (name, version)
        self._handlers[identity] = handler
        if output_validator is not None:
            self._validators[identity] = output_validator

    def discover(self, query: str = "") -> list[dict[str, Any]]:
        registry = self._read_json(self.registry_path)
        needle = query.casefold().strip()
        found: list[dict[str, Any]] = []
        for entry in registry.get("skills", []):
            if not isinstance(entry, dict):
                continue
            discovery = entry.get("discovery", {})
            haystack = " ".join(
                [
                    str(entry.get("name", "")),
                    str(entry.get("category", "")),
                    str(discovery.get("summary", "")),
                    *[str(tag) for tag in discovery.get("tags", [])],
                ]
            ).casefold()
            if not needle or needle in haystack:
                found.append(dict(entry))
        return found

    def select(self, name: str, version: str, *, platform: str) -> SkillSelection:
        registry = self._read_json(self.registry_path)
        policy = registry.get("selection_policy")
        if not isinstance(policy, dict):
            raise SkillNotLoadable("registry selection_policy is missing")
        if set(policy.get("production_states", [])) != PRODUCTION_STATES:
            raise SkillNotLoadable("registry production-state policy drift detected")
        if policy.get("require_capability_lease") is not True:
            raise SkillNotLoadable("registry no longer requires capability leases")
        if policy.get("require_provenance") is not True:
            raise SkillNotLoadable("registry no longer requires provenance")
        if policy.get("require_license_status") is not True:
            raise SkillNotLoadable("registry no longer requires license status")

        entries = [
            entry
            for entry in registry.get("skills", [])
            if isinstance(entry, dict)
            and entry.get("name") == name
            and entry.get("version") == version
        ]
        if len(entries) != 1:
            raise SkillNotFound(f"registered skill not found: {name}@{version}")

        entry = entries[0]
        package_path = entry.get("package_path")
        if not isinstance(package_path, str) or not package_path:
            raise SkillNotLoadable("registry package_path is invalid")
        package_dir = (self.repo_root / package_path).resolve()
        if package_dir != self.repo_root and self.repo_root not in package_dir.parents:
            raise SkillNotLoadable("package path escapes repository root")

        manifest = self._read_json(package_dir / "skill.json")
        if manifest.get("name") != name or manifest.get("version") != version:
            raise SkillNotLoadable("registry/manifest identity mismatch")
        if manifest.get("state") not in PRODUCTION_STATES:
            raise SkillNotLoadable(
                f"{name}@{version} is not production-loadable: {manifest.get('state')}"
            )
        platforms = manifest.get("runtime", {}).get("platforms", [])
        if platform not in platforms:
            raise SkillNotLoadable(f"runtime platform is not declared: {platform}")

        provenance = manifest.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("origin"):
            raise SkillNotLoadable("provenance is incomplete")
        license_status = provenance.get("license_status")
        if license_status != PRODUCTION_LICENSE_STATUS:
            raise SkillNotLoadable(
                f"{name}@{version} license status is not production-compatible: {license_status}"
            )
        sources = provenance.get("sources")
        if not isinstance(sources, list) or not sources:
            raise SkillNotLoadable("provenance sources are incomplete")
        if not (package_dir / "SKILL.md").is_file():
            raise SkillNotLoadable("SKILL.md is missing")

        return SkillSelection(
            name=name,
            version=version,
            package_path=package_path,
            authority_class=str(entry.get("authority_class", "")),
            manifest=manifest,
        )

    def execute(
        self,
        *,
        name: str,
        version: str,
        platform: str,
        lease_token: str,
        tenant_id: str,
        domain_id: str,
        task_id: str,
        correlation_id: str,
        input_value: Any,
    ) -> SkillExecutionResult:
        selection = self.select(name, version, platform=platform)
        identity = (name, version)
        handler = self._handlers.get(identity)
        if handler is None:
            raise SkillNotLoadable(f"no bounded handler registered for {name}@{version}")

        execution_id = "skill_exec_" + secrets.token_urlsafe(12)
        capability_decisions: list[dict[str, Any]] = []
        requirements = selection.manifest.get("required_capabilities", [])
        if not isinstance(requirements, list) or not requirements:
            raise SkillAuthorizationDenied("skill declares no capability requirements")

        for index, requirement in enumerate(requirements):
            if not isinstance(requirement, dict):
                raise SkillAuthorizationDenied("invalid capability requirement")
            if requirement.get("optional") is True:
                continue
            capability = requirement.get("name")
            resource_scope = requirement.get("resource_scope")
            if not isinstance(capability, str) or not isinstance(resource_scope, str):
                raise SkillAuthorizationDenied("invalid required capability contract")
            try:
                decision = self.capability_authorizer(
                    lease_token,
                    tenant_id=tenant_id,
                    domain_id=domain_id,
                    task_id=task_id,
                    capability=capability,
                    resource_scope=resource_scope,
                    operation_nonce=f"{execution_id}:{index}",
                    correlation_id=correlation_id,
                )
            except Exception as exc:
                raise SkillAuthorizationDenied(
                    f"capability denied before execution: {capability}@{resource_scope}: {type(exc).__name__}"
                ) from exc
            capability_decisions.append(_decision_dict(decision))

        input_digest = _digest(input_value)
        try:
            output = handler(input_value)
        except Exception as exc:
            receipt = self._receipt(
                selection=selection,
                execution_id=execution_id,
                correlation_id=correlation_id,
                input_digest=input_digest,
                output_digest=None,
                capability_decisions=capability_decisions,
                validation={
                    "passed": False,
                    "reason": "bounded handler raised",
                    "kind": "execution",
                },
                outcome="failed",
                failure=f"HANDLER_FAILED:{type(exc).__name__}",
            )
            self._emit(receipt)
            raise

        validator = self._validators.get(identity)
        if validator is None:
            passed, reason = (
                True,
                "handler completed; no additional runtime output validator registered",
            )
        else:
            passed, reason = validator(output)
        if not passed:
            receipt = self._receipt(
                selection=selection,
                execution_id=execution_id,
                correlation_id=correlation_id,
                input_digest=input_digest,
                output_digest=_digest(output),
                capability_decisions=capability_decisions,
                validation={
                    "passed": False,
                    "reason": reason,
                    "kind": "deterministic",
                },
                outcome="rejected",
                failure="output validation failed",
            )
            self._emit(receipt)
            raise SkillValidationFailed(reason)

        receipt = self._receipt(
            selection=selection,
            execution_id=execution_id,
            correlation_id=correlation_id,
            input_digest=input_digest,
            output_digest=_digest(output),
            capability_decisions=capability_decisions,
            validation={"passed": True, "reason": reason, "kind": "deterministic"},
            outcome="completed",
            failure=None,
        )
        self._emit(receipt)
        return SkillExecutionResult(output=output, receipt=receipt)

    def _receipt(
        self,
        *,
        selection: SkillSelection,
        execution_id: str,
        correlation_id: str,
        input_digest: str,
        output_digest: str | None,
        capability_decisions: list[dict[str, Any]],
        validation: Mapping[str, Any],
        outcome: str,
        failure: str | None,
    ) -> dict[str, Any]:
        manifest = dict(selection.manifest)
        lease_ids = sorted(
            {
                str(decision.get("lease_id"))
                for decision in capability_decisions
                if decision.get("lease_id")
            }
        )
        return {
            "schema": "kpgs.skill-execution-receipt.v1",
            "execution_id": execution_id,
            "skill": {
                "name": selection.name,
                "version": selection.version,
                "package_path": selection.package_path,
                "authority_class": selection.authority_class,
                "manifest_digest": _digest(manifest),
                "license_status": manifest.get("provenance", {}).get("license_status"),
            },
            "correlation_id": correlation_id,
            "input_digest": input_digest,
            "output_digest": output_digest,
            "capability_lease_ids": lease_ids,
            "capability_decisions": capability_decisions,
            "validation": dict(validation),
            "outcome": outcome,
            "failure": failure,
            "authority_effect": "none",
            "execution_context": {
                "released": True,
                "upstream_lease_revoked": False,
            },
            "created_at": _iso_now(),
        }

    def _emit(self, receipt: Mapping[str, Any]) -> None:
        if self.evidence_sink is not None:
            self.evidence_sink(receipt)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise SkillNotLoadable(f"missing skill runtime file: {path}") from exc
        except json.JSONDecodeError as exc:
            raise SkillNotLoadable(f"invalid JSON: {path}") from exc
        if not isinstance(value, dict):
            raise SkillNotLoadable(f"expected JSON object: {path}")
        return value
