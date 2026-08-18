"""Reference KPGS capability-lease authority runtime.

This module is intentionally standard-library only. It proves the governance
semantics required by issue #42 without turning a Stateless Renter, frontend,
or skill into a credential landlord.

The compact token is a KPGS envelope, not a claim of JWT conformance. An
OIDC/JWT identity boundary may translate an authenticated subject into this
lease at the Sovereign Hub boundary. The signing key ring remains server-side.
"""

from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets
from typing import Any, Callable, Iterable, Mapping

TOKEN_TYPE = "KPGS-LEASE"
TOKEN_ALG = "HS256"
SUBJECT_KINDS = {"renter", "adapter", "skill", "agent", "human", "service"}
FORBIDDEN_AMBIENT_CAPABILITIES = {"admin", "all-access", "*"}


class LeaseError(Exception):
    """Base class for fail-closed lease errors."""


class LeaseSignatureError(LeaseError):
    pass


class LeaseExpired(LeaseError):
    pass


class LeaseRevoked(LeaseError):
    pass


class LeaseDenied(LeaseError):
    pass


class LeaseReplay(LeaseDenied):
    pass


@dataclass(frozen=True)
class AuthorizationDecision:
    lease_id: str
    subject_id: str
    subject_kind: str
    tenant_id: str
    domain_id: str
    task_id: str
    capability: str
    resource_scope: str
    correlation_id: str
    key_id: str


class KeyRing:
    """Server-side signing/verification keys with explicit rotation.

    Rotation switches the active signing key while retaining prior verification
    keys until their leases have naturally expired. Frontends need no redeploy.
    """

    def __init__(self, keys: Mapping[str, bytes], active_key_id: str):
        self._keys: dict[str, bytes] = {}
        for key_id, key in keys.items():
            self._validate_key(key_id, key)
            self._keys[key_id] = bytes(key)
        if active_key_id not in self._keys:
            raise ValueError("active key id must exist in key ring")
        self._active_key_id = active_key_id

    @staticmethod
    def _validate_key(key_id: str, key: bytes) -> None:
        if not isinstance(key_id, str) or not key_id.strip():
            raise ValueError("key id is required")
        if not isinstance(key, (bytes, bytearray)) or len(key) < 32:
            raise ValueError("signing keys must contain at least 32 bytes")

    @property
    def active_key_id(self) -> str:
        return self._active_key_id

    def rotate(self, key_id: str, key: bytes) -> None:
        self._validate_key(key_id, key)
        self._keys[key_id] = bytes(key)
        self._active_key_id = key_id

    def retire(self, key_id: str) -> None:
        if key_id == self._active_key_id:
            raise ValueError("active signing key cannot be retired")
        self._keys.pop(key_id, None)

    def sign(self, key_id: str, message: bytes) -> bytes:
        key = self._keys.get(key_id)
        if key is None:
            raise LeaseSignatureError("unknown signing key")
        return hmac.new(key, message, hashlib.sha256).digest()

    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        key = self._keys.get(key_id)
        if key is None:
            return False
        expected = hmac.new(key, message, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)


