"""
OBSERVABLE COGNITION SURFACE & RTC GOVERNANCE TRACE ENGINE
===========================================================
"Evidence is truth-pressure. Governance is continuity."
"Show me what the system is doing to earn the answer."

Distinction:
Not dumping a massive secret hidden chain-of-thought monologue,
but making the governance movement observable, inspectable, and accountable:
- Where did you look?
- What did you remember?
- What did you validate?
- Which brain did you consult?
- What contradicted what?
- What evidence survived?
- Why should I trust the resulting state?

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class EpistemicState(str, Enum):
    PROVEN = "PROVEN"          # E1: Cryptographic or 100% deterministic test on metal
    SUPPORTED = "SUPPORTED"    # E2: Grounded in Schematics / verified vault contracts
    INFERRED = "INFERRED"      # E3: Logical synthesis under human alignment
    UNKNOWN = "UNKNOWN"        # E4: Unverified / pending research


@dataclass
class EvidenceItem:
    evidence_id: str
    source_type: str  # "LOCAL_GSMB", "CLOUD_GSMB", "GOOGLE_DRIVE", "CONVERSATION_HISTORY", "METAL_TEST"
    path_or_uri: str
    description: str
    verified: bool = True


@dataclass
class GovernanceTrace:
    trace_id: str
    speaker_seat: str  # e.g., "SEAT_01_KC", "SEAT_02_CASSEY", "SEAT_10_ANTIGRAVITY", "FORGE"
    question_or_intent: str
    where_looked: List[str] = field(default_factory=list)
    what_remembered: List[str] = field(default_factory=list)
    what_validated: List[str] = field(default_factory=list)
    which_brain_consulted: str = "LOCAL_MAO_BLACK_BEAST"  # "LOCAL_MAO", "CLOUD_MMAO", "HYBRID_REFLECTED"
    contradictions_resolved: List[str] = field(default_factory=list)
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    epistemic_state: EpistemicState = EpistemicState.SUPPORTED
    why_trust_reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["epistemic_state"] = self.epistemic_state.value
        return data

    def to_visual_card(self) -> str:
        """Renders the canonical Observable Cognition Surface ASCII card for desktop UI."""
        evidence_summary = "\n".join(f"  • [{e.source_type}] {e.description} ({e.path_or_uri})" for e in self.evidence_items) or "  • None attached"
        where_summary = "\n".join(f"  ✓ {w}" for w in self.where_looked) or "  ✓ Direct context"
        val_summary = "\n".join(f"  ✓ {v}" for v in self.what_validated) or "  ✓ Invariant checks"

        return f"""┌────────────────────────────────────────────────────────────────────────────┐
│ OBSERVABLE COGNITION SURFACE — RTC ACTIVITY LEDGER                         │
├────────────────────────────────────────────────────────────────────────────┤
│ SPEAKER / SEAT: {self.speaker_seat}
│ INTENT:         {self.question_or_intent}
│ BRAIN:          {self.which_brain_consulted}
├────────────────────────────────────────────────────────────────────────────┤
│ GOVERNANCE TRACE:
{where_summary}
{val_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ EVIDENCE SURVIVED:
{evidence_summary}
├────────────────────────────────────────────────────────────────────────────┤
│ EPISTEMIC STATE: [{self.epistemic_state.value}]
│ PROVENANCE:      {self.why_trust_reason}
└────────────────────────────────────────────────────────────────────────────┘"""


class GovernanceTraceEngine:
    """
    Builds, manages, and validates observable cognition traces across the estate.
    """

    def __init__(self):
        self.traces: List[GovernanceTrace] = []

    def start_trace(
        self,
        speaker_seat: str,
        question_or_intent: str,
        which_brain: str = "LOCAL_MAO_BLACK_BEAST"
    ) -> GovernanceTrace:
        trace_id = f"trace:{int(time.time()*1000)}:{hashlib.sha256(question_or_intent.encode('utf-8')).hexdigest()[:8]}"
        trace = GovernanceTrace(
            trace_id=trace_id,
            speaker_seat=speaker_seat,
            question_or_intent=question_or_intent,
            which_brain_consulted=which_brain
        )
        self.traces.append(trace)
        return trace

    def record_search(self, trace: GovernanceTrace, source: str) -> None:
        if source not in trace.where_looked:
            trace.where_looked.append(source)

    def record_memory(self, trace: GovernanceTrace, memory_snippet: str) -> None:
        trace.what_remembered.append(memory_snippet)

    def record_validation(self, trace: GovernanceTrace, check_desc: str) -> None:
        trace.what_validated.append(check_desc)

    def add_evidence(
        self,
        trace: GovernanceTrace,
        source_type: str,
        path_or_uri: str,
        description: str,
        verified: bool = True
    ) -> None:
        eid = f"ev:{len(trace.evidence_items)+1}:{hashlib.sha256(path_or_uri.encode('utf-8')).hexdigest()[:6]}"
        item = EvidenceItem(
            evidence_id=eid,
            source_type=source_type,
            path_or_uri=path_or_uri,
            description=description,
            verified=verified
        )
        trace.evidence_items.append(item)

    def seal_trace(
        self,
        trace: GovernanceTrace,
        state: EpistemicState,
        why_trust: str
    ) -> GovernanceTrace:
        trace.epistemic_state = state
        trace.why_trust_reason = why_trust
        return trace
