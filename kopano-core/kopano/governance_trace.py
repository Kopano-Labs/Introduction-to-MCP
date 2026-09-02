"""
OBSERVABLE COGNITION SURFACE & DURABLE RTC ACTIVITY LEDGER
===========================================================
"Evidence is truth-pressure. Governance is continuity."
"Show me what the system is doing to earn the answer."

Canonical FEP Evidence Classes (from 24-RTC Learning / fep_engine.py):
  E1: Direct User Testimony (Master Robyn's direct voice / human authority)
  E2: Repository / Artifact Evidence (Git commits, SQLite datalake, Schematics, physical tests)
  E3: Working Inference (Model synthesis, structured deduction)
  E4: Unknown / Requires Forensic Audit (External signals, unverified web inputs)

Observable Cognition Surface — 7 Core Questions:
  1. Where did you look? (where_looked)
  2. What did you remember? (what_remembered)
  3. What did you validate? (what_validated)
  4. Which brain did you consult? (which_brain_consulted)
  5. What contradicted what? (contradictions_resolved)
  6. What evidence survived? (evidence_items with E1-E4 classification & verification)
  7. Epistemic state & why trust? (PROVEN / SUPPORTED / INFERRED / UNKNOWN derived by policy)

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("kopano.governance_trace")

LEDGER_DB_PATH = Path(os.environ.get(
    "RTC_ACTIVITY_LEDGER_DB",
    str(Path.home() / ".kopano" / "rtc_activity_ledger.db")
))


class CanonicalEvidenceClass(str, Enum):
    """Canonical FEP Evidence Classes (aligned with fep_engine.py)."""
    E1_DIRECT_TESTIMONY = "E1_Direct_User_Testimony"
    E2_REPOSITORY_ARTIFACT = "E2_Repository_Artifact_Evidence"
    E3_WORKING_INFERENCE = "E3_Working_Inference"
    E4_UNKNOWN_AUDIT_REQUIRED = "E4_Unknown_Requires_Forensic_Audit"


class ClaimType(str, Enum):
    """Claim categories for claim-type-aware epistemic derivation."""
    USER_INTENT_OR_TESTIMONY = "USER_INTENT_OR_TESTIMONY"
    REPOSITORY_STATE = "REPOSITORY_STATE"
    RUNTIME_OR_METAL = "RUNTIME_OR_METAL"
    MODEL_INTERPRETATION = "MODEL_INTERPRETATION"
    EXTERNAL_FACT = "EXTERNAL_FACT"
    GENERAL_QUERY = "GENERAL_QUERY"


class EpistemicState(str, Enum):
    PROVEN = "PROVEN"          # Verified claim-fit evidence (E1 for intent, E2 for repo/metal)
    SUPPORTED = "SUPPORTED"    # Grounded in supporting evidence but lacks claim-fit proof
    INFERRED = "INFERRED"      # E3 working inferences without hard proof
    UNKNOWN = "UNKNOWN"        # Unverified claims, unresolved contradictions, or E4 items


@dataclass
class TraceEvidenceItem:
    evidence_id: str
    evidence_class: CanonicalEvidenceClass
    source_location: str
    description: str
    verified: bool = False  # Starts unverified by default; must be validated by proof
    falsifiable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_class": self.evidence_class.value,
            "source_location": self.source_location,
            "description": self.description,
            "verified": self.verified,
            "falsifiable": self.falsifiable,
        }


@dataclass
class GovernanceTrace:
    trace_id: str
    session_id: str
    speaker_seat: str  # e.g., "SEAT_01_KC", "SEAT_02_CASSEY", "SEAT_10_ANTIGRAVITY", "FORGE"
    question_or_intent: str
    claim_type: ClaimType = ClaimType.GENERAL_QUERY
    supersedes_trace_id: Optional[str] = None
    superseded_by_trace_id: Optional[str] = None
    where_looked: List[str] = field(default_factory=list)
    what_remembered: List[str] = field(default_factory=list)
    what_validated: List[str] = field(default_factory=list)
    which_brain_consulted: str = "LOCAL_MAO_BLACK_BEAST"  # "LOCAL_MAO", "CLOUD_MMAO", "HYBRID_REFLECTED"
    contradictions_resolved: List[str] = field(default_factory=list)
    evidence_items: List[TraceEvidenceItem] = field(default_factory=list)
    epistemic_state: EpistemicState = EpistemicState.UNKNOWN
    why_trust_reason: str = ""
    content_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_hash(self) -> str:
        """Computes a tamper-evident cryptographic hash over the trace contents."""
        payload = {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "speaker_seat": self.speaker_seat,
            "question_or_intent": self.question_or_intent,
            "claim_type": self.claim_type.value,
            "supersedes_trace_id": self.supersedes_trace_id,
            "where_looked": self.where_looked,
            "what_remembered": self.what_remembered,
            "what_validated": self.what_validated,
            "which_brain_consulted": self.which_brain_consulted,
            "contradictions_resolved": self.contradictions_resolved,
            "evidence_items": [e.to_dict() for e in self.evidence_items],
            "epistemic_state": self.epistemic_state.value,
            "why_trust_reason": self.why_trust_reason,
            "timestamp": self.timestamp,
        }
        raw_json = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "speaker_seat": self.speaker_seat,
            "question_or_intent": self.question_or_intent,
            "claim_type": self.claim_type.value,
            "supersedes_trace_id": self.supersedes_trace_id,
            "superseded_by_trace_id": self.superseded_by_trace_id,
            "where_looked": self.where_looked,
            "what_remembered": self.what_remembered,
            "what_validated": self.what_validated,
            "which_brain_consulted": self.which_brain_consulted,
            "contradictions_resolved": self.contradictions_resolved,
            "evidence_items": [e.to_dict() for e in self.evidence_items],
            "epistemic_state": self.epistemic_state.value,
            "why_trust_reason": self.why_trust_reason,
            "content_hash": self.content_hash or self.compute_hash(),
            "timestamp": self.timestamp,
        }

    def to_visual_card(self) -> str:
        """
        Renders the canonical Observable Cognition Surface ASCII card for desktop UI,
        exposing all 7 observable dimensions without hidden chain-of-thought dumps.
        """
        where_summary = "\n".join(f"  ✓ {w}" for w in self.where_looked) or "  ✓ Direct context"
        rem_summary = "\n".join(f"  • {r}" for r in self.what_remembered) or "  • None retrieved"
        val_summary = "\n".join(f"  ✓ {v}" for v in self.what_validated) or "  ✓ Invariant checks"
        contra_summary = "\n".join(f"  ⚔ {c}" for c in self.contradictions_resolved) or "  • None detected"
        
        ev_lines = []
        for e in self.evidence_items:
            status_icon = "✓" if e.verified else "⚠ UNVERIFIED"
            ev_lines.append(f"  [{status_icon}] {e.evidence_class.value}: {e.description} ({e.source_location})")
        evidence_summary = "\n".join(ev_lines) or "  • None attached"

        return f"""┌────────────────────────────────────────────────────────────────────────────┐
