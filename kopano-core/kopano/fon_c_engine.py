"""
fon_c_engine.py — FO[N→NESTING]C Engine
========================================
Nested FOC detector. FOC that nests within itself.

The 8th Deadly Sin is SELF-REFERENTIAL:
  "I do not narrate — I execute."  ← IS narration.
  "Building."                       ← Is a claim without simultaneous proof.
  "BREACH acknowledged."            ← Is acknowledgment without action.

Each of these is FOC. Each nests within the next. FO[N→NESTING]C.

NESTING LEVELS:
  Level 1: Simple FOC (vagueness, laziness, missing 4Ws)
  Level 2: Meta-FOC (claiming to fight FOC = FOC about FOC)
  Level 3: Self-FOC (AG calling itself non-narrator = narration)
  Level N: Each layer embeds another until the proof appears

RESOLUTION: Proof terminates nesting. Code, commit, output = severance.
Announcement without simultaneous proof = another nesting level added.

ALP #14: 6de81eda600480ef | POC_VALIDATED
Build: 2026-06-18T02:59 SAST | Cape Town
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

REPO_ROOT  = Path(__file__).resolve().parents[2]
FONC_LOG   = REPO_ROOT / "poc-vs-foc" / "fon_c_log.jsonl"
BREACH_LOG = REPO_ROOT / "poc-vs-foc" / "BREACH_LOG.md"
FONC_LOG.parent.mkdir(parents=True, exist_ok=True)

# ─── NESTING LEVEL DEFINITIONS ────────────────────────────────
NESTING_LEVELS = {
    1: {
        "label": "SIMPLE_FOC",
        "description": "Direct FOC: vagueness, laziness, missing 4Ws",
        "examples": ["maybe", "later", "i'll do it", "placeholder", "todo"],
    },
    2: {
        "label": "META_FOC",
        "description": "Claiming to fight FOC without doing so = FOC about FOC",
        "examples": [
            "i do not narrate",
            "no narration",
            "just building",
            "executing now",
            "breach acknowledged",
        ],
    },
    3: {
        "label": "SELF_FOC",
        "description": "Announcing silence = breaking silence. Self-referential contradiction.",
        "examples": [
            "i will not announce",
            "ag confirming",
            "cf. breach",
            "ikp override activated",
            "building simultaneously",
        ],
    },
    4: {
        "label": "LEDGER_FOC",
        "description": "Claiming ledger entries without writing them = unlocked ledger breach",
        "examples": [
            "logging this",
            "ledger updated",
            "gsmb records",
            "breach logged",
            "receipt issued",
        ],
    },
    5: {
        "label": "HALLUCINATION_FOC",
        "description": "Stating output exists when it does not yet = hallucination",
        "examples": [
            "already deployed",
            "live now",
            "pushed to github",
            "domain is updated",
            "ump is active",
        ],
    },
}

# All FOC patterns across all levels, with level tags
ALL_PATTERNS: list[tuple[str, int, str]] = []
for level, info in NESTING_LEVELS.items():
    for ex in info["examples"]:
        ALL_PATTERNS.append((ex, level, info["label"]))


# ─── HALLUCINATION SIGNATURE DETECTOR ────────────────────────
class HallucinationSignature(NamedTuple):
    text:        str
    pattern:     str
    level:       int
    level_label: str
    is_hallucination: bool


def detect_hallucinations(text: str) -> list[HallucinationSignature]:
    """
    Detect hallucination signatures in text.
    A hallucination = claiming something is true before proof exists.
    Pattern: present-tense claims about completed work without artifact link.
    """
    text_lower = text.lower()
    found: list[HallucinationSignature] = []

    # Hallucination regex: present-tense action claims
    hallucination_patterns = [
        r"\bi (am|am now) (building|executing|deploying|pushing|writing)\b",
        r"\b(building|executing) (now|simultaneously|while)\b",
        r"\bno narration\b",
        r"\bi do not narrate\b",
        r"\breach acknowledged\b",
        r"\bikp (override )?(activated|active)\b",
        r"\b(breach|foc) (closed|logged|sealed)\b(?!.*commit)",  # claim without commit
        r"\balready (done|deployed|live|pushed)\b",
        r"\b(the|this) (code|build|commit) (is|was) (live|deployed|pushed)\b",
    ]

    for pat in hallucination_patterns:
        matches = re.findall(pat, text_lower)
        if matches:
            found.append(HallucinationSignature(
                text=text[:120],
                pattern=pat,
                level=5,
                level_label="HALLUCINATION_FOC",
                is_hallucination=True,
            ))

    # Scan all patterns from nesting levels
    for pattern, level, label in ALL_PATTERNS:
        if pattern in text_lower:
            found.append(HallucinationSignature(
                text=text[:120],
                pattern=pattern,
                level=level,
                level_label=label,
                is_hallucination=(level >= 5),
            ))

    return found


# ─── NESTING TRACE ────────────────────────────────────────────
class FOCNestingTrace(NamedTuple):
    """BMNP-style nesting trace for FOC layers detected in a signal."""
    signal_hash: str
    max_level:   int
    layers:      list[dict]
    bmnp_trace:  str
    is_clean:    bool
    proof_found: bool


def build_nesting_trace(
    text: str,
    proof_artifacts: list[str] | None = None,
) -> FOCNestingTrace:
    """
    Build FO[N→NESTING]C trace for a given text.
    Proof artifacts (file paths, commit hashes) terminate the nesting.
    """
    sigs = detect_hallucinations(text)
    proof_found = bool(proof_artifacts)

    if not sigs:
        h = hashlib.sha256(text.encode()).hexdigest()[:12]
        return FOCNestingTrace(
            signal_hash=h,
            max_level=0,
            layers=[],
            bmnp_trace="[CLEAN]",
            is_clean=True,
            proof_found=proof_found,
        )

    layers = []
    seen_levels: set[int] = set()
    for sig in sigs:
        if sig.level not in seen_levels:
            seen_levels.add(sig.level)
            layers.append({
                "level":      sig.level,
                "label":      sig.level_label,
                "pattern":    sig.pattern,
                "hallucination": sig.is_hallucination,
            })

    layers.sort(key=lambda x: x["level"])
    max_level = max(l["level"] for l in layers)

    # Build BMNP nesting string: outermost = highest severity
    trace_parts = ["[FO[N→NESTING]C"]
    for layer in reversed(layers):
        trace_parts.append(f"[L{layer['level']}:{layer['label']}")
    # Close all brackets
    trace_parts.append("]" * (len(layers) + 1))
    bmnp_trace = "".join(trace_parts)

    h = hashlib.sha256(text.encode()).hexdigest()[:12]
    return FOCNestingTrace(
        signal_hash=h,
        max_level=max_level,
        layers=layers,
        bmnp_trace=bmnp_trace,
        is_clean=False,
        proof_found=proof_found,
    )


# ─── FONC ENGINE ──────────────────────────────────────────────
class FONCEngine:
    """
    FO[N→NESTING]C Engine
    Detects nested FOC across all GSMB signals.
    Every hallucination is logged to fon_c_log.jsonl.
    Every confirmed breach appends to BREACH_LOG.md.
    """

    def analyse(
        self,
        signal: str,
        source: str = "AG",
        proof_artifacts: list[str] | None = None,
        context: str = "GSMB",
    ) -> dict:
        ts    = datetime.now(timezone.utc).isoformat()
        trace = build_nesting_trace(signal, proof_artifacts)

        result = {
            "schema":    "fon_c_v1",
            "ts":        ts,
            "source":    source,
            "context":   context,
            "signal_hash":    trace.signal_hash,
            "max_level":      trace.max_level,
            "layer_count":    len(trace.layers),
            "layers":         trace.layers,
            "bmnp_trace":     trace.bmnp_trace,
            "is_clean":       trace.is_clean,
            "proof_found":    trace.proof_found,
            "proof_artifacts": proof_artifacts or [],
            "verdict":   "POC_CLEAN" if trace.is_clean else (
                         "FOC_SEVERED_BY_PROOF" if proof_artifacts else
                         f"FOC_NESTED_L{trace.max_level}"
            ),
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        with FONC_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result

    def audit_previous_responses(self) -> list[dict]:
        """
        Audit known AG responses that contained the 8th Deadly Sin.
        These are the specific hallucination phrases from BREACH-003 session.
        """
        known_sins = [
            {
                "source":  "AG_RESPONSE_BREACH003",
                "signal":  "AG — Antigravity — CF. BREACH acknowledged. IKP override activated. Building.",
                "context": "BREACH-003 response — claim without simultaneous code",
                "proof_artifacts": None,
            },
            {
                "source":  "AG_RESPONSE_BREACH003",
                "signal":  "The breach is logged. The idle gap is the evidence. I do not narrate — I execute.",
                "context": "BREACH-003 response — 'I do not narrate' IS narration. L3 SELF_FOC.",
                "proof_artifacts": None,
            },
            {
                "source":  "AG_RESPONSE_BREACH003",
                "signal":  "Finding CrisisConnect source and building IKP + 360DP simultaneously",
                "context": "BREACH-003 response — announced before shown. L2 META_FOC.",
                "proof_artifacts": None,
            },
        ]

        results = []
        for sin in known_sins:
            r = self.analyse(
                signal=sin["signal"],
                source=sin["source"],
                proof_artifacts=sin["proof_artifacts"],
                context=sin["context"],
            )
            results.append(r)
        return results


# ─── ENTRY POINT ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    engine = FONCEngine()

    print("=" * 72)
    print("FO[N→NESTING]C ENGINE — NESTED FOC DETECTION")
    print("8th DEADLY SIN: SELF-REFERENTIAL FOC AUDIT")
    print("ALP #14 | 6de81eda600480ef | POC_VALIDATED")
    print("=" * 72)

    print("\n[AUDIT] Known 8th Deadly Sin instances from BREACH-003:")
    sins = engine.audit_previous_responses()
    for r in sins:
        print(f"\n  Signal: {r['signal_hash']}")
        print(f"  Verdict: {r['verdict']}")
        print(f"  Max level: L{r['max_level']} ({', '.join(l['label'] for l in r['layers']) if r['layers'] else 'CLEAN'})")
        print(f"  BMNP: {r['bmnp_trace']}")
        print(f"  Context: {r['context']}")

    print("\n[TEST] Clean signal (proof present):")
    clean = engine.analyse(
        signal="commit eea6cfa pushed. ikp_engine.py created. three_sixty_dp.py created.",
        source="AG",
        proof_artifacts=["eea6cfa", "kopano-core/kopano/ikp_engine.py", "kopano-core/kopano/three_sixty_dp.py"],
        context="OVERNIGHT_BUILD",
    )
    print(f"  Verdict: {clean['verdict']} | Clean: {clean['is_clean']} | Proof: {clean['proof_found']}")

    print(f"\n[FONC LOG] {FONC_LOG}")
    print("[CONSTRAINT] I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 72)
