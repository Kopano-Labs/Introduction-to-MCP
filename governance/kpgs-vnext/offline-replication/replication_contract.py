from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


SCHEMA_VERSION = "kpgs.replica.v0.1"
AUTHORITY_EFFECT = "none"
NON_AUTHORITATIVE_CLASSES = frozenset(
    {"non_authoritative", "derived_projection", "pending_proposal"}
)


class ReplicationError(ValueError):
    pass


class IntegrityError(ReplicationError):
    pass


class PeerAuthorizationError(ReplicationError):
    pass


class AuthorityViolation(ReplicationError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class ReplicaOperation:
    document_id: str
    actor_replica_id: str
    actor_principal_id: str
    counter: int
    key: str
    value: Any
    state_class: str = "non_authoritative"
    authority_effect: str = AUTHORITY_EFFECT
    provenance_sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ReplicationError("document_id is required")
        if not self.actor_replica_id.strip():
            raise ReplicationError("actor_replica_id is required")
        if not self.actor_principal_id.strip():
            raise ReplicationError("actor_principal_id is required")
        if self.counter < 1:
            raise ReplicationError("counter must be >= 1")
        if not self.key.strip():
            raise ReplicationError("key is required")
        if self.state_class not in NON_AUTHORITATIVE_CLASSES:
            raise AuthorityViolation("replicated state class cannot be authoritative")
        if self.authority_effect != AUTHORITY_EFFECT:
            raise AuthorityViolation("replicated operation cannot carry authority")
        if self.provenance_sha256 is not None and (
            len(self.provenance_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.provenance_sha256)
        ):
            raise IntegrityError("provenance_sha256 must be lowercase SHA-256 hex")

    @property
    def op_id(self) -> str:
        return f"{self.actor_replica_id}:{self.counter}"

    @property
    def order_key(self) -> tuple[int, str, str]:
        """Total order used by the LWW-register projection.

        Counter is the Lamport component. Replica and operation IDs break ties
        deterministically; transport arrival order never participates.
        """
        return (self.counter, self.actor_replica_id, self.op_id)

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "document_id": self.document_id,
            "actor_replica_id": self.actor_replica_id,
            "actor_principal_id": self.actor_principal_id,
            "counter": self.counter,
            "key": self.key,
            "value": self.value,
            "state_class": self.state_class,
            "authority_effect": self.authority_effect,
            "provenance_sha256": self.provenance_sha256,
        }

    @property
    def sha256(self) -> str:
        return canonical_sha256(self.unsigned_payload())

    def to_wire(self) -> dict[str, Any]:
        return {
            **self.unsigned_payload(),
            "op_id": self.op_id,
            "sha256": self.sha256,
        }

    @classmethod
    def from_wire(cls, raw: Mapping[str, Any]) -> "ReplicaOperation":
        required = {
            "schema_version",
            "document_id",
            "actor_replica_id",
            "actor_principal_id",
            "counter",
            "key",
            "value",
            "state_class",
            "authority_effect",
            "provenance_sha256",
            "op_id",
            "sha256",
        }
        missing = required.difference(raw)
        if missing:
            raise IntegrityError(f"wire operation missing fields: {sorted(missing)}")
        if raw["schema_version"] != SCHEMA_VERSION:
            raise IntegrityError("unsupported replica schema version")
        operation = cls(
            document_id=str(raw["document_id"]),
            actor_replica_id=str(raw["actor_replica_id"]),
            actor_principal_id=str(raw["actor_principal_id"]),
            counter=int(raw["counter"]),
            key=str(raw["key"]),
            value=raw["value"],
            state_class=str(raw["state_class"]),
            authority_effect=str(raw["authority_effect"]),
            provenance_sha256=raw["provenance_sha256"],
        )
        if raw["op_id"] != operation.op_id:
            raise IntegrityError("operation id does not match canonical identity")
        if raw["sha256"] != operation.sha256:
            raise IntegrityError("operation hash does not match canonical payload")
        return operation


