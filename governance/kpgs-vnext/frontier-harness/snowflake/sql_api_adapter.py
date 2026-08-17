#!/usr/bin/env python3
"""Governed Snowflake SQL API adapter for KPGS Frontier Harness v0.2."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

GOVERNING_SPEC = "kpgs-frontier-harness-snowflake-v0.2"
REQUIRED_CAPABILITY = "snowflake.telemetry.append"
RESOURCE_SCOPE = "KPGS_FRONTIER.EVIDENCE.FRONTIER_TELEMETRY"
ALLOWED_TOKEN_TYPES = {"OAUTH", "KEYPAIR_JWT", "PROGRAMMATIC_ACCESS_TOKEN"}
FORBIDDEN_TELEMETRY_KEYS = {"semantic_input", "private_payload", "raw_input", "provider_output", "prompt", "response_text"}
ACCOUNT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
INSERT_SQL = """INSERT INTO KPGS_FRONTIER.EVIDENCE.FRONTIER_TELEMETRY
  (EVENT_SCHEMA, REQUEST_ID, SOURCE_PROVIDER, CAPABILITY, SELECTED_PROVIDER,
   OUTPUT_DIGEST, DATA_CLASSIFICATION, EXTERNAL_PROCESSING_ALLOWED)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""


class GovernanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class SnowflakeTarget:
    account_identifier: str
    warehouse: str
    role: str
    database: str = "KPGS_FRONTIER"
    schema: str = "EVIDENCE"

    def endpoint(self) -> str:
        if not ACCOUNT_RE.fullmatch(self.account_identifier):
            raise GovernanceError("invalid Snowflake account identifier")
        return f"https://{self.account_identifier}.snowflakecomputing.com/api/v2/statements"


@dataclass(frozen=True)
class PreparedInsert:
    request_id: str
    endpoint: str
    body: dict[str, Any]
    token_type: str
    secret_ref: str

    def safe_receipt(self) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.snowflake_request_receipt.v1",
            "request_id": self.request_id,
            "endpoint": self.endpoint,
            "binding_count": len(self.body["bindings"]),
            "token_type": self.token_type,
            "secret_ref": self.secret_ref,
            "contains_secret": False,
        }


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise GovernanceError("lease timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


def validate_lease(lease: dict[str, Any], *, now: datetime | None = None) -> None:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if lease.get("governing_spec_ref") != GOVERNING_SPEC:
        raise GovernanceError("lease is not bound to the Snowflake v0.2 governing spec")
    subject = lease.get("subject") or {}
    if subject.get("kind") not in {"adapter", "service", "renter"}:
        raise GovernanceError("Snowflake capability must be leased to an adapter/service/renter")
    capabilities = lease.get("capabilities") or []
    permitted = any(
        item.get("name") == REQUIRED_CAPABILITY and item.get("resource_scope") == RESOURCE_SCOPE
        for item in capabilities
    )
    if not permitted:
        raise GovernanceError("lease does not permit governed Snowflake telemetry append")
    issued = _parse_time(str(lease.get("issued_at", "")))
    expires = _parse_time(str(lease.get("expires_at", "")))
    if not (issued <= current < expires):
        raise GovernanceError("capability lease is not currently valid")
    secret_refs = lease.get("secret_provider_refs") or []
    if len(secret_refs) != 1 or not str(secret_refs[0]).startswith("env://"):
        raise GovernanceError("v0.2 requires exactly one env:// external secret reference")


def resolve_env_secret(secret_ref: str, env: dict[str, str] | None = None) -> str:
    name = secret_ref.removeprefix("env://")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", name):
        raise GovernanceError("invalid env secret reference")
    source = env if env is not None else os.environ
    token = source.get(name)
    if not token:
        raise GovernanceError(f"secret provider did not resolve {secret_ref}")
    return token


def _binding(value: Any) -> dict[str, str]:
    if isinstance(value, bool):
        return {"type": "BOOLEAN", "value": "true" if value else "false"}
    return {"type": "TEXT", "value": str(value)}


def prepare_telemetry_insert(row: dict[str, Any], lease: dict[str, Any], target: SnowflakeTarget, *, token_type: str = "PROGRAMMATIC_ACCESS_TOKEN", now: datetime | None = None) -> PreparedInsert:
    validate_lease(lease, now=now)
    if token_type not in ALLOWED_TOKEN_TYPES:
        raise GovernanceError("unsupported Snowflake token type")
    leaked = FORBIDDEN_TELEMETRY_KEYS.intersection(row)
    if leaked:
        raise GovernanceError(f"forbidden semantic/private fields in telemetry row: {sorted(leaked)}")
    columns = ["event_schema", "request_id", "source_provider", "capability", "selected_provider", "output_digest", "data_classification", "external_processing_allowed"]
    missing = [name for name in columns if name not in row]
    if missing:
        raise GovernanceError(f"telemetry row missing required fields: {missing}")
    if row["event_schema"] != "kpgs.frontier_telemetry.v1":
        raise GovernanceError("unexpected telemetry schema")
    bindings = {str(i): _binding(row[name]) for i, name in enumerate(columns, start=1)}
    body = {
        "statement": INSERT_SQL,
        "timeout": 20,
        "database": target.database,
        "schema": target.schema,
        "warehouse": target.warehouse,
        "role": target.role,
        "bindings": bindings,
        "parameters": {"QUERY_TAG": f"kpgs-frontier:{row['request_id']}"},
    }
    return PreparedInsert(str(row["request_id"]), target.endpoint(), body, token_type, str(lease["secret_provider_refs"][0]))


def submit_prepared(prepared: PreparedInsert, *, secret_resolver: Callable[[str], str] = resolve_env_secret, opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    token = secret_resolver(prepared.secret_ref)
    url = f"{prepared.endpoint}?requestId={urllib.parse.quote(prepared.request_id, safe='')}"
    payload = json.dumps(prepared.body, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "KPGS-Frontier-Harness/0.2",
        "X-Snowflake-Authorization-Token-Type": prepared.token_type,
    })
    try:
        with opener(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw) if raw else {}
            return {"schema_version": "kpgs.snowflake_execution_receipt.v1", "request_id": prepared.request_id, "http_status": getattr(response, "status", 200), "statement_handle": result.get("statementHandle"), "code": result.get("code"), "message": result.get("message"), "contains_secret": False}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {"message": raw[:500]}
        return {"schema_version": "kpgs.snowflake_execution_receipt.v1", "request_id": prepared.request_id, "http_status": exc.code, "statement_handle": detail.get("statementHandle"), "code": detail.get("code"), "message": detail.get("message"), "contains_secret": False}
