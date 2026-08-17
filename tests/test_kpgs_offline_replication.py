from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "governance"
    / "kpgs-vnext"
    / "offline-replication"
    / "replication_contract.py"
)
SPEC = importlib.util.spec_from_file_location("kpgs_offline_replication", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)

AUTHORITY_EFFECT = module.AUTHORITY_EFFECT
AuthorityViolation = module.AuthorityViolation
CanonicalAuthorityStore = module.CanonicalAuthorityStore
IntegrityError = module.IntegrityError
LocalReplica = module.LocalReplica
PeerAuthorizationError = module.PeerAuthorizationError
canonical_sha256 = module.canonical_sha256
request_authority_promotion = module.request_authority_promotion


def _pair():
    alice = LocalReplica(
        document_id="doc:kasilink-neighbourhood-view",
        replica_id="device-a",
        principal_id="principal:alice",
        trusted_peers={"device-b": "principal:bob"},
    )
    bob = LocalReplica(
        document_id="doc:kasilink-neighbourhood-view",
        replica_id="device-b",
        principal_id="principal:bob",
        trusted_peers={"device-a": "principal:alice"},
    )
    return alice, bob


def test_partitioned_peers_converge_after_concurrent_updates():
    alice, bob = _pair()

    alice.local_set("nearby_gigs", ["electrician", "tutor"])
    bob.local_set("network_hint", "offline")
    alice.local_set("shared_banner", "from-a")
    bob.local_set("shared_banner", "from-b")

    assert alice.snapshot() != bob.snapshot()

    alice_batch = alice.export_batch()
    bob_batch = bob.export_batch()
    alice.import_batch(bob_batch)
    bob.import_batch(alice_batch)

    assert alice.snapshot() == bob.snapshot()
    assert alice.state_hash == bob.state_hash
    # Same Lamport counter: deterministic replica-id tie-break, not arrival order.
    assert alice.snapshot()["shared_banner"] == "from-b"


def test_duplicate_and_reordered_delivery_are_idempotent():
    alice, bob = _pair()
    alice.local_set("status", "ready")
    batch = alice.export_batch()

    assert bob.import_batch(batch) == 1
    first_hash = bob.state_hash
    assert bob.import_batch(batch) == 0
    assert bob.state_hash == first_hash
    assert bob.operation_count == 1


def test_untrusted_peer_is_rejected_before_projection():
    receiver = LocalReplica(
        document_id="doc:kasilink-neighbourhood-view",
        replica_id="device-a",
        principal_id="principal:alice",
    )
    sender = LocalReplica(
        document_id="doc:kasilink-neighbourhood-view",
        replica_id="device-z",
        principal_id="principal:mallory",
    )
    sender.local_set("status", "owned")

    with pytest.raises(PeerAuthorizationError, match="not trusted"):
        receiver.import_batch(sender.export_batch())

    assert receiver.snapshot() == {}


def test_peer_principal_binding_is_enforced():
    alice, _ = _pair()
    impostor = LocalReplica(
        document_id=alice.document_id,
        replica_id="device-b",
        principal_id="principal:mallory",
    )
    impostor.local_set("status", "forged")

    with pytest.raises(PeerAuthorizationError, match="principal"):
        alice.import_batch(impostor.export_batch())


def test_batch_corruption_is_detected():
    alice, bob = _pair()
    alice.local_set("status", "ready")
    raw = json.loads(alice.export_batch().decode("utf-8"))
    raw["operations"][0]["value"] = "tampered"
    corrupted = json.dumps(raw, sort_keys=True).encode("utf-8")

    with pytest.raises(IntegrityError, match="batch hash mismatch"):
        bob.import_batch(corrupted)


def test_local_persistence_restores_replica_and_can_resync():
    alice, bob = _pair()
    alice.local_set("status", "offline")
    persisted = alice.dump_local()

    restored = LocalReplica.restore_local(persisted)
    assert restored.snapshot() == alice.snapshot()
    assert restored.state_hash == alice.state_hash

    bob.local_set("utility_notice", "water interruption")
    restored.import_batch(bob.export_batch())
    bob.import_batch(restored.export_batch())

    assert restored.snapshot() == bob.snapshot()


def test_replication_can_never_directly_mutate_canonical_authority():
    alice, _ = _pair()
    alice.local_set("status", "candidate")
    store = CanonicalAuthorityStore()

    with pytest.raises(AuthorityViolation, match="not authority"):
        store.apply_replica_snapshot(alice)


def test_promotion_requires_explicit_governing_task_receipt():
    alice, _ = _pair()
    alice.local_set("status", "candidate")

    with pytest.raises(AuthorityViolation, match="task receipt"):
        request_authority_promotion(alice, governing_task_receipt_ref="")

    proposal = request_authority_promotion(
        alice,
        governing_task_receipt_ref="kpgs-receipt://task/abc/r0002",
    )
    assert proposal.state_sha256 == alice.state_hash
    assert proposal.authority_effect == "proposal_only"


def test_authoritative_state_class_and_authority_effect_are_refused():
    alice, _ = _pair()

    with pytest.raises(AuthorityViolation, match="authoritative"):
        alice.local_set("status", "x", state_class="constitutional_truth")

    with pytest.raises(AuthorityViolation, match="carry authority"):
        module.ReplicaOperation(
            document_id=alice.document_id,
            actor_replica_id=alice.replica_id,
            actor_principal_id=alice.principal_id,
            counter=1,
            key="status",
            value="x",
            authority_effect="grant",
        )


def test_provenance_is_hash_only():
    alice, _ = _pair()
    source = {"private": "do-not-replicate"}
    operation = alice.local_set("status", "ready", provenance=source)

    wire_operation = json.loads(alice.export_batch().decode("utf-8"))["operations"][0]
    assert operation.provenance_sha256 == canonical_sha256(source)
    assert wire_operation["provenance_sha256"] == operation.provenance_sha256
    assert "private" not in wire_operation
    assert wire_operation["authority_effect"] == AUTHORITY_EFFECT