@dataclass(frozen=True)
class ReplicaBatch:
    document_id: str
    sender_replica_id: str
    operations: tuple[ReplicaOperation, ...]

    def to_wire(self) -> bytes:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "document_id": self.document_id,
            "sender_replica_id": self.sender_replica_id,
            "authority_effect": AUTHORITY_EFFECT,
            "operations": [operation.to_wire() for operation in self.operations],
        }
        envelope = {
            **payload,
            "batch_sha256": canonical_sha256(payload),
        }
        return canonical_json_bytes(envelope)

    @classmethod
    def from_wire(cls, wire: bytes) -> "ReplicaBatch":
        try:
            raw = json.loads(wire.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IntegrityError("replica batch is not valid UTF-8 JSON") from exc
        expected_hash = raw.pop("batch_sha256", None)
        if expected_hash is None or expected_hash != canonical_sha256(raw):
            raise IntegrityError("replica batch hash mismatch")
        if raw.get("schema_version") != SCHEMA_VERSION:
            raise IntegrityError("unsupported batch schema version")
        if raw.get("authority_effect") != AUTHORITY_EFFECT:
            raise AuthorityViolation("replica batch cannot carry authority")
        operations = tuple(
            ReplicaOperation.from_wire(item) for item in raw.get("operations", [])
        )
        document_id = str(raw.get("document_id", ""))
        if any(operation.document_id != document_id for operation in operations):
            raise IntegrityError("batch contains an operation for another document")
        return cls(
            document_id=document_id,
            sender_replica_id=str(raw.get("sender_replica_id", "")),
            operations=operations,
        )


class LocalReplica:
    """Transport-agnostic LWW-map CRDT POC for non-authoritative state.

    Operations form a grow-only set keyed by op_id. The visible document is a
    deterministic projection selecting the highest Lamport/actor tuple for each
    key. Merge is set union, so duplicate/reordered delivery is harmless.

    This class deliberately does not mutate a KPGS canonical authority store.
    """

    def __init__(
        self,
        *,
        document_id: str,
        replica_id: str,
        principal_id: str,
        trusted_peers: Mapping[str, str] | None = None,
    ) -> None:
        if not document_id.strip() or not replica_id.strip() or not principal_id.strip():
            raise ReplicationError("document_id, replica_id and principal_id are required")
        self.document_id = document_id
        self.replica_id = replica_id
        self.principal_id = principal_id
        self.trusted_peers = dict(trusted_peers or {})
        self._operations: dict[str, ReplicaOperation] = {}
        self._counter = 0

    @property
    def operation_count(self) -> int:
        return len(self._operations)

    @property
    def state_hash(self) -> str:
        return canonical_sha256(self.snapshot())

    def local_set(
        self,
        key: str,
        value: Any,
        *,
        state_class: str = "non_authoritative",
        provenance: Any | None = None,
    ) -> ReplicaOperation:
        self._counter += 1
        operation = ReplicaOperation(
            document_id=self.document_id,
            actor_replica_id=self.replica_id,
            actor_principal_id=self.principal_id,
            counter=self._counter,
            key=key,
            value=value,
            state_class=state_class,
            authority_effect=AUTHORITY_EFFECT,
            provenance_sha256=(
                canonical_sha256(provenance) if provenance is not None else None
            ),
        )
        self._operations[operation.op_id] = operation
        return operation

    def snapshot(self) -> dict[str, Any]:
        winners: dict[str, ReplicaOperation] = {}
        for operation in self._operations.values():
            current = winners.get(operation.key)
            if current is None or operation.order_key > current.order_key:
                winners[operation.key] = operation
        return {
            key: winners[key].value
            for key in sorted(winners)
        }

    def export_batch(self) -> bytes:
        batch = ReplicaBatch(
            document_id=self.document_id,
            sender_replica_id=self.replica_id,
            operations=tuple(
                sorted(
                    (
                        operation
                        for operation in self._operations.values()
                        if operation.actor_replica_id == self.replica_id
                    ),
                    key=lambda operation: operation.op_id,
                )
            ),
        )
        return batch.to_wire()

    def import_batch(self, wire: bytes) -> int:
        batch = ReplicaBatch.from_wire(wire)
        if batch.document_id != self.document_id:
            raise IntegrityError("replica batch document does not match local document")
        expected_principal = self.trusted_peers.get(batch.sender_replica_id)
        if expected_principal is None:
            raise PeerAuthorizationError("sender replica is not trusted")
        for operation in batch.operations:
            if operation.actor_replica_id != batch.sender_replica_id:
                raise PeerAuthorizationError(
                    "forwarded operations are not accepted in v0.1 peer batches"
                )
            if operation.actor_principal_id != expected_principal:
                raise PeerAuthorizationError(
                    "operation principal does not match trusted peer binding"
                )
        before = len(self._operations)
        for operation in batch.operations:
            existing = self._operations.get(operation.op_id)
            if existing is not None and existing.sha256 != operation.sha256:
                raise IntegrityError("operation id collision with different payload")
            self._operations[operation.op_id] = operation
            self._counter = max(self._counter, operation.counter)
        return len(self._operations) - before

    def dump_local(self) -> bytes:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "document_id": self.document_id,
            "replica_id": self.replica_id,
            "principal_id": self.principal_id,
            "trusted_peers": self.trusted_peers,
            "counter": self._counter,
            "authority_effect": AUTHORITY_EFFECT,
            "operations": [
                operation.to_wire()
                for operation in sorted(
                    self._operations.values(), key=lambda item: item.op_id
                )
            ],
        }
        envelope = {**payload, "local_sha256": canonical_sha256(payload)}
        return canonical_json_bytes(envelope)

    @classmethod
    def restore_local(cls, wire: bytes) -> "LocalReplica":
        try:
            raw = json.loads(wire.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IntegrityError("local replica state is not valid UTF-8 JSON") from exc
        expected_hash = raw.pop("local_sha256", None)
        if expected_hash is None or expected_hash != canonical_sha256(raw):
            raise IntegrityError("local replica state hash mismatch")
        if raw.get("schema_version") != SCHEMA_VERSION:
            raise IntegrityError("unsupported local replica schema version")
        if raw.get("authority_effect") != AUTHORITY_EFFECT:
            raise AuthorityViolation("restored replica state cannot carry authority")
        replica = cls(
            document_id=str(raw["document_id"]),
            replica_id=str(raw["replica_id"]),
            principal_id=str(raw["principal_id"]),
            trusted_peers=raw.get("trusted_peers", {}),
        )
        operations = [
            ReplicaOperation.from_wire(item) for item in raw.get("operations", [])
        ]
        if any(operation.document_id != replica.document_id for operation in operations):
            raise IntegrityError("local state contains another document")
        for operation in operations:
            replica._operations[operation.op_id] = operation
        replica._counter = max(
            int(raw.get("counter", 0)),
            max((operation.counter for operation in operations), default=0),
        )
        return replica


@dataclass(frozen=True)
class PromotionProposal:
    document_id: str
    state_sha256: str
    governing_task_receipt_ref: str
    authority_effect: str = "proposal_only"


def request_authority_promotion(
    replica: LocalReplica,
    *,
    governing_task_receipt_ref: str,
) -> PromotionProposal:
    """Create a promotion proposal; never mutate canonical authority directly."""
    if not governing_task_receipt_ref.strip():
        raise AuthorityViolation(
            "replicated state requires a governing task receipt before promotion"
        )
    return PromotionProposal(
        document_id=replica.document_id,
        state_sha256=replica.state_hash,
        governing_task_receipt_ref=governing_task_receipt_ref,
    )


class CanonicalAuthorityStore:
    """Guard rail proving replicated state cannot self-promote in this POC."""

    def apply_replica_snapshot(self, _replica: LocalReplica) -> None:
        raise AuthorityViolation(
            "replica convergence is not authority; submit a governed promotion proposal"
        )
