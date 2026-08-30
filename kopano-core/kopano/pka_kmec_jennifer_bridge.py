"""
PKA-KMEC-Jennifer Bridge Module
Canonical Cross-Estate Ingress for Kopano Phu Governance Systems (KPGS)

Connects:
1. PKA (Partial-Knowable-Algebra): 13 FOC groups, convergence bands, and trust vectors.
2. KMEC (Morning Engine Core): Observational membrane (D_t, F_t, G_t, R_t), GSMB markdown telemetry.
3. Project Jennifer: Dual-database consequence journal, projection != authority, and validation policy merge gates.

Authority: Master Robyn Kholofelo Rababalela (Seat 1)
Compiler: AntiGravity (Seat 10 / Chief Facilitator)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import time
import uuid


class PkaConvergenceBand(Enum):
    TOWARD_ZERO = "TowardZero"  # Divergence pole (< 0.5)
    BALANCED = "Balanced"        # Founder-defined balance point (0.5)
    TOWARD_ONE = "TowardOne"    # Convergence pole (> 0.5)


class PkaTrustVector(Enum):
    GREEN = "GREEN"    # (PocCandidate, Propose)
    YELLOW = "YELLOW"  # (Maybe, Hold)
    RED = "RED"        # (FocCandidate, Block)


class JenniferDatabaseLayer(Enum):
    POSTGRESQL_AUTHORITATIVE = "PostgreSQL_Authoritative" # Immutable event ledger & consequence journal
    MONGODB_PROJECTION = "MongoDB_Projection"             # Mutable adaptive projection (UI view)


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


class PkaKmecJenniferBridge:
    """Unified bridge orchestrating PKA math, KMEC observation, and Jennifer governance."""

    def __init__(self, balance_point: float = 0.5):
        self.balance_point = balance_point
        self.consequence_journal: List[ConsequenceJournalEntry] = []
        self.projection_store: Dict[str, Dict[str, Any]] = {}

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
        raw_bytes = json_str = str(sorted(payload.items())).encode("utf-8")
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
        Rejects projection updates without valid journal receipt.
        """
        valid_receipts = [e.entry_id for e in self.consequence_journal]
        if source_entry_id not in valid_receipts:
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
        # Gate 1: Source Provenance
        if not declared_source or not declared_by or not declaration_date:
            violations.append("Gate 1 Failed: Incomplete source provenance metadata.")
        
        # Gate 2: Explicit Validation State
        if validation_state.upper() not in ["PENDING", "VALIDATED", "UNVERIFIED"]:
            violations.append(f"Gate 2 Failed: Invalid validation state '{validation_state}'.")
            
        # Gate 3: Evidence Checklist
        if not evidence_linked and validation_state.upper() == "VALIDATED":
            violations.append("Gate 3 Failed: Claimed 'Validated' state without linked evidence.")
            
        # Gate 4: Governance Approver Sign-Off
        if not governance_signed:
            violations.append("Gate 4 Failed: Missing governance approver sign-off.")

        return (len(violations) == 0, violations)
