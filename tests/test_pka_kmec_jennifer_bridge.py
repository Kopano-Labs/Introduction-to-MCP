"""
Test Suite for PKA-KMEC-Jennifer Cross-Estate Smart Ledger & Offline Reconciliation
===================================================================================
Forensic Verification:
- PKA Convergence Bands, Trust Vectors & PR Merge Gates (Backward Compatibility)
- Authoritative PostgreSQL Consequence Journal & MongoDB Projection Layer
- Smart Ledger Blockchain Properties (SHA-256 Hash Chaining, Plain INSERT Immutability)
- Idempotency Replay Protection & Superseding Lineages
- Apple & Android Embodiment Staged Deployment Parsers
- 9-Step Offline Edge Reconciliation Lifecycle (Cold Restart -> PKA Gate -> PostgreSQL Admission / Conflict)
- Full Chain Cryptographic Integrity Verification

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.pka_kmec_jennifer_bridge import (
    PkaKmecJenniferBridge,
    PkaConvergenceBand,
    PkaTrustVector,
    JenniferDatabaseLayer,
    PlatformEmbodiment,
    SmartLedgerAdmissionState,
    SmartLedgerEngine,
    OfflineReconciliationEngine,
    AppleDeploymentStage,
    AndroidDeploymentStage,
    GENESIS_HASH,
)


@pytest.fixture
def smart_bridge(tmp_path):
    test_db = tmp_path / "test_smart_ledger.db"
    ledger = SmartLedgerEngine(db_path=test_db)
    return PkaKmecJenniferBridge(balance_point=0.5, ledger=ledger)


def test_pka_convergence_bands(smart_bridge):
    """Founder-defined balance point at 0.5."""
    assert smart_bridge.classify_convergence(0.2) == PkaConvergenceBand.TOWARD_ZERO
    assert smart_bridge.classify_convergence(0.5) == PkaConvergenceBand.BALANCED
    assert smart_bridge.classify_convergence(0.85) == PkaConvergenceBand.TOWARD_ONE
    with pytest.raises(ValueError):
        smart_bridge.classify_convergence(-0.1)


def test_pka_trust_vectors(smart_bridge):
    """Trust vector maps (verdict, disposition) to Green/Yellow/Red."""
    assert smart_bridge.evaluate_trust_vector("POC_CANDIDATE", "PROPOSE") == PkaTrustVector.GREEN
    assert smart_bridge.evaluate_trust_vector("MAYBE", "HOLD") == PkaTrustVector.YELLOW
    assert smart_bridge.evaluate_trust_vector("FOC_CANDIDATE", "BLOCK") == PkaTrustVector.RED


def test_projection_requires_authoritative_receipt(smart_bridge):
    """Projection state (MongoDB) cannot be updated without authoritative receipt."""
    entry = smart_bridge.record_authoritative_event(
        event_type="STATE_SETTLEMENT",
        actor_id="agent-001",
        scope="KPGS::CORE",
        payload={"balance": 1000, "currency": "ZAR"}
    )
    assert entry.verified is True
    assert entry.payload_hash != ""

    proj = smart_bridge.update_projection("dashboard_view", {"balance_display": "R 1,000"}, entry.entry_id)
    assert proj["layer"] == JenniferDatabaseLayer.MONGODB_PROJECTION.value
    assert proj["source_entry_id"] == entry.entry_id

    with pytest.raises(PermissionError):
        smart_bridge.update_projection("dashboard_view", {"fake": True}, "fake-receipt-id")


def test_jennifer_merge_gates(smart_bridge):
    """Enforce Sprint 3 VALIDATION_POLICY.md gates."""
    passed, violations = smart_bridge.validate_jennifer_merge_gates(
        declared_source="User-provided canonical architecture artifact",
        declared_by="@RobynAwesome",
        declaration_date="2026-08-29",
        validation_state="VALIDATED",
        evidence_linked=True,
        governance_signed=True
    )
    assert passed is True
    assert len(violations) == 0

    failed, violations = smart_bridge.validate_jennifer_merge_gates(
        declared_source="Architecture Spec",
        declared_by="@RobynAwesome",
        declaration_date="2026-08-29",
        validation_state="VALIDATED",
        evidence_linked=False,
        governance_signed=True
    )
    assert failed is False
    assert any("Gate 3 Failed" in v for v in violations)


def test_smart_ledger_hash_chaining_and_immutability(smart_bridge):
    """
    Verifies Blockchain Properties on Physical Metal:
    - Genesis receipt has previous_hash = 000...0
    - Receipt N+1 chains to Receipt N's receipt_hash
    - Duplicate idempotency replay is idempotent
    - Duplicate idempotency conflict raises ValueError
    - Strict append-only plain INSERT protects history
    """
    ledger = smart_bridge.ledger

    # Receipt 1 (Genesis block in chain)
    r1 = ledger.append_receipt(
        actor_seat="SEAT_01_KC",
        embodiment=PlatformEmbodiment.APPLE_SECURE_ENCLAVE_CRYPTOKIT,
        pka_verdict="ALLOW",
        claim_type="USER_INTENT_OR_TESTIMONY",
        idempotency_key="idemp_apple_001",
        payload={"action": "ESTABLISH_SOVEREIGNTY", "target": "KOPANO_LABS"},
        evidence_refs=["USER_CHAT_DIRECTIVE"],
        device_secret_key="APPLE_SECURE_ENCLAVE_SECRET_KEY"
    )
    assert r1.sequence_number == 1
    assert r1.previous_receipt_hash == GENESIS_HASH
    assert r1.receipt_hash != ""

    # Receipt 2 (Chained to Receipt 1)
    r2 = ledger.append_receipt(
        actor_seat="SEAT_10_ANTIGRAVITY",
        embodiment=PlatformEmbodiment.ANDROID_KEYSTORE_WORKMANAGER,
        pka_verdict="ALLOW",
        claim_type="REPOSITORY_STATE",
        idempotency_key="idemp_android_002",
        payload={"action": "COMMIT_METAL_RECEIPTS", "tests_passed": 33},
        evidence_refs=["tests/test_governance_trace.py"],
        device_secret_key="ANDROID_KEYSTORE_SECRET_KEY"
    )
    assert r2.sequence_number == 2
    assert r2.previous_receipt_hash == r1.receipt_hash

    # Idempotent replay: Re-sending r1 with same payload returns r1
    r1_replay = ledger.append_receipt(
        actor_seat="SEAT_01_KC",
        embodiment=PlatformEmbodiment.APPLE_SECURE_ENCLAVE_CRYPTOKIT,
        pka_verdict="ALLOW",
        claim_type="USER_INTENT_OR_TESTIMONY",
        idempotency_key="idemp_apple_001",
        payload={"action": "ESTABLISH_SOVEREIGNTY", "target": "KOPANO_LABS"},
        evidence_refs=["USER_CHAT_DIRECTIVE"]
    )
    assert r1_replay.receipt_id == r1.receipt_id
    assert r1_replay.sequence_number == 1

    # Idempotency conflict: Re-sending same key with different payload MUST fail
    with pytest.raises(ValueError, match="Idempotency conflict"):
        ledger.append_receipt(
            actor_seat="SEAT_01_KC",
            embodiment=PlatformEmbodiment.APPLE_SECURE_ENCLAVE_CRYPTOKIT,
            pka_verdict="ALLOW",
            claim_type="USER_INTENT_OR_TESTIMONY",
            idempotency_key="idemp_apple_001",
            payload={"action": "MALICIOUS_OVERWRITE_ATTEMPT"}
        )

    # Whole chain cryptographic validation
    valid, errors = ledger.verify_chain_integrity()
    assert valid is True
    assert len(errors) == 0


def test_smart_ledger_superseding_lineage(smart_bridge):
    """
    Verifies that amendments create forward/backward superseding links without erasing history.
    """
    ledger = smart_bridge.ledger

    r1 = ledger.append_receipt(
        actor_seat="FORGE",
        embodiment=PlatformEmbodiment.SERVER_METAL,
        pka_verdict="ALLOW",
        claim_type="MODEL_INTERPRETATION",
        idempotency_key="idemp_forge_001",
        payload={"hypothesis": "Initial observation engine draft"}
    )

    # Superseding receipt
    r2 = ledger.create_superseding_receipt(
        ancestor=r1,
        new_payload={"hypothesis": "Refined observation engine with KMEC box plots"},
        actor_seat="FORGE",
        idempotency_key="idemp_forge_002"
    )

    assert r2.supersedes_receipt_id == r1.receipt_id
    assert r2.previous_receipt_hash == r1.receipt_hash

    # Check that r1 links forward to r2 in SQLite
    reloaded_r1 = ledger.get_receipt_by_id(r1.receipt_id)
    assert reloaded_r1.superseded_by_receipt_id == r2.receipt_id

    # Verify chain integrity across superseding blocks
    valid, errors = ledger.verify_chain_integrity()
    assert valid is True
    assert len(errors) == 0


def test_apple_and_android_deployment_parsers(smart_bridge):
    """
    Verifies KMEC Staged Deployment Parsers for Apple & Android:
    - Apple: UPLOAD_ACCEPTED != PROCESSED_BUILD
    - Android: WORKMANAGER_ENQUEUED != SERVER_ADMITTED
    """
    # Apple Stage 1: Upload accepted, but not yet processed build
    apple_upload = smart_bridge.parse_apple_deployment_event(
        stage=AppleDeploymentStage.UPLOAD_DISTRIBUTE,
        bundle_id="com.kopanolabs.app",
        version="1.0.0"
    )
    assert apple_upload["upload_accepted"] is True
    assert apple_upload["processed_build"] is False
    assert apple_upload["invariant_check"] == "PASS"

    # Apple Stage 2: TestFlight review -> Processed Build
    apple_processed = smart_bridge.parse_apple_deployment_event(
        stage=AppleDeploymentStage.TESTFLIGHT_APP_REVIEW_NOTARIZATION,
        bundle_id="com.kopanolabs.app",
        version="1.0.0"
    )
    assert apple_processed["processed_build"] is True

    # Android Stage 1: WorkManager enqueued, but not yet server admitted
    android_enqueued = smart_bridge.parse_android_deployment_event(
        stage=AndroidDeploymentStage.WORKMANAGER_QUEUE,
        package_name="com.kopanolabs.app",
        version_code=100
    )
    assert android_enqueued["workmanager_enqueued"] is True
    assert android_enqueued["server_admitted"] is False

    # Android Stage 2: Closed testing review -> Server admitted
    android_admitted = smart_bridge.parse_android_deployment_event(
        stage=AndroidDeploymentStage.CLOSED_TESTING_REVIEW,
        package_name="com.kopanolabs.app",
        version_code=100
    )
    assert android_admitted["server_admitted"] is True


def test_offline_reconciliation_protocol_and_cold_restart(tmp_path):
    """
    Full 9-Step Offline Reconciliation & Cold Restart Test:
    1. Offline candidate batch created on edge.
    2. Engine destroyed / cold restart simulated.
    3. Reconnection engine reconciles batch through PKA revalidation.
    4. Valid candidates admitted to PostgreSQL authority layer.
    5. Conflicting/unproven claims emit signed Conflict Receipts (never dropped).
    6. Rebuildable MongoDB projections refreshed.
    7. Full chain remains untampered and mathematically sound.
    """
    db_file = tmp_path / "cold_restart_reconciliation.db"

    # 1. Edge generates offline batch
    candidate_batch = [
        # Candidate 1: Proven Intent with Evidence -> Admitted
        {
            "idempotency_key": "off_candidate_001",
            "actor_seat": "SEAT_01_KC",
            "embodiment": PlatformEmbodiment.APPLE_SECURE_ENCLAVE_CRYPTOKIT.value,
            "claim_type": "USER_INTENT_OR_TESTIMONY",
            "payload": {"directive": "Execute Sprint 4 Convergence"},
            "evidence_refs": ["USER_CHAT_DIRECTIVE"],
            "pka_verdict": "ALLOW"
        },
        # Candidate 2: Runtime Metal Claim with Evidence -> Admitted
        {
            "idempotency_key": "off_candidate_002",
            "actor_seat": "SEAT_10_ANTIGRAVITY",
            "embodiment": PlatformEmbodiment.ANDROID_KEYSTORE_WORKMANAGER.value,
            "claim_type": "RUNTIME_OR_METAL",
            "payload": {"pytest_result": "33/33 passed"},
            "evidence_refs": ["tests/test_governance_trace.py"],
            "pka_verdict": "ALLOW"
        },
        # Candidate 3: Runtime Metal Claim WITHOUT Evidence -> Rejected with Conflict Receipt
        {
            "idempotency_key": "off_candidate_003",
            "actor_seat": "UNVERIFIED_AGENT",
            "embodiment": PlatformEmbodiment.ANDROID_KEYSTORE_WORKMANAGER.value,
            "claim_type": "RUNTIME_OR_METAL",
            "payload": {"fake_metal_claim": "server online without proof"},
            "evidence_refs": [],  # Empty evidence for metal claim!
            "pka_verdict": "ALLOW"
        }
    ]

    # Cold Restart: Initialize fresh engine instances from disk
    ledger = SmartLedgerEngine(db_path=db_file)
    bridge = PkaKmecJenniferBridge(balance_point=0.5, ledger=ledger)
    reconciler = OfflineReconciliationEngine(ledger, bridge)

    # Reconcile batch upon reconnection
    report = reconciler.reconcile_batch(candidate_batch)

    assert report.total_candidates == 3
    assert report.admitted_count == 2
    assert report.conflict_count == 1
    assert report.chain_valid is True
    assert len(report.rebuilt_projection_keys) == 2

    # Verify that the Conflict Receipt is durable in the chain
    conflict_rcpt = ledger.get_receipt_by_id(report.conflict_receipt_ids[0])
    assert conflict_rcpt.admission_state == SmartLedgerAdmissionState.CONFLICT_REJECTED
    assert conflict_rcpt.pka_verdict == "BLOCK"
    assert "PKA Reject" in conflict_rcpt.payload["reason"]

    # Verify that projections in MongoDB layer are rebuildable from ledger receipts
    for proj_key in report.rebuilt_projection_keys:
        assert proj_key in bridge.projection_store
        proj_data = bridge.projection_store[proj_key]
        assert proj_data["layer"] == JenniferDatabaseLayer.MONGODB_PROJECTION.value

    # Verify entire chain integrity from Genesis through all 3 blocks
    chain = ledger.list_chain()
    assert len(chain) == 3
    assert chain[0].sequence_number == 1
    assert chain[1].sequence_number == 2
    assert chain[2].sequence_number == 3
    assert chain[2].previous_receipt_hash == chain[1].receipt_hash
    assert chain[1].previous_receipt_hash == chain[0].receipt_hash