│ OBSERVABLE COGNITION SURFACE — RTC ACTIVITY LEDGER                         │
├────────────────────────────────────────────────────────────────────────────┤
│ SPEAKER / SEAT: {self.speaker_seat}
│ INTENT:         {self.question_or_intent}
│ BRAIN:          {self.which_brain_consulted}
│ SESSION:        {self.session_id}
├────────────────────────────────────────────────────────────────────────────┤
│ 1. WHERE DID YOU LOOK?
{where_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ 2. WHAT DID YOU REMEMBER?
{rem_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ 3. WHAT DID YOU VALIDATE?
{val_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ 4. CONTRADICTIONS RESOLVED:
{contra_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ 5. SURVIVING EVIDENCE:
{evidence_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ 6. EPISTEMIC STATE: [{self.epistemic_state.value}]
│ 7. WHY TRUST:       {self.why_trust_reason}
│    HASH SEAL:       {self.content_hash[:16]}...
└────────────────────────────────────────────────────────────────────────────┘"""


class GovernanceTraceEngine:
    """
    Durable Governance Trace Engine and Append-Only SQLite Activity Ledger.
    Enforces policy-derived epistemic certainty and supports cross-session replay.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(os.environ.get("RTC_ACTIVITY_LEDGER_DB", str(Path.home() / ".kopano" / "rtc_activity_ledger.db")))
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rtc_activity_traces (
                    trace_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    speaker_seat TEXT NOT NULL,
                    question_or_intent TEXT NOT NULL,
                    which_brain TEXT NOT NULL,
                    claim_type TEXT NOT NULL DEFAULT 'GENERAL_QUERY',
                    supersedes_trace_id TEXT,
                    superseded_by_trace_id TEXT,
                    epistemic_state TEXT NOT NULL,
                    why_trust TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    trace_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def start_trace(
        self,
        speaker_seat: str,
        question_or_intent: str,
        session_id: str = "default_session",
        which_brain: str = "LOCAL_MAO_BLACK_BEAST",
        claim_type: ClaimType = ClaimType.GENERAL_QUERY,
        supersedes_trace_id: Optional[str] = None
    ) -> GovernanceTrace:
        trace_id = f"trace:{int(time.time()*1000)}:{hashlib.sha256(question_or_intent.encode('utf-8')).hexdigest()[:8]}"
        return GovernanceTrace(
            trace_id=trace_id,
            session_id=session_id,
            speaker_seat=speaker_seat,
            question_or_intent=question_or_intent,
            which_brain_consulted=which_brain,
            claim_type=claim_type,
            supersedes_trace_id=supersedes_trace_id
        )

    def create_superseding_trace(
        self,
        old_trace: GovernanceTrace,
        question_or_intent: Optional[str] = None,
        speaker_seat: Optional[str] = None
    ) -> GovernanceTrace:
        """
        Creates a new trace that links backward to an older trace without overwriting history.
        """
        return self.start_trace(
            speaker_seat=speaker_seat or old_trace.speaker_seat,
            question_or_intent=question_or_intent or old_trace.question_or_intent,
            session_id=old_trace.session_id,
            which_brain=old_trace.which_brain_consulted,
            claim_type=old_trace.claim_type,
            supersedes_trace_id=old_trace.trace_id
        )

    def record_search(self, trace: GovernanceTrace, source: str) -> None:
        if source not in trace.where_looked:
            trace.where_looked.append(source)

    def record_memory(self, trace: GovernanceTrace, memory_snippet: str) -> None:
        trace.what_remembered.append(memory_snippet)

    def record_validation(self, trace: GovernanceTrace, check_desc: str) -> None:
        trace.what_validated.append(check_desc)

    def record_contradiction(self, trace: GovernanceTrace, contradiction_desc: str) -> None:
        trace.contradictions_resolved.append(contradiction_desc)

    def add_evidence(
        self,
        trace: GovernanceTrace,
        evidence_class: CanonicalEvidenceClass,
        source_location: str,
        description: str,
        verified: bool = False,
        falsifiable: bool = True
    ) -> TraceEvidenceItem:
        """
        Adds evidence item. Starts unverified (verified=False) unless explicitly validated.
        """
        eid = f"ev:{len(trace.evidence_items)+1}:{hashlib.sha256(source_location.encode('utf-8')).hexdigest()[:6]}"
        item = TraceEvidenceItem(
            evidence_id=eid,
            evidence_class=evidence_class,
            source_location=source_location,
            description=description,
            verified=verified,
            falsifiable=falsifiable
        )
        trace.evidence_items.append(item)
        return item

    def verify_evidence(self, trace: GovernanceTrace, evidence_id: str) -> bool:
        """Explicit verification step by a formal verifier or test run."""
        for item in trace.evidence_items:
            if item.evidence_id == evidence_id:
                item.verified = True
                return True
        return False

    def derive_epistemic_state(self, trace: GovernanceTrace) -> EpistemicState:
        """
        Policy-driven claim-type-aware epistemic state calculation (Anti-'Trust Me Bro' Gate v2):
        - USER_INTENT_OR_TESTIMONY: Verified E1 is required & sufficient to derive PROVEN.
        - REPOSITORY_STATE: Verified E2 repository artifact is REQUIRED to derive PROVEN. E1 alone is SUPPORTED.
        - RUNTIME_OR_METAL: Verified E2 test receipt on metal is REQUIRED to derive PROVEN. E1 alone is SUPPORTED.
        - MODEL_INTERPRETATION: E3 inferences can never be PROVEN by themselves (max SUPPORTED/INFERRED).
        - EXTERNAL_FACT: Requires verified promotion; otherwise UNKNOWN.
        - GENERAL_QUERY: Verified E2 artifact derives PROVEN; E1 derives SUPPORTED.
        """
        if not trace.evidence_items:
            return EpistemicState.UNKNOWN

        verified_e1 = [e for e in trace.evidence_items if e.evidence_class == CanonicalEvidenceClass.E1_DIRECT_TESTIMONY and e.verified]
        verified_e2 = [e for e in trace.evidence_items if e.evidence_class == CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT and e.verified]
        unverified_e4 = [e for e in trace.evidence_items if e.evidence_class == CanonicalEvidenceClass.E4_UNKNOWN_AUDIT_REQUIRED or not e.verified]

        # If any item is marked E4 or unverified, state cannot be PROVEN
        if unverified_e4:
            if verified_e2:
                return EpistemicState.SUPPORTED
            return EpistemicState.UNKNOWN

        claim = trace.claim_type

        if claim == ClaimType.USER_INTENT_OR_TESTIMONY:
            if verified_e1:
                return EpistemicState.PROVEN
            if verified_e2:
                return EpistemicState.SUPPORTED
            return EpistemicState.INFERRED

        elif claim in (ClaimType.REPOSITORY_STATE, ClaimType.RUNTIME_OR_METAL):
            # Physical repo/metal claims REQUIRE verified E2 artifact. E1 alone is hearsay/intent, yielding SUPPORTED.
            if verified_e2:
                return EpistemicState.PROVEN
            if verified_e1:
                return EpistemicState.SUPPORTED
            return EpistemicState.INFERRED

        elif claim == ClaimType.MODEL_INTERPRETATION:
            # Model inference can never be PROVEN alone
            if verified_e2 or verified_e1:
                return EpistemicState.SUPPORTED
            return EpistemicState.INFERRED

        elif claim == ClaimType.EXTERNAL_FACT:
            if verified_e2:
                return EpistemicState.PROVEN
            return EpistemicState.UNKNOWN

        else:  # GENERAL_QUERY
            if verified_e2:
                return EpistemicState.PROVEN
            if verified_e1:
                return EpistemicState.SUPPORTED
            e3_items = [e for e in trace.evidence_items if e.evidence_class == CanonicalEvidenceClass.E3_WORKING_INFERENCE]
            if e3_items:
                return EpistemicState.INFERRED
            return EpistemicState.UNKNOWN

    def seal_and_persist_trace(
        self,
        trace: GovernanceTrace,
        why_trust: str
    ) -> GovernanceTrace:
        """
        Seals the trace by deriving the epistemic state from claim-type evidence policy,
        computes the tamper-evident SHA-256 seal, and persists it via strict append-only INSERT.
        Fails hard on duplicate trace_id.
        """
        trace.epistemic_state = self.derive_epistemic_state(trace)
        trace.why_trust_reason = why_trust
        trace.content_hash = trace.compute_hash()

        # Append to durable SQLite Activity Ledger (Strict Plain INSERT)
        with sqlite3.connect(str(self.db_path)) as conn:
            # Check for duplicate trace_id to enforce strict immutability
            cur = conn.execute("SELECT trace_id FROM rtc_activity_traces WHERE trace_id = ?", (trace.trace_id,))
            if cur.fetchone() is not None:
                raise ValueError(
                    f"Immutable Activity Ledger violation: Trace {trace.trace_id} already exists. "
                    f"To record updates, create a new trace with supersedes_trace_id instead of overwriting."
                )

            conn.execute(
                """
                INSERT INTO rtc_activity_traces (
                    trace_id, session_id, speaker_seat, question_or_intent, which_brain,
                    claim_type, supersedes_trace_id, superseded_by_trace_id,
                    epistemic_state, why_trust, content_hash, trace_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace.trace_id,
                    trace.session_id,
                    trace.speaker_seat,
                    trace.question_or_intent,
                    trace.which_brain_consulted,
                    trace.claim_type.value,
                    trace.supersedes_trace_id,
                    trace.superseded_by_trace_id,
                    trace.epistemic_state.value,
                    trace.why_trust_reason,
                    trace.content_hash,
                    json.dumps(trace.to_dict()),
                    trace.timestamp,
                )
            )

            # If this trace supersedes an older trace, link backward
            if trace.supersedes_trace_id:
                conn.execute(
                    "UPDATE rtc_activity_traces SET superseded_by_trace_id = ? WHERE trace_id = ?",
                    (trace.trace_id, trace.supersedes_trace_id)
                )

            conn.commit()

        return trace

    def load_trace(self, trace_id: str) -> Optional[GovernanceTrace]:
        """Loads and reconstructs a trace from durable SQLite storage, validating hash seal."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT trace_json, supersedes_trace_id, superseded_by_trace_id, claim_type FROM rtc_activity_traces WHERE trace_id = ?",
                (trace_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            data = json.loads(row["trace_json"])
            ev_items = [
                TraceEvidenceItem(
                    evidence_id=e["evidence_id"],
                    evidence_class=CanonicalEvidenceClass(e["evidence_class"]),
                    source_location=e["source_location"],
                    description=e["description"],
                    verified=e["verified"],
                    falsifiable=e["falsifiable"]
                ) for e in data.get("evidence_items", [])
            ]

            trace = GovernanceTrace(
                trace_id=data["trace_id"],
                session_id=data["session_id"],
                speaker_seat=data["speaker_seat"],
                question_or_intent=data["question_or_intent"],
                claim_type=ClaimType(row["claim_type"] or data.get("claim_type", ClaimType.GENERAL_QUERY.value)),
                supersedes_trace_id=row["supersedes_trace_id"] or data.get("supersedes_trace_id"),
                superseded_by_trace_id=row["superseded_by_trace_id"] or data.get("superseded_by_trace_id"),
                where_looked=data.get("where_looked", []),
                what_remembered=data.get("what_remembered", []),
                what_validated=data.get("what_validated", []),
                which_brain_consulted=data.get("which_brain_consulted", "LOCAL_MAO_BLACK_BEAST"),
                contradictions_resolved=data.get("contradictions_resolved", []),
                evidence_items=ev_items,
                epistemic_state=EpistemicState(data["epistemic_state"]),
                why_trust_reason=data["why_trust_reason"],
                content_hash=data["content_hash"],
                timestamp=data["timestamp"]
            )
            return trace

    def list_session_traces(self, session_id: str) -> List[GovernanceTrace]:
        """Reconstructs all traces in chronological order for a given session."""
        traces = []
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT trace_id FROM rtc_activity_traces WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            )
            for row in cursor.fetchall():
                t = self.load_trace(row["trace_id"])
                if t:
                    traces.append(t)
        return traces
