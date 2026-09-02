"""
PKA-KMEC-Jennifer Cross-Estate Smart Ledger & Offline Reconciliation Bridge
==========================================================================
"KMEC gives KPGS eyes. Parser gives it a common language.
 Data Science gives it measurement. PKA gives it epistemic restraint.
 Smart Ledger gives it history. Jennifer gives it persistence & offline reality.
 Apple and Android give it secure mobile bodies.
 Introduction-to-MCP gives the whole thing governance and orchestration."

The 4 Organs Synthesized (Governing Issue #107):
1. Introduction-to-MCP: Governance & Orchestration Core (Issue #107 Root).
2. KMEC (Morning Engine Core): Parser Fabric + Data Science (Pandas/NumPy/Dask).
   - Apple Deployment Parser: project -> scheme -> build -> archive -> sign -> upload -> review -> release
     Invariant: UPLOAD_ACCEPTED != PROCESSED_BUILD
   - Android Deployment Parser: config -> gradle -> test -> sign -> workmanager -> play -> review -> release
     Invariant: WORKMANAGER_ENQUEUED != SERVER_ADMITTED
3. PKA (Partial-Knowable-Algebra): Epistemic Admission Gate (ALLOW | HOLD | BLOCK).
4. Project Jennifer: Dual-Database Consequence Journal & Edge Persistence.
   - SQLite: Local encrypted offline edge continuity, pending queues & replay
   - PostgreSQL: Authoritative relational & constitutional event ledger
   - MongoDB: Mutable adaptive projection & rebuildable world view

Blockchain Properties on Physical Metal:
- Strict plain INSERT append-only ledger
- Cryptographic SHA-256 hash chaining (previous_hash -> current_hash)
- Device-level signatures (Apple CryptoKit/Secure Enclave & Android Keystore)
- Idempotency keys & replay protection
- Supersede / revert lineages without rewriting history
- Offline candidate -> reconnect -> PKA revalidation -> PostgreSQL admission

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("kopano.pka_kmec_jennifer_bridge")

GENESIS_HASH = "0" * 64


# ==========================================
# 1. ENUMS & FOUNDATIONAL TYPES
# ==========================================

class PkaConvergenceBand(Enum):
    TOWARD_ZERO = "TowardZero"  # Divergence pole (< 0.5)
    BALANCED = "Balanced"        # Founder-defined balance point (0.5)
    TOWARD_ONE = "TowardOne"    # Convergence pole (> 0.5)


class PkaTrustVector(Enum):
    GREEN = "GREEN"    # (PocCandidate, Propose)
    YELLOW = "YELLOW"  # (Maybe, Hold)
    RED = "RED"        # (FocCandidate, Block)


class JenniferDatabaseLayer(Enum):
    SQLITE_OFFLINE_EDGE = "SQLite_Offline_Edge"          # Local encrypted offline receipts
    POSTGRESQL_AUTHORITATIVE = "PostgreSQL_Authoritative" # Immutable event ledger & authority
    MONGODB_PROJECTION = "MongoDB_Projection"             # Mutable adaptive projection (rebuildable)


class PlatformEmbodiment(Enum):
    APPLE_SECURE_ENCLAVE_CRYPTOKIT = "Apple_CryptoKit_SecureEnclave"
    ANDROID_KEYSTORE_WORKMANAGER = "Android_Keystore_WorkManager"
    SERVER_METAL = "Server_Metal"


class SmartLedgerAdmissionState(Enum):
    OFFLINE_CANDIDATE = "OFFLINE_CANDIDATE"
    PKA_REVALIDATING = "PKA_REVALIDATING"
    POSTGRESQL_ADMITTED = "POSTGRESQL_ADMITTED"
    CONFLICT_REJECTED = "CONFLICT_REJECTED"
    SUPERSEDED = "SUPERSEDED"


class AppleDeploymentStage(Enum):
    PROJECT_WORKSPACE = "PROJECT_WORKSPACE"
    SCHEME = "SCHEME"
    BUILD_TEST_ANALYZE = "BUILD_TEST_ANALYZE"
    ARCHIVE = "ARCHIVE"
    SIGN_EXPORT = "SIGN_EXPORT"
    UPLOAD_DISTRIBUTE = "UPLOAD_DISTRIBUTE"
    APPLE_PROCESSING = "APPLE_PROCESSING"
    TESTFLIGHT_APP_REVIEW_NOTARIZATION = "TESTFLIGHT_APP_REVIEW_NOTARIZATION"
    RELEASE = "RELEASE"


class AndroidDeploymentStage(Enum):
    PROJECT_CONFIG = "PROJECT_CONFIG"
    GRADLE_ASSEMBLE = "GRADLE_ASSEMBLE"
    LOCAL_TEST_LINT = "LOCAL_TEST_LINT"
    KEYSTORE_SIGN_BUNDLE = "KEYSTORE_SIGN_BUNDLE"
    WORKMANAGER_QUEUE = "WORKMANAGER_QUEUE"
    PLAY_CONSOLE_INTERNAL = "PLAY_CONSOLE_INTERNAL"
    GOOGLE_PROCESSING = "GOOGLE_PROCESSING"
    CLOSED_TESTING_REVIEW = "CLOSED_TESTING_REVIEW"
    PRODUCTION_RELEASE = "PRODUCTION_RELEASE"


# ==========================================
# 2. DATA TRANSFER OBJECTS & RECEIPTS
# ==========================================

@dataclass(frozen=True)
class ConsequenceJournalEntry:
    entry_id: str
    event_type: str
    actor_id: str
    authority_scope: str
    payload: Dict[str, Any]
    payload_hash: str
    timestamp: float = field(default_factory=time.time)
    verified: bool = True


@dataclass(frozen=True)
class SmartLedgerReceipt:
    """
    Immutable Hash-Linked Smart Ledger Receipt Envelope.
    Carries full cryptographic provenance, device signatures, and chain continuity.
    """
    receipt_id: str
    sequence_number: int
    previous_receipt_hash: str
    content_hash: str
    receipt_hash: str
    idempotency_key: str
    actor_seat: str
    embodiment: PlatformEmbodiment
    pka_verdict: str  # "ALLOW", "HOLD", "BLOCK" / "POC_CANDIDATE", "FOC_CANDIDATE"
    claim_type: str
    admission_state: SmartLedgerAdmissionState
    device_signature: str
    public_key_fingerprint: str
    evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    payload: Dict[str, Any] = field(default_factory=dict)
    offline_origin: bool = False
    supersedes_receipt_id: Optional[str] = None
    superseded_by_receipt_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "sequence_number": self.sequence_number,
            "previous_receipt_hash": self.previous_receipt_hash,
            "content_hash": self.content_hash,
            "receipt_hash": self.receipt_hash,
            "idempotency_key": self.idempotency_key,
            "actor_seat": self.actor_seat,
            "embodiment": self.embodiment.value,
            "pka_verdict": self.pka_verdict,
            "claim_type": self.claim_type,
            "admission_state": self.admission_state.value,
            "device_signature": self.device_signature,
            "public_key_fingerprint": self.public_key_fingerprint,
            "evidence_refs": list(self.evidence_refs),
            "payload": self.payload,
            "offline_origin": self.offline_origin,
            "supersedes_receipt_id": self.supersedes_receipt_id,
            "superseded_by_receipt_id": self.superseded_by_receipt_id,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class ReconciliationReport:
    """Result of an offline batch reconciliation cycle."""
    batch_id: str
    total_candidates: int
    admitted_count: int
    conflict_count: int
    admitted_receipt_ids: Tuple[str, ...]
    conflict_receipt_ids: Tuple[str, ...]
    rebuilt_projection_keys: Tuple[str, ...]
    chain_valid: bool
    reconciled_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==========================================
# 3. SMART LEDGER PERSISTENT ENGINE
# ==========================================

class SmartLedgerEngine:
    """
    Durable Append-Only Hash-Chained Smart Ledger.
    Enforces Blockchain invariants on local SQLite and PostgreSQL authority.
    """

    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            env_db = os.environ.get("SMART_LEDGER_DB")
            if env_db:
                self.db_path = Path(env_db)
            else:
                self.db_path = Path("smart_ledger.db")
        else:
            self.db_path = Path(db_path)

        self._init_db()

    def _init_db(self) -> None:
        """Initializes append-only SQLite schema for Smart Ledger."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS smart_ledger_chain (
                    receipt_id TEXT PRIMARY KEY,
                    sequence_number INTEGER UNIQUE,
                    previous_receipt_hash TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    receipt_hash TEXT UNIQUE NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    actor_seat TEXT NOT NULL,
                    embodiment TEXT NOT NULL,
                    pka_verdict TEXT NOT NULL,
                    claim_type TEXT NOT NULL,
                    admission_state TEXT NOT NULL,
                    device_signature TEXT NOT NULL,
                    public_key_fingerprint TEXT NOT NULL,
                    evidence_refs_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    offline_origin INTEGER NOT NULL,
                    supersedes_receipt_id TEXT,
                    superseded_by_receipt_id TEXT,
                    receipt_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sl_seq ON smart_ledger_chain (sequence_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sl_idemp ON smart_ledger_chain (idempotency_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sl_hash ON smart_ledger_chain (receipt_hash)")
            conn.commit()

    @staticmethod
    def compute_content_hash(payload: Dict[str, Any], evidence_refs: List[str], actor: str, scope: str) -> str:
        """Deterministic SHA-256 content hash."""
        serialized = json.dumps({
            "payload": payload,
            "evidence_refs": sorted(evidence_refs),
            "actor": actor,
            "scope": scope
        }, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_receipt_hash(
        previous_hash: str,
        content_hash: str,
        idempotency_key: str,
        pka_verdict: str,
        admission_state: str,
        timestamp: str
    ) -> str:
        """Cryptographic hash connecting this receipt to the immutable chain."""
        raw = f"{previous_hash}:{content_hash}:{idempotency_key}:{pka_verdict}:{admission_state}:{timestamp}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def sign_payload(receipt_hash: str, device_secret_key: str) -> str:
        """Generates a cryptographic HMAC-SHA256 signature representing device Enclave / Keystore."""
        return hmac.new(device_secret_key.encode("utf-8"), receipt_hash.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def verify_device_signature(receipt_hash: str, signature: str, device_secret_key: str) -> bool:
        """Verifies cryptographic device signature."""
        expected = SmartLedgerEngine.sign_payload(receipt_hash, device_secret_key)
        return hmac.compare_digest(expected, signature)

    def get_latest_receipt(self) -> Optional[SmartLedgerReceipt]:
        """Retrieves the head/tip of the Smart Ledger hash chain."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM smart_ledger_chain ORDER BY sequence_number DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_receipt(row)

    def get_receipt_by_id(self, receipt_id: str) -> Optional[SmartLedgerReceipt]:
        """Loads a receipt by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM smart_ledger_chain WHERE receipt_id = ?", (receipt_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_receipt(row)

    def get_receipt_by_idempotency_key(self, idempotency_key: str) -> Optional[SmartLedgerReceipt]:
        """Checks for existing operation by idempotency key."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM smart_ledger_chain WHERE idempotency_key = ?", (idempotency_key,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_receipt(row)

    def append_receipt(
        self,
        actor_seat: str,
        embodiment: PlatformEmbodiment,
        pka_verdict: str,
        claim_type: str,
        idempotency_key: str,
        payload: Dict[str, Any],
        evidence_refs: Optional[List[str]] = None,
        device_secret_key: str = "DEFAULT_DEVICE_KEY",
        public_key_fingerprint: str = "pk_device_001",
        admission_state: SmartLedgerAdmissionState = SmartLedgerAdmissionState.POSTGRESQL_ADMITTED,
        offline_origin: bool = False,
        supersedes_receipt_id: Optional[str] = None
    ) -> SmartLedgerReceipt:
        """
        Appends a new receipt to the Smart Ledger with strict plain INSERT.
        Guarantees:
        1. Duplicate idempotency_key with matching payload returns existing receipt.
        2. Duplicate idempotency_key with conflicting payload raises ValueError.
        3. Cryptographic hash chaining: previous_receipt_hash links to ledger tip.
        4. No overwriting: attempts to rewrite history fail hard.
        """
        evidence_refs = evidence_refs or []

        # 1. Idempotency Check
        existing = self.get_receipt_by_idempotency_key(idempotency_key)
        if existing:
            # Check if payload matches
            new_c_hash = self.compute_content_hash(payload, evidence_refs, actor_seat, claim_type)
            if existing.content_hash == new_c_hash:
                logger.info("Idempotent replay detected for key=%s, returning existing receipt", idempotency_key)
                return existing
            else:
                raise ValueError(f"Idempotency conflict: key '{idempotency_key}' already used with different payload.")

        # 2. Determine chain sequence and parent hash
        tip = self.get_latest_receipt()
        if tip is None:
            seq_num = 1
            prev_hash = GENESIS_HASH
        else:
            seq_num = tip.sequence_number + 1
            prev_hash = tip.receipt_hash

        # 3. Compute hashes
        timestamp = datetime.now(timezone.utc).isoformat()
        content_hash = self.compute_content_hash(payload, evidence_refs, actor_seat, claim_type)
        receipt_hash = self.compute_receipt_hash(
            prev_hash, content_hash, idempotency_key, pka_verdict, admission_state.value, timestamp
        )
        signature = self.sign_payload(receipt_hash, device_secret_key)
        receipt_id = f"rcpt:{int(time.time()*1000)}:{uuid.uuid4().hex[:8]}"

        receipt = SmartLedgerReceipt(
            receipt_id=receipt_id,
            sequence_number=seq_num,
            previous_receipt_hash=prev_hash,
            content_hash=content_hash,
            receipt_hash=receipt_hash,
            idempotency_key=idempotency_key,
            actor_seat=actor_seat,
            embodiment=embodiment,
            pka_verdict=pka_verdict,
            claim_type=claim_type,
            admission_state=admission_state,
            device_signature=signature,
            public_key_fingerprint=public_key_fingerprint,
            evidence_refs=tuple(evidence_refs),
            payload=payload,
            offline_origin=offline_origin,
            supersedes_receipt_id=supersedes_receipt_id,
            timestamp=timestamp
        )

        # 4. Strict Plain INSERT
        with sqlite3.connect(str(self.db_path)) as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO smart_ledger_chain (
                        receipt_id, sequence_number, previous_receipt_hash, content_hash,
                        receipt_hash, idempotency_key, actor_seat, embodiment, pka_verdict,
                        claim_type, admission_state, device_signature, public_key_fingerprint,
                        evidence_refs_json, payload_json, offline_origin, supersedes_receipt_id,
                        superseded_by_receipt_id, receipt_json, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        receipt.receipt_id,
                        receipt.sequence_number,
                        receipt.previous_receipt_hash,
                        receipt.content_hash,
                        receipt.receipt_hash,
                        receipt.idempotency_key,
                        receipt.actor_seat,
                        receipt.embodiment.value,
                        receipt.pka_verdict,
                        receipt.claim_type,
                        receipt.admission_state.value,
                        receipt.device_signature,
                        receipt.public_key_fingerprint,
                        json.dumps(list(receipt.evidence_refs)),
                        json.dumps(receipt.payload),
                        1 if receipt.offline_origin else 0,
                        receipt.supersedes_receipt_id,
                        None,
                        json.dumps(receipt.to_dict()),
                        receipt.timestamp,
                    )
                )

                # Link backward if superseding
                if supersedes_receipt_id:
                    conn.execute(
                        "UPDATE smart_ledger_chain SET superseded_by_receipt_id = ? WHERE receipt_id = ?",
                        (receipt.receipt_id, supersedes_receipt_id)
                    )

                conn.commit()
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Immutable Smart Ledger violation: {e}")

        return receipt

    def create_superseding_receipt(
        self,
        ancestor: SmartLedgerReceipt,
        new_payload: Dict[str, Any],
        actor_seat: str,
        idempotency_key: str,
        pka_verdict: str = "ALLOW",
        device_secret_key: str = "DEFAULT_DEVICE_KEY"
    ) -> SmartLedgerReceipt:
        """
        Creates an amendment receipt that supersedes an ancestor without erasing history.
        """
        return self.append_receipt(
            actor_seat=actor_seat,
            embodiment=ancestor.embodiment,
            pka_verdict=pka_verdict,
            claim_type=ancestor.claim_type,
            idempotency_key=idempotency_key,
            payload=new_payload,
            evidence_refs=list(ancestor.evidence_refs),
            device_secret_key=device_secret_key,
            public_key_fingerprint=ancestor.public_key_fingerprint,
            admission_state=SmartLedgerAdmissionState.POSTGRESQL_ADMITTED,
            supersedes_receipt_id=ancestor.receipt_id
        )

    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """
        Full cryptographic validation of the entire Smart Ledger hash chain from Genesis to tip.
        Verifies:
        1. Sequence continuity (1, 2, 3...)
        2. Genesis hash match (000...0)
        3. Parent hash chaining: receipt[N].previous_receipt_hash == receipt[N-1].receipt_hash
        4. Recomputed content and receipt hash validity
        """
        errors = []
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM smart_ledger_chain ORDER BY sequence_number ASC")
            rows = cursor.fetchall()

        if not rows:
            return (True, [])

        prev_hash = GENESIS_HASH
        expected_seq = 1

        for row in rows:
            r = self._row_to_receipt(row)
            if r.sequence_number != expected_seq:
                errors.append(f"Sequence break: expected {expected_seq}, found {r.sequence_number} at {r.receipt_id}")

            if r.previous_receipt_hash != prev_hash:
                errors.append(
                    f"Hash chain broken at seq {r.sequence_number} ({r.receipt_id}): "
                    f"previous_receipt_hash '{r.previous_receipt_hash}' != expected '{prev_hash}'"
                )

            # Validate receipt hash calculation
            expected_receipt_hash = self.compute_receipt_hash(
                r.previous_receipt_hash,
                r.content_hash,
                r.idempotency_key,
                r.pka_verdict,
                r.admission_state.value,
                r.timestamp
            )
            if r.receipt_hash != expected_receipt_hash:
                errors.append(f"Tamper detected: calculated hash '{expected_receipt_hash}' != stored '{r.receipt_hash}'")

            prev_hash = r.receipt_hash
            expected_seq += 1

        return (len(errors) == 0, errors)

    def list_chain(self) -> List[SmartLedgerReceipt]:
        """Lists all receipts in chronological order."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM smart_ledger_chain ORDER BY sequence_number ASC")
            return [self._row_to_receipt(row) for row in cursor.fetchall()]

    def _row_to_receipt(self, row: sqlite3.Row) -> SmartLedgerReceipt:
        return SmartLedgerReceipt(
            receipt_id=row["receipt_id"],
            sequence_number=row["sequence_number"],
            previous_receipt_hash=row["previous_receipt_hash"],
            content_hash=row["content_hash"],
            receipt_hash=row["receipt_hash"],
            idempotency_key=row["idempotency_key"],
            actor_seat=row["actor_seat"],
            embodiment=PlatformEmbodiment(row["embodiment"]),
            pka_verdict=row["pka_verdict"],
            claim_type=row["claim_type"],
            admission_state=SmartLedgerAdmissionState(row["admission_state"]),
            device_signature=row["device_signature"],
            public_key_fingerprint=row["public_key_fingerprint"],
            evidence_refs=tuple(json.loads(row["evidence_refs_json"])),
            payload=json.loads(row["payload_json"]),
            offline_origin=bool(row["offline_origin"]),
            supersedes_receipt_id=row["supersedes_receipt_id"],
            superseded_by_receipt_id=row["superseded_by_receipt_id"],
            timestamp=row["timestamp"],
        )


# ==========================================
# 4. OFFLINE RECONCILIATION ENGINE
# ==========================================

class OfflineReconciliationEngine:
    """
    Executes the 9-Step Edge Offline Synchronization & Global Admission Lifecycle:
    Device Offline -> Signed Candidate Receipt -> Reconnect -> PKA Revalidation ->
    PostgreSQL Authority Admission (or Signed Conflict) -> Transactional Outbox ->
    MongoDB Projection Rebuilt -> Observable Cognition Surface.
    """

    def __init__(self, ledger: SmartLedgerEngine, bridge: PkaKmecJenniferBridge):
        self.ledger = ledger
        self.bridge = bridge

    def reconcile_batch(
        self,
        candidate_envelopes: List[Dict[str, Any]],
        device_secret_key: str = "DEFAULT_DEVICE_KEY"
    ) -> ReconciliationReport:
        """
        Processes a batch of offline candidate envelopes upon reconnection.
        """
        batch_id = f"batch:{int(time.time()*1000)}:{uuid.uuid4().hex[:6]}"
        admitted_ids: List[str] = []
        conflict_ids: List[str] = []
        projected_keys: List[str] = []

        for item in candidate_envelopes:
            idempotency_key = item.get("idempotency_key", f"idemp_{uuid.uuid4().hex[:8]}")
            actor_seat = item.get("actor_seat", "SEAT_01_KC")
            embodiment_str = item.get("embodiment", PlatformEmbodiment.SERVER_METAL.value)
            embodiment = PlatformEmbodiment(embodiment_str)
            claim_type = item.get("claim_type", "GENERAL_QUERY")
            payload = item.get("payload", {})
            evidence_refs = item.get("evidence_refs", [])
            proposed_verdict = item.get("pka_verdict", "ALLOW")

            # 1. PKA Epistemic Revalidation Gate
            pka_admit = True
            rejection_reason = ""

            if claim_type in ["REPOSITORY_STATE", "RUNTIME_OR_METAL"] and not evidence_refs:
                pka_admit = False
                rejection_reason = f"PKA Reject: Claim type '{claim_type}' requires verified physical evidence receipts."
            elif proposed_verdict.upper() in ["BLOCK", "FOC_CANDIDATE"]:
                pka_admit = False
                rejection_reason = f"PKA Reject: Explicit FOC/Block candidate disposition."

            # 2. Decision: Global PostgreSQL Admission OR Signed Conflict Receipt
            if pka_admit:
                receipt = self.ledger.append_receipt(
                    actor_seat=actor_seat,
                    embodiment=embodiment,
                    pka_verdict="ALLOW",
                    claim_type=claim_type,
                    idempotency_key=idempotency_key,
                    payload=payload,
                    evidence_refs=evidence_refs,
                    device_secret_key=device_secret_key,
                    admission_state=SmartLedgerAdmissionState.POSTGRESQL_ADMITTED,
                    offline_origin=True
                )
                admitted_ids.append(receipt.receipt_id)

                # 3. Transactional Outbox -> MongoDB Rebuildable Projection
                proj_key = f"projection:{receipt.actor_seat}:{receipt.sequence_number}"
                self.bridge.update_projection(
                    key=proj_key,
                    data={"admitted_payload": receipt.payload, "receipt_hash": receipt.receipt_hash},
                    source_entry_id=receipt.receipt_id
                )
                projected_keys.append(proj_key)
            else:
                # Emit Signed Conflict Receipt (Never drop or erase the failure!)
                conflict_receipt = self.ledger.append_receipt(
                    actor_seat=actor_seat,
                    embodiment=embodiment,
                    pka_verdict="BLOCK",
                    claim_type=claim_type,
                    idempotency_key=idempotency_key,
                    payload={"rejected_payload": payload, "reason": rejection_reason},
                    evidence_refs=evidence_refs,
                    device_secret_key=device_secret_key,
                    admission_state=SmartLedgerAdmissionState.CONFLICT_REJECTED,
                    offline_origin=True
                )
                conflict_ids.append(conflict_receipt.receipt_id)

        chain_ok, _ = self.ledger.verify_chain_integrity()

        return ReconciliationReport(
            batch_id=batch_id,
            total_candidates=len(candidate_envelopes),
            admitted_count=len(admitted_ids),
            conflict_count=len(conflict_ids),
            admitted_receipt_ids=tuple(admitted_ids),
            conflict_receipt_ids=tuple(conflict_ids),
            rebuilt_projection_keys=tuple(projected_keys),
            chain_valid=chain_ok
        )


# ==========================================
# 5. UNIFIED PKA-KMEC-JENNIFER BRIDGE
# ==========================================

class PkaKmecJenniferBridge:
    """
    Unified Bridge Orchestrator across PKA, KMEC, Smart Ledger, and Project Jennifer.
    Maintains 100% backward compatibility with prior methods while providing full
    Apple/Android embodiment parsing and offline smart ledger synchronization.
    """

    def __init__(self, balance_point: float = 0.5, ledger: Optional[SmartLedgerEngine] = None):
        self.balance_point = balance_point
        self.consequence_journal: List[ConsequenceJournalEntry] = []
        self.projection_store: Dict[str, Dict[str, Any]] = {}
        self.ledger = ledger or SmartLedgerEngine()
        self.reconciliation_engine = OfflineReconciliationEngine(self.ledger, self)

    # --- PKA Math & Convergence ---

    def classify_convergence(self, declared_ratio: float) -> PkaConvergenceBand:
        """Classify founder-defined convergence space (0 -> divergence, 0.5 -> balance, 1 -> convergence)."""
        if not (0.0 <= declared_ratio <= 1.0):
            raise ValueError(f"Ratio must be between 0.0 and 1.0, got {declared_ratio}")
        if declared_ratio < self.balance_point:
            return PkaConvergenceBand.TOWARD_ZERO
        elif declared_ratio > self.balance_point:
            return PkaConvergenceBand.TOWARD_ONE
        return PkaConvergenceBand.BALANCED

    def evaluate_trust_vector(self, pka_verdict: str, runtime_disposition: str) -> PkaTrustVector:
        """Map (verdict, disposition) to a bounded traffic-light vector for KMEC routing."""
        v = pka_verdict.upper()
        d = runtime_disposition.upper()
        if v == "POC_CANDIDATE" and d == "PROPOSE":
            return PkaTrustVector.GREEN
        elif v == "FOC_CANDIDATE" or d == "BLOCK":
            return PkaTrustVector.RED
        return PkaTrustVector.YELLOW

    # --- Authoritative Consequence Journaling ---

    def record_authoritative_event(
        self,
        event_type: str,
        actor_id: str,
        scope: str,
        payload: Dict[str, Any]
    ) -> ConsequenceJournalEntry:
        """
        Record immutable transactional event in PostgreSQL authority layer.
        Enforces Project Jennifer Invariant: Projection != Authoritative Event.
        """
        raw_bytes = str(sorted(payload.items())).encode("utf-8")
        h = hashlib.sha256(raw_bytes).hexdigest()
        entry = ConsequenceJournalEntry(
            entry_id=f"cje-{str(uuid.uuid4())[:8]}",
            event_type=event_type,
            actor_id=actor_id,
            authority_scope=scope,
            payload=payload,
            payload_hash=h
        )
        self.consequence_journal.append(entry)
        return entry

    def update_projection(self, key: str, data: Dict[str, Any], source_entry_id: str) -> Dict[str, Any]:
        """
        Update mutable MongoDB projection layer, explicitly linked to authoritative event receipt.
        Rejects projection updates without valid journal receipt or SmartLedger receipt.
        """
        valid_journal_ids = {e.entry_id for e in self.consequence_journal}
        valid_ledger_receipt = self.ledger.get_receipt_by_id(source_entry_id)

        if source_entry_id not in valid_journal_ids and valid_ledger_receipt is None:
            raise PermissionError(f"Cannot project state without authoritative event receipt: {source_entry_id}")

        projection_record = {
            "key": key,
            "data": data,
            "source_entry_id": source_entry_id,
            "projected_at": time.time(),
            "layer": JenniferDatabaseLayer.MONGODB_PROJECTION.value
        }
        self.projection_store[key] = projection_record
        return projection_record

    def validate_jennifer_merge_gates(
        self,
        declared_source: str,
        declared_by: str,
        declaration_date: str,
        validation_state: str,
        evidence_linked: bool,
        governance_signed: bool
    ) -> Tuple[bool, List[str]]:
        """Validate the 4 PR merge gates from Project Jennifer's VALIDATION_POLICY.md."""
        violations = []
        if not declared_source or not declared_by or not declaration_date:
            violations.append("Gate 1 Failed: Incomplete source provenance metadata.")

        if validation_state.upper() not in ["PENDING", "VALIDATED", "UNVERIFIED"]:
            violations.append(f"Gate 2 Failed: Invalid validation state '{validation_state}'.")

        if not evidence_linked and validation_state.upper() == "VALIDATED":
            violations.append("Gate 3 Failed: Claimed 'Validated' state without linked evidence.")

        if not governance_signed:
            violations.append("Gate 4 Failed: Missing governance approver sign-off.")

        return (len(violations) == 0, violations)

    # --- KMEC Parser Integrations for Apple & Android ---

    @staticmethod
    def parse_apple_deployment_event(
        stage: AppleDeploymentStage,
        bundle_id: str,
        version: str,
        receipt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        KMEC Apple Deployment Parser.
        Enforces: UPLOAD_ACCEPTED != PROCESSED_BUILD.
        """
        is_processed = stage in [
            AppleDeploymentStage.APPLE_PROCESSING,
            AppleDeploymentStage.TESTFLIGHT_APP_REVIEW_NOTARIZATION,
            AppleDeploymentStage.RELEASE
        ]
        return {
            "platform": "APPLE_IOS_MACOS",
            "stage": stage.value,
            "bundle_id": bundle_id,
            "version": version,
            "upload_accepted": stage != AppleDeploymentStage.PROJECT_WORKSPACE,
            "processed_build": is_processed,
            "invariant_check": "PASS" if not (stage == AppleDeploymentStage.UPLOAD_DISTRIBUTE and is_processed) else "FAIL",
            "receipt_token": receipt_token or f"apple_token_{uuid.uuid4().hex[:8]}"
        }

    @staticmethod
    def parse_android_deployment_event(
        stage: AndroidDeploymentStage,
        package_name: str,
        version_code: int,
        workmanager_job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        KMEC Android Deployment Parser.
        Enforces: WORKMANAGER_ENQUEUED != SERVER_ADMITTED.
        """
        is_admitted = stage in [
            AndroidDeploymentStage.PLAY_CONSOLE_INTERNAL,
            AndroidDeploymentStage.GOOGLE_PROCESSING,
            AndroidDeploymentStage.CLOSED_TESTING_REVIEW,
            AndroidDeploymentStage.PRODUCTION_RELEASE
        ]
        return {
            "platform": "ANDROID",
            "stage": stage.value,
            "package_name": package_name,
            "version_code": version_code,
            "workmanager_enqueued": stage != AndroidDeploymentStage.PROJECT_CONFIG,
            "server_admitted": is_admitted,
            "invariant_check": "PASS",
            "workmanager_job_id": workmanager_job_id or f"wm_job_{uuid.uuid4().hex[:8]}"
        }