def _b64encode(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return urlsafe_b64decode(value + padding)
    except Exception as exc:
        raise LeaseSignatureError("invalid compact-token encoding") from exc


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _iso8601(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _parse_time(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise LeaseDenied(f"{field_name} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LeaseDenied(f"{field_name} is invalid") from exc
    if parsed.tzinfo is None:
        raise LeaseDenied(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc)


class CapabilityLeaseAuthority:
    """Issue, verify, revoke and authorize short-lived capability leases."""

    def __init__(
        self,
        key_ring: KeyRing,
        *,
        issuer: str = "kpgs-sovereign-hub",
        max_ttl_seconds: int = 900,
        clock: Callable[[], datetime] | None = None,
    ):
        if max_ttl_seconds <= 0:
            raise ValueError("max_ttl_seconds must be positive")
        self.key_ring = key_ring
        self.issuer = issuer
        self.max_ttl_seconds = max_ttl_seconds
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._revocations: dict[str, dict[str, str]] = {}
        self._operation_nonces: set[tuple[str, str]] = set()
        self._issued_nonces: set[str] = set()
        self._audit_log: list[dict[str, Any]] = []

    @staticmethod
    def _validate_capabilities(capabilities: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in capabilities:
            name = item.get("name")
            resource_scope = item.get("resource_scope")
            constraints = item.get("constraints", [])
            if not isinstance(name, str) or len(name.strip()) < 3:
                raise LeaseDenied("capability name is required")
            if name in FORBIDDEN_AMBIENT_CAPABILITIES:
                raise LeaseDenied("ambient capability names are forbidden")
            if not isinstance(resource_scope, str) or not resource_scope.strip():
                raise LeaseDenied("resource scope is required")
            if resource_scope.strip() == "*":
                raise LeaseDenied("wildcard resource scope is forbidden")
            if not isinstance(constraints, list) or not all(
                isinstance(value, str) and value.strip() for value in constraints
            ):
                raise LeaseDenied("capability constraints must be non-empty strings")
            normalized.append(
                {
                    "name": name.strip(),
                    "resource_scope": resource_scope.strip(),
                    "constraints": list(constraints),
                }
            )
        if not normalized:
            raise LeaseDenied("at least one capability is required")
        return normalized

    @staticmethod
    def _validate_secret_provider_refs(refs: Iterable[str]) -> list[str]:
        normalized: list[str] = []
        for ref in refs:
            if not isinstance(ref, str) or "://" not in ref:
                raise LeaseDenied(
                    "secret provider references must be URI-like references, not raw secret material"
                )
            normalized.append(ref)
        return normalized

    def _new_nonce(self) -> str:
        while True:
            nonce = secrets.token_urlsafe(18)
            if nonce not in self._issued_nonces:
                self._issued_nonces.add(nonce)
                return nonce

    def _record_audit(
        self,
        *,
        event: str,
        outcome: str,
        reason: str,
        lease: Mapping[str, Any] | None = None,
        capability: str | None = None,
        resource_scope: str | None = None,
        correlation_id: str = "",
        evidence_ref: str = "",
        key_id: str = "",
    ) -> None:
        subject = lease.get("subject", {}) if lease else {}
        self._audit_log.append(
            {
                "schema": "kpgs.capability-audit.v1",
                "event": event,
                "outcome": outcome,
                "reason": reason,
                "lease_id": lease.get("lease_id") if lease else None,
                "subject_id": subject.get("id") if isinstance(subject, dict) else None,
                "subject_kind": subject.get("kind") if isinstance(subject, dict) else None,
                "tenant_id": lease.get("tenant_id") if lease else None,
                "domain_id": lease.get("domain_id") if lease else None,
                "task_id": lease.get("task_id") if lease else None,
                "capability": capability,
                "resource_scope": resource_scope,
                "correlation_id": correlation_id,
                "evidence_ref": evidence_ref,
                "key_id": key_id,
                "at": _iso8601(self._clock()),
            }
        )

    def issue(
        self,
        *,
        subject_id: str,
        subject_kind: str,
        tenant_id: str,
        domain_id: str,
        task_id: str,
        capabilities: Iterable[Mapping[str, Any]],
        policy_decision_ref: str,
        governing_spec_ref: str,
        ttl_seconds: int = 300,
        secret_provider_refs: Iterable[str] = (),
        correlation_id: str = "",
        evidence_ref: str = "",
    ) -> str:
        if subject_kind not in SUBJECT_KINDS:
            raise LeaseDenied("unsupported subject kind")
        for label, value in {
            "subject_id": subject_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "task_id": task_id,
            "policy_decision_ref": policy_decision_ref,
            "governing_spec_ref": governing_spec_ref,
        }.items():
            if not isinstance(value, str) or not value.strip():
                raise LeaseDenied(f"{label} is required")
        if ttl_seconds <= 0 or ttl_seconds > self.max_ttl_seconds:
            raise LeaseDenied("lease TTL exceeds the short-lived authority boundary")

        issued_at = self._clock().astimezone(timezone.utc)
        expires_at = issued_at + timedelta(seconds=ttl_seconds)
        lease_id = "lease_" + secrets.token_urlsafe(18)
        nonce = self._new_nonce()
        capability_list = self._validate_capabilities(capabilities)
        provider_refs = self._validate_secret_provider_refs(secret_provider_refs)

        payload: dict[str, Any] = {
            "lease_id": lease_id,
            "subject": {"id": subject_id, "kind": subject_kind},
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "task_id": task_id,
            "capabilities": capability_list,
            "issued_at": _iso8601(issued_at),
            "expires_at": _iso8601(expires_at),
            "nonce": nonce,
            "policy_decision_ref": policy_decision_ref,
            "governing_spec_ref": governing_spec_ref,
            "secret_provider_refs": provider_refs,
            "audit": {
                "correlation_id": correlation_id or f"corr:{lease_id}",
                "evidence_ref": evidence_ref or f"evidence:{lease_id}",
            },
        }
        token = self._encode(payload)
        self._record_audit(
            event="lease-issued",
            outcome="allow",
            reason="short-lived scoped lease issued",
            lease=payload,
            correlation_id=payload["audit"]["correlation_id"],
            evidence_ref=payload["audit"]["evidence_ref"],
            key_id=self.key_ring.active_key_id,
        )
        return token

    def _encode(self, payload: Mapping[str, Any]) -> str:
        header = {
            "alg": TOKEN_ALG,
            "typ": TOKEN_TYPE,
            "kid": self.key_ring.active_key_id,
            "iss": self.issuer,
        }
        encoded_header = _b64encode(_canonical_json(header))
        encoded_payload = _b64encode(_canonical_json(payload))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = self.key_ring.sign(self.key_ring.active_key_id, signing_input)
        return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}"

    def verify(self, token: str) -> tuple[dict[str, Any], str]:
        if not isinstance(token, str) or len(token) > 32_768:
            raise LeaseSignatureError("invalid lease token")
        parts = token.split(".")
        if len(parts) != 3:
            raise LeaseSignatureError("invalid compact lease token")
        encoded_header, encoded_payload, encoded_signature = parts
        try:
            header = json.loads(_b64decode(encoded_header))
            payload = json.loads(_b64decode(encoded_payload))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise LeaseSignatureError("lease token JSON is invalid") from exc
        if not isinstance(header, dict) or not isinstance(payload, dict):
            raise LeaseSignatureError("lease token envelope is invalid")
        if header.get("alg") != TOKEN_ALG or header.get("typ") != TOKEN_TYPE:
            raise LeaseSignatureError("unsupported lease token algorithm/type")
        if header.get("iss") != self.issuer:
            raise LeaseSignatureError("lease issuer mismatch")
        key_id = header.get("kid")
        if not isinstance(key_id, str) or not key_id:
            raise LeaseSignatureError("lease key id is missing")
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = _b64decode(encoded_signature)
        if not self.key_ring.verify(key_id, signing_input, signature):
            raise LeaseSignatureError("lease signature verification failed")

        issued_at = _parse_time(payload.get("issued_at"), "issued_at")
        expires_at = _parse_time(payload.get("expires_at"), "expires_at")
        now = self._clock().astimezone(timezone.utc)
        ttl = (expires_at - issued_at).total_seconds()
        if ttl <= 0 or ttl > self.max_ttl_seconds:
            raise LeaseDenied("lease lifetime violates short-lived authority policy")
        if now < issued_at:
            raise LeaseDenied("lease is not active yet")
        if now >= expires_at:
            raise LeaseExpired("lease expired")

        lease_id = payload.get("lease_id")
        if not isinstance(lease_id, str) or not lease_id:
            raise LeaseDenied("lease identity is missing")
        if lease_id in self._revocations:
            raise LeaseRevoked("lease revoked")
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or len(nonce) < 8:
            raise LeaseDenied("lease nonce is missing")
        return payload, key_id

    def authorize(
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
    ) -> AuthorizationDecision:
        lease: dict[str, Any] | None = None
        key_id = ""
        try:
            lease, key_id = self.verify(token)
            expected = {
                "tenant_id": tenant_id,
                "domain_id": domain_id,
                "task_id": task_id,
            }
            for field_name, value in expected.items():
                if lease.get(field_name) != value:
                    raise LeaseDenied(f"{field_name} scope mismatch")

            admitted = any(
                item.get("name") == capability
                and item.get("resource_scope") == resource_scope
                for item in lease.get("capabilities", [])
                if isinstance(item, dict)
            )
            if not admitted:
                raise LeaseDenied("capability/resource scope denied")
            if not isinstance(operation_nonce, str) or len(operation_nonce) < 8:
                raise LeaseDenied("operation nonce is required")

            replay_key = (lease["lease_id"], operation_nonce)
            if replay_key in self._operation_nonces:
                raise LeaseReplay("operation nonce replay detected")
            self._operation_nonces.add(replay_key)

            audit = lease.get("audit", {})
            evidence_ref = audit.get("evidence_ref", "") if isinstance(audit, dict) else ""
            self._record_audit(
                event="capability-used",
                outcome="allow",
                reason="lease and exact resource scope admitted",
                lease=lease,
                capability=capability,
                resource_scope=resource_scope,
                correlation_id=correlation_id,
                evidence_ref=evidence_ref,
                key_id=key_id,
            )
            subject = lease["subject"]
            return AuthorizationDecision(
                lease_id=lease["lease_id"],
                subject_id=subject["id"],
                subject_kind=subject["kind"],
                tenant_id=tenant_id,
                domain_id=domain_id,
                task_id=task_id,
                capability=capability,
                resource_scope=resource_scope,
                correlation_id=correlation_id,
                key_id=key_id,
            )
        except LeaseError as exc:
            self._record_audit(
                event="capability-used",
                outcome="deny",
                reason=type(exc).__name__,
                lease=lease,
                capability=capability,
                resource_scope=resource_scope,
                correlation_id=correlation_id,
                key_id=key_id,
            )
            raise

    def revoke(self, token_or_lease_id: str, *, reason: str, evidence_ref: str) -> str:
        if not reason.strip() or not evidence_ref.strip():
            raise LeaseDenied("revocation requires reason and evidence reference")
        lease: dict[str, Any] | None = None
        key_id = ""
        lease_id = token_or_lease_id
        if "." in token_or_lease_id:
            lease, key_id = self.verify(token_or_lease_id)
            lease_id = lease["lease_id"]
        self._revocations[lease_id] = {
            "reason": reason,
            "evidence_ref": evidence_ref,
            "revoked_at": _iso8601(self._clock()),
        }
        self._record_audit(
            event="lease-revoked",
            outcome="allow",
            reason=reason,
            lease=lease or {"lease_id": lease_id},
            evidence_ref=evidence_ref,
            key_id=key_id,
        )
        return lease_id

    def audit_events(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(event) for event in self._audit_log)
