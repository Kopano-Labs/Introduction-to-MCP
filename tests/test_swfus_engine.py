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
