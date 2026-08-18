from __future__ import annotations

from kopano.swfus_engine import SwfusHierarchy, SwfusPayload


def test_crud_progression_is_revisioned_and_delete_is_a_tombstone():
    engine = SwfusHierarchy()

    created = engine.execute_with_receipt(
        SwfusPayload(
            node_id="province-context",
            action_type="CREATE",
            telemetry_value=20,
            data={"province": "western-cape"},
            correlation_id="corr-create",
        )
    )
    assert created.accepted is True
    assert created.sync_state == "pending_sync"
    assert created.revision == 1
    assert engine.read("province-context") is not None

    updated = engine.execute_with_receipt(
        SwfusPayload(
            node_id="province-context",
            action_type="UPDATE",
            telemetry_value=21,
            expected_revision=1,
            data={"province": "gauteng"},
            correlation_id="corr-update",
        )
    )
    assert updated.accepted is True
    assert updated.revision == 2
    assert engine.read("province-context").data["province"] == "gauteng"

    deleted = engine.execute_with_receipt(
        SwfusPayload(
            node_id="province-context",
            action_type="DELETE",
            telemetry_value=0,
            expected_revision=2,
        )
    )
    assert deleted.accepted is True
    assert deleted.revision == 3
    assert engine.read("province-context") is None
    assert engine.local_offline_db["province-context"].tombstoned is True


def test_read_is_side_effect_free_and_sync_not_applicable():
    sync_calls = []

    def sync_adapter(record, receipt):
        sync_calls.append((record.node_id, receipt.resolved_action))
        return True

    engine = SwfusHierarchy(sync_adapter=sync_adapter)
    engine.execute_with_receipt(
        SwfusPayload(
            node_id="read-safe",
            action_type="CREATE",
            data={"state": "current"},
            correlation_id="create-read-safe",
        )
    )
    sync_calls.clear()
    before = engine.read("read-safe")

    receipt = engine.execute_with_receipt(
        SwfusPayload(
            node_id="read-safe",
            action_type="READ",
            correlation_id="read-001",
        )
    )

    assert receipt.accepted is True
    assert receipt.sync_state == "not_applicable"
    assert receipt.revision == 1
    assert engine.read("read-safe") == before
    assert sync_calls == []


def test_revision_conflict_is_severed_without_rewriting_witnessed_state():
    engine = SwfusHierarchy()
    engine.execute_with_receipt(
        SwfusPayload(
            node_id="profile",
            action_type="CREATE",
            data={"tier": "mobile"},
        )
    )

    rejected = engine.execute_with_receipt(
        SwfusPayload(
            node_id="profile",
            action_type="UPDATE",
            expected_revision=99,
            data={"tier": "immersive"},
        )
    )

    assert rejected.accepted is False
    assert rejected.sync_state == "severed"
    assert "revision conflict" in (rejected.reason or "")
    assert engine.read("profile").revision == 1
    assert engine.read("profile").data["tier"] == "mobile"
    assert engine.quarantine_ledger[-1] == rejected


def test_untrusted_payload_is_quarantined_and_prior_state_is_preserved():
    engine = SwfusHierarchy()
    engine.execute_with_receipt(
        SwfusPayload(
            node_id="locality",
            action_type="CREATE",
            data={"province": "limpopo"},
        )
    )

    rejected = engine.execute_with_receipt(
        SwfusPayload(
            node_id="locality",
            action_type="UPDATE",
            is_hallucinated=True,
            data={"province": "unknown"},
        )
    )

    assert rejected.accepted is False
    assert engine.read("locality").data["province"] == "limpopo"


def test_transport_failure_keeps_local_truth_pending_instead_of_severing():
    engine = SwfusHierarchy(sync_adapter=lambda _record, _receipt: False)

    receipt = engine.execute_with_receipt(
        SwfusPayload(
            node_id="offline-update",
            action_type="CREATE",
            data={"state": "queued"},
        )
    )

    assert receipt.accepted is True
    assert receipt.sync_state == "pending_sync"
    assert engine.read("offline-update") is not None
    assert engine.quarantine_ledger == []


def test_sync_success_is_only_claimed_when_adapter_observes_success():
    engine = SwfusHierarchy(sync_adapter=lambda _record, _receipt: True)

    receipt = engine.execute_with_receipt(
        SwfusPayload(
            node_id="synced-update",
            action_type="CREATE",
            data={"state": "accepted"},
            capability_lease_id="lease-123",
        )
    )

    assert receipt.accepted is True
    assert receipt.sync_state == "synced"
    assert receipt.capability_lease_id == "lease-123"


def test_same_correlation_retry_returns_original_receipt_without_double_mutation():
    engine = SwfusHierarchy(sync_adapter=lambda _record, _receipt: True)
    payload = SwfusPayload(
        node_id="retry-safe",
        action_type="CREATE",
        data={"province": "western-cape"},
        correlation_id="retry-001",
    )

    first = engine.execute_with_receipt(payload)
    retry = engine.execute_with_receipt(payload)

    assert first.accepted is True
    assert first.sync_state == "synced"
    assert retry == first
    assert engine.read("retry-safe").revision == 1
    assert len(engine.receipt_ledger) == 1


def test_correlation_id_reuse_for_different_payload_is_severed_without_mutation():
    engine = SwfusHierarchy()
    first = engine.execute_with_receipt(
        SwfusPayload(
            node_id="correlation-guard",
            action_type="CREATE",
            data={"province": "western-cape"},
            correlation_id="same-correlation",
        )
    )
    rejected = engine.execute_with_receipt(
        SwfusPayload(
            node_id="correlation-guard",
            action_type="UPDATE",
            expected_revision=1,
            data={"province": "gauteng"},
            correlation_id="same-correlation",
        )
    )

    assert first.accepted is True
    assert rejected.accepted is False
    assert "cannot be reused" in (rejected.reason or "")
    assert engine.read("correlation-guard").revision == 1
    assert engine.read("correlation-guard").data["province"] == "western-cape"


def test_legacy_telemetry_ingestion_maps_to_create_then_update():
    engine = SwfusHierarchy()

    first = engine.execute_with_receipt(
        SwfusPayload(
            node_id="legacy-node",
            action_type="TELEMETRY_INGESTION",
            telemetry_value=10,
        )
    )
    second = engine.execute_with_receipt(
        SwfusPayload(
            node_id="legacy-node",
            action_type="TELEMETRY_INGESTION",
            telemetry_value=11,
        )
    )

    assert first.resolved_action == "CREATE"
    assert second.resolved_action == "UPDATE"
    assert second.revision == 2
    assert engine.execute(
        SwfusPayload(
            node_id="another-node",
            action_type="TELEMETRY_INGESTION",
            telemetry_value=1,
        )
    ) is True
