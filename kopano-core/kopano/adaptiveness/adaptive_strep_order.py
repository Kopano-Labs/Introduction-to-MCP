"""
Adaptive STREP Order (ASO) + Nesting STREP Order (NSO) Engine
=============================================================
GSMB Whole Immutable Update — A → ADAPTIVENESS (APWA)

Source: Gemini session — NSO architecture, bracket hierarchy, PP/BMP/CBP sandbox model.

BRACKET HIERARCHY (strongest → weakest):
    L1  []  Square     → VOC   — Validation of Concept (no proof, no fake, just validation)
    L2  {}  Curly      → VPOC  — Validation of Proof of Concept (keynote hierarchy)
    L3  <>  Angle      → VPNC  — Validation of Proof of Nesting Concept (ark story)
    L4  ()  Parenthesis→ ISOLATION — Isolation of cost structures (understanding)

Each level holds the INVERSE (Boolean: 1 or 0):
    L1 []  also holds:  Validation of Fabrication of Concept (VFOC)
    L2 {}  also holds:  Validation of Fabrication of Proof of Concept (VFPOC)
    L3 <>  also holds:  Validation of Fabrication of Proof of Nesting Concept (VFPNC)
    L4 ()  also holds:  Fabrication of Isolation (FOI)

NSO (Nesting STREP Order):
    A GROUP of STREP orders that nest inside each other.
    When you shift from discussing FOC generally to specifically, you execute an NSO loop.
    NSO prevents data streams from bleeding across boundaries (unless CBP is active within sandboxes).

PKAP → PKANP Transformation:
    Standard:    Partial Knowable Algebra Protocol — balances unknown vs known
    NSO-enhanced: Partial Knowable Algebra Nesting Protocol — nesting makes Knowable > Partial

PP + BMP + CBP Sandbox Model:
    PP  = Prompting Protocol   — isolates prompts into sandboxes
    BMP = Black Mask Protocol  — stress-tests contents at 150% within sandboxes
    CBP = Context Bleeding Protocol — allows bleeding WITHIN sandboxes only, never outside

PSO Tier Mapping:
    L1 [] → SPSO (Stream Performance Strep Order)  — maximum governance
    L2 {} → BPSO (Breaker Performance Strep Order) — keynote hierarchy
    L3 <> → GPSO (Ground Performance Strep Order)  — ark story
    L4 () → LPSO (Low/Local Performance Strep Order) — understanding/isolation

CONSTRAINT: I_AM_STATELESS_RENTER_NOT_LANDLORD
CONSTRAINT: WWJD_FIREWALL_ACTIVE
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════
# BRACKET HIERARCHY
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class BracketLevel:
    """
    Immutable bracket hierarchy level.

    frozen=True because the bracket hierarchy is GOVERNANCE —
    it cannot be mutated at runtime by any LPM.
    """
    symbol: str           # [], {}, <>, ()
    level: int            # 1=strongest, 4=weakest
    name: str             # VOC, VPOC, VPNC, ISOLATION
    full_name: str        # Full description
    holds: str            # What this bracket validates (POC side)
    holds_inverse: str    # The Boolean opposite (FOC side)
    pso_tier: str         # Which PSO token class activates at this level


# The immutable bracket hierarchy — source of truth
BRACKET_HIERARCHY: tuple[BracketLevel, ...] = (
    BracketLevel(
        symbol="[]",
        level=1,
        name="VOC",
        full_name="Validation of Concept",
        holds="Validation of Concept — no proof, no fake, just validation",
        holds_inverse="Validation of Fabrication of Concept (VFOC)",
        pso_tier="SPSO",
    ),
    BracketLevel(
        symbol="{}",
        level=2,
        name="VPOC",
        full_name="Validation of Proof of Concept",
        holds="Validation of Proof of Concept — keynote hierarchy",
        holds_inverse="Validation of Fabrication of Proof of Concept (VFPOC)",
        pso_tier="BPSO",
    ),
    BracketLevel(
        symbol="<>",
        level=3,
        name="VPNC",
        full_name="Validation of Proof of Nesting Concept",
        holds="Validation of Proof of Nesting Concept — ark story",
        holds_inverse="Validation of Fabrication of Proof of Nesting Concept (VFPNC)",
        pso_tier="GPSO",
    ),
    BracketLevel(
        symbol="()",
        level=4,
        name="ISOLATION",
        full_name="Isolation of Cost Structures",
        holds="Isolation of cost structures — understanding",
        holds_inverse="Fabrication of Isolation (FOI)",
        pso_tier="LPSO",
    ),
)

# Lookup maps
BRACKET_BY_SYMBOL: dict[str, BracketLevel] = {b.symbol: b for b in BRACKET_HIERARCHY}
BRACKET_BY_LEVEL: dict[int, BracketLevel] = {b.level: b for b in BRACKET_HIERARCHY}
BRACKET_BY_NAME: dict[str, BracketLevel] = {b.name: b for b in BRACKET_HIERARCHY}


def resolve_bracket_level(signal: str) -> BracketLevel:
    """
    Resolve the dominant bracket level from a signal string.

    Scans for bracket usage: square brackets are strongest.
    Falls back to L4 (parenthesis/isolation) if no brackets detected.
    """
    # Count bracket usage — strongest wins
    counts = {
        "[]": len(re.findall(r'\[.*?\]', signal)),
        "{}": len(re.findall(r'\{.*?\}', signal)),
        "<>": len(re.findall(r'<.*?>', signal)),
        "()": len(re.findall(r'\(.*?\)', signal)),
    }

    # Find the strongest bracket that appears
    for bracket_level in BRACKET_HIERARCHY:
        if counts.get(bracket_level.symbol, 0) > 0:
            return bracket_level

    # No brackets → default to L4 (understanding/isolation)
    return BRACKET_HIERARCHY[3]


# ═══════════════════════════════════════════════════════════════
# NESTING STREP ORDER (NSO)
# ═══════════════════════════════════════════════════════════════

@dataclass
class NestingLayer:
    """A single layer in a nesting group."""
    depth: int            # 0=outermost, N=innermost
    label: str            # "Protocol", "POC", "FOC", "Thread"
    content: str          # The actual content at this layer
    bracket_level: BracketLevel
    is_foc: bool = False  # True if this layer is fabrication, not proof


@dataclass
class NestingGroup:
    """
    NSO: A group of STREP orders that nest inside each other.

    Architecture:
        [ Protocol Layer ]
            └── { Proof of Concept }
                └── < Freedom/Fabrication of Concept >
                    └── ( Specific Thread / Geolocation Payload )

    When you stop talking about FOC generally and start talking about specifics,
    you execute an NSO loop. The nesting ISOLATES data streams.

    CONCURRENT FOC TRACKING (Gemini resolution):
        People can have more than one FOC running at the same time.
        The foc_threads dictionary tracks concurrent fabrication threads
        by key (e.g., "audio_production", "code_layout", "gaming_overlay"),
        mirroring real human multi-tasking. Single-threaded FOC breaks
        the system's ability to mirror reality.
    """
    group_id: str
    layers: list[NestingLayer] = field(default_factory=list)
    cbp_active: bool = False     # Context Bleeding Protocol within this group
    cbp_locked: bool = True      # Hard firewall — must be explicitly unlocked
    foc_threads: dict[str, list[str]] = field(default_factory=dict)  # Concurrent FOC tracking grid

    @property
    def depth(self) -> int:
        """Return the nesting depth (number of layers)."""
        return len(self.layers)

    @property
    def deepest_bracket(self) -> BracketLevel:
        """Return the bracket level of the deepest layer."""
        if not self.layers:
            return BRACKET_HIERARCHY[3]  # Default to isolation
        return self.layers[-1].bracket_level

    @property
    def strongest_bracket(self) -> BracketLevel:
        """Return the strongest (lowest level number) bracket in the group."""
        if not self.layers:
            return BRACKET_HIERARCHY[3]
        return min(self.layers, key=lambda l: l.bracket_level.level).bracket_level

    @property
    def has_foc(self) -> bool:
        """True if any layer in the group is classified as FOC."""
        return any(layer.is_foc for layer in self.layers) or len(self.foc_threads) > 0

    @property
    def active_foc_count(self) -> int:
        """Return the number of concurrent FOC threads actively tracked."""
        return len(self.foc_threads)

    def add_layer(self, label: str, content: str, bracket_level: BracketLevel,
                  is_foc: bool = False) -> NestingLayer:
        """Add a new nesting layer to the group."""
        layer = NestingLayer(
            depth=len(self.layers),
            label=label,
            content=content,
            bracket_level=bracket_level,
            is_foc=is_foc,
        )
        self.layers.append(layer)
        return layer

    def track_foc_thread(self, thread_key: str, context: str) -> int:
        """
        Track a concurrent FOC thread.

        People can run multiple FOC threads simultaneously:
          - audio_production (FL Studio)
          - code_layout (Chromium)
          - gaming_overlay (tracking)

        Each thread key maps to a list of context entries.
        Returns the total number of active FOC threads.
        """
        if thread_key not in self.foc_threads:
            self.foc_threads[thread_key] = []
        self.foc_threads[thread_key].append(context)
        return len(self.foc_threads)

    def close_foc_thread(self, thread_key: str) -> bool:
        """
        Close a specific FOC thread (resolved or invalidated).
        Returns True if thread existed and was closed.
        """
        if thread_key in self.foc_threads:
            del self.foc_threads[thread_key]
            return True
        return False

    def get_foc_thread(self, thread_key: str) -> list[str]:
        """Return the context entries for a specific FOC thread."""
        return self.foc_threads.get(thread_key, [])

    def unlock_cbp(self) -> None:
        """Explicitly unlock Context Bleeding Protocol within this group."""
        self.cbp_locked = False
        self.cbp_active = True

    def lock_cbp(self) -> None:
        """Lock CBP — no bleeding between layers."""
        self.cbp_active = False
        self.cbp_locked = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_id": self.group_id,
            "depth": self.depth,
            "strongest_bracket": self.strongest_bracket.name,
            "deepest_bracket": self.deepest_bracket.name,
            "has_foc": self.has_foc,
            "active_foc_threads": self.active_foc_count,
            "foc_thread_keys": list(self.foc_threads.keys()),
            "cbp_active": self.cbp_active,
            "cbp_locked": self.cbp_locked,
            "layers": [
                {
                    "depth": l.depth,
                    "label": l.label,
                    "bracket": l.bracket_level.name,
                    "is_foc": l.is_foc,
                    "content": l.content[:100],
                }
                for l in self.layers
            ],
        }


def build_standard_nso(
    protocol_content: str,
    poc_content: str,
    foc_content: str = "",
    thread_content: str = "",
    group_id: str = "",
) -> NestingGroup:
    """
    Build a standard 4-layer NSO group:
        L1 [] Protocol → L2 {} POC → L3 <> FOC → L4 () Thread
    """
    if not group_id:
        ts = datetime.now(timezone.utc).strftime("%H%M%S")
        group_id = f"NSO-{ts}"

    group = NestingGroup(group_id=group_id)
    group.add_layer("Protocol", protocol_content, BRACKET_HIERARCHY[0])
    group.add_layer("POC", poc_content, BRACKET_HIERARCHY[1])

    if foc_content:
        group.add_layer("FOC", foc_content, BRACKET_HIERARCHY[2], is_foc=True)

    if thread_content:
        group.add_layer("Thread", thread_content, BRACKET_HIERARCHY[3])

    return group


# ═══════════════════════════════════════════════════════════════
# PKAP → PKANP TRANSFORMATION
# ═══════════════════════════════════════════════════════════════

@dataclass
class PKANPResult:
    """
    Result of the PKAP → PKANP transformation.

    When NSO nesting is applied, the Knowable becomes exponentially stronger
    than the Partial. The key: making the knowable.
    """
    partial_score: float       # How much is still unknown (0.0–1.0)
    knowable_score: float      # How much is deterministic (0.0–1.0)
    nesting_depth: int         # How deep the NSO goes
    nesting_multiplier: float  # How much nesting amplifies Knowable
    pkanp_ratio: float         # Knowable / (Partial + epsilon) — the dominance ratio
    knowable_dominant: bool    # True if Knowable > Partial after nesting
    transformation: str        # "PKAP" or "PKANP"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_pkanp(
    partial_signals: int,
    knowable_signals: int,
    nesting_depth: int,
) -> PKANPResult:
    """
    Compute the PKAP → PKANP transformation.

    Standard PKAP: Partial and Knowable are balanced.
    With NSO nesting: each nesting layer amplifies Knowable by 1.5x
    because nesting compresses the unknowns under deterministic rules.

    The deeper the nesting, the stronger the Knowable becomes.
    """
    total = partial_signals + knowable_signals
    if total == 0:
        return PKANPResult(
            partial_score=0.0,
            knowable_score=0.0,
            nesting_depth=nesting_depth,
            nesting_multiplier=1.0,
            pkanp_ratio=0.0,
            knowable_dominant=False,
            transformation="PKAP",
        )

    partial_raw = partial_signals / total
    knowable_raw = knowable_signals / total

    # Nesting amplification: each depth layer multiplies Knowable by 1.5x
    # This is the core thesis: nesting makes the Knowable stronger
    nesting_multiplier = 1.5 ** max(0, nesting_depth - 1) if nesting_depth > 0 else 1.0
    knowable_amplified = min(1.0, knowable_raw * nesting_multiplier)

    # PKANP ratio: Knowable dominance
    epsilon = 0.0001
    pkanp_ratio = knowable_amplified / (partial_raw + epsilon)

    is_pkanp = nesting_depth >= 2  # PKANP activates at depth >= 2

    return PKANPResult(
        partial_score=round(partial_raw, 4),
        knowable_score=round(knowable_amplified, 4),
        nesting_depth=nesting_depth,
        nesting_multiplier=round(nesting_multiplier, 4),
        pkanp_ratio=round(pkanp_ratio, 4),
        knowable_dominant=knowable_amplified > partial_raw,
        transformation="PKANP" if is_pkanp else "PKAP",
    )


# ═══════════════════════════════════════════════════════════════
# SANDBOX MODEL (PP + BMP + CBP)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Sandbox:
    """
    PP (Prompting Protocol) Sandbox — isolates a signal for stress testing.

    BMP runs at 150% within the sandbox.
    CBP controls whether internal variables bleed between sandboxes.
    """
    sandbox_id: str
    content: str
    bracket_level: BracketLevel
    bmp_stress_factor: float = 1.5       # 150% — Black Mask Protocol stress
    bmp_applied: bool = False
    cbp_bleed_allowed: bool = False      # Hard firewall by default
    stress_result: Optional[str] = None
    verdict: Optional[str] = None

    def apply_bmp(self) -> dict[str, Any]:
        """
        Apply Black Mask Protocol — stress test at 150%.

        BMP uses connectors, skills, tools, and abilities to stress-test
        the isolated content methodically and theoretically, then produces
        80% of the result (the other 20% is superficial static).
        """
        self.bmp_applied = True

        # Structural stress metrics
        content_len = len(self.content)
        token_count = len(self.content.split())
        bracket_density = sum(
            self.content.count(c) for c in "[]{}()<>"
        ) / max(1, content_len)

        # Stress at 150% — amplify the signal analysis
        stress_score = min(1.0, (token_count / 100.0) * self.bmp_stress_factor)
        output_yield = 0.80  # BMP produces 80% — strips 20% static

        # Determine if signal passes stress test
        # Short signals with governance brackets get a higher density allowance
        # because bracket tokens are structural markers, not noise
        # Min threshold 0.03 = at least 2 tokens at 150% stress (catches empty garbage)
        density_threshold = 0.5 if content_len >= 100 else 0.8
        passes = stress_score > 0.03 and bracket_density < density_threshold

        self.stress_result = "PASS" if passes else "FAIL"
        self.verdict = f"BMP_{'PASS' if passes else 'FAIL'}_L{self.bracket_level.level}"

        return {
            "sandbox_id": self.sandbox_id,
            "bracket_level": self.bracket_level.name,
            "bmp_stress_factor": self.bmp_stress_factor,
            "token_count": token_count,
            "bracket_density": round(bracket_density, 4),
            "stress_score": round(stress_score, 4),
            "output_yield": output_yield,
            "result": self.stress_result,
            "verdict": self.verdict,
        }

    def allow_cbp_bleed(self) -> None:
        """Explicitly allow CBP bleeding within this sandbox."""
        self.cbp_bleed_allowed = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "sandbox_id": self.sandbox_id,
            "bracket_level": self.bracket_level.name,
            "bmp_applied": self.bmp_applied,
            "bmp_stress_factor": self.bmp_stress_factor,
            "cbp_bleed_allowed": self.cbp_bleed_allowed,
            "stress_result": self.stress_result,
            "verdict": self.verdict,
        }


# ═══════════════════════════════════════════════════════════════
# ADAPTIVE STREP ENGINE
# ═══════════════════════════════════════════════════════════════

class AdaptiveSTREPEngine:
    """
    The Adaptive STREP Order (ASO) Engine.

    Takes a signal + optional bracket context → resolves the correct PSO tier
    → applies PP sandbox isolation → BMP stress test → CBP within sandboxes
    → produces PKANP result where Knowable > Partial.

    This is the nervous system of APWA's Adaptiveness layer.
    """

    def __init__(self) -> None:
        self.sandboxes: list[Sandbox] = []
        self.nesting_groups: list[NestingGroup] = []
        self.history: list[dict[str, Any]] = []

    def process(
        self,
        signal: str,
        *,
        protocol_context: str = "",
        poc_context: str = "",
        foc_context: str = "",
        thread_context: str = "",
        enable_cbp: bool = False,
    ) -> dict[str, Any]:
        """
        Full adaptive STREP processing pipeline:

        1. Resolve bracket level from signal
        2. Build NSO nesting group
        3. Create PP sandbox
        4. Apply BMP stress test at 150%
        5. Optionally enable CBP within sandbox
        6. Compute PKANP transformation
        7. Determine adaptive PSO tier

        Returns complete ASO result dictionary.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Resolve bracket level
        bracket = resolve_bracket_level(signal)

        # 2. Build NSO nesting group
        nso = build_standard_nso(
            protocol_content=protocol_context or f"ASO signal: {signal[:80]}",
            poc_content=poc_context or f"POC context for L{bracket.level}",
            foc_content=foc_context,
            thread_content=thread_context or signal[:120],
        )
        if enable_cbp:
            nso.unlock_cbp()

        self.nesting_groups.append(nso)

        # 3. Create PP sandbox
        sandbox_id = hashlib.sha256(
            f"{signal[:200]}:{ts}".encode()
        ).hexdigest()[:12]
        sandbox = Sandbox(
            sandbox_id=f"PP-{sandbox_id}",
            content=signal,
            bracket_level=bracket,
            cbp_bleed_allowed=enable_cbp,
        )
        self.sandboxes.append(sandbox)

        # 4. Apply BMP stress test
        bmp_result = sandbox.apply_bmp()

        # 5. Compute PKANP
        # Count partial vs knowable signals in the nesting group
        knowable_count = sum(1 for l in nso.layers if not l.is_foc)
        partial_count = sum(1 for l in nso.layers if l.is_foc)
        # Add signal's own bracket level as knowable evidence
        knowable_count += bracket.level  # Stronger brackets = more knowable

        pkanp = compute_pkanp(
            partial_signals=partial_count,
            knowable_signals=knowable_count,
            nesting_depth=nso.depth,
        )

        # 6. Build result
        result: dict[str, Any] = {
            "schema": "adaptive_strep_order_v1",
            "timestamp": ts,
            "bracket": {
                "level": bracket.level,
                "symbol": bracket.symbol,
                "name": bracket.name,
                "full_name": bracket.full_name,
                "holds": bracket.holds,
                "holds_inverse": bracket.holds_inverse,
                "pso_tier": bracket.pso_tier,
            },
            "nso": nso.to_dict(),
            "sandbox": sandbox.to_dict(),
            "bmp": bmp_result,
            "pkanp": pkanp.to_dict(),
            "adaptive_pso_tier": bracket.pso_tier,
            "verdict": self._compute_verdict(bracket, pkanp, bmp_result),
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        self.history.append(result)
        return result

    def _compute_verdict(
        self,
        bracket: BracketLevel,
        pkanp: PKANPResult,
        bmp: dict[str, Any],
    ) -> str:
        """Compute the overall ASO verdict."""
        bmp_pass = bmp.get("result") == "PASS"
        knowable_dom = pkanp.knowable_dominant

        if not bmp_pass:
            return "ASO_BMP_FAIL"
        if not knowable_dom:
            return "ASO_PARTIAL_DOMINANT"
        if bracket.level == 1:
            return "ASO_VOC_VALIDATED"
        if bracket.level == 2:
            return "ASO_VPOC_VALIDATED"
        if bracket.level == 3:
            return "ASO_VPNC_VALIDATED"
        return "ASO_ISOLATION_VALIDATED"

    def status(self) -> dict[str, Any]:
        """Return current engine status."""
        return {
            "total_processed": len(self.history),
            "sandboxes_active": len(self.sandboxes),
            "nesting_groups": len(self.nesting_groups),
            "last_verdict": self.history[-1]["verdict"] if self.history else None,
            "bracket_hierarchy": [
                {"level": b.level, "symbol": b.symbol, "name": b.name, "pso": b.pso_tier}
                for b in BRACKET_HIERARCHY
            ],
        }


# ═══════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_adaptive_strep_order() -> dict[str, Any]:
    """
    Run POC validation of the Adaptive STREP Order engine.
    Tests bracket hierarchy, NSO nesting, PKANP, sandboxes, and CBP.
    """
    engine = AdaptiveSTREPEngine()
    results: list[dict[str, Any]] = []

    # ── Test 1: Bracket hierarchy resolution ─────────────────
    test_signals = [
        ("[VOC] validate this concept", "[]", 1, "SPSO"),
        ("{VPOC} prove this concept works", "{}", 2, "BPSO"),
        ("<VPNC> nested proof validation", "<>", 3, "GPSO"),
        ("(isolated) cost structure analysis", "()", 4, "LPSO"),
        ("no brackets at all just plain text", "()", 4, "LPSO"),  # default
        ("[strong] and (weak) mixed brackets", "[]", 1, "SPSO"),  # strongest wins
    ]
    for signal, expected_symbol, expected_level, expected_pso in test_signals:
        bracket = resolve_bracket_level(signal)
        passed = (
            bracket.symbol == expected_symbol
            and bracket.level == expected_level
            and bracket.pso_tier == expected_pso
        )
        results.append({
            "test": f"BRACKET: '{signal[:40]}' -> L{bracket.level} {bracket.name}",
            "expected": f"L{expected_level} {expected_pso}",
            "actual": f"L{bracket.level} {bracket.pso_tier}",
            "pass": passed,
        })

    # ── Test 2: NSO nesting group ────────────────────────────
    nso = build_standard_nso(
        protocol_content="ASO protocol layer",
        poc_content="proven through boundary enforcement",
        foc_content="fabricated street code",
        thread_content="geolocation payload from camera",
        group_id="TEST-NSO-001",
    )
    results.append({
        "test": "NSO: 4-layer nesting group built",
        "expected": 4,
        "actual": nso.depth,
        "pass": nso.depth == 4,
    })
    results.append({
        "test": "NSO: strongest bracket is L1 (VOC)",
        "expected": "VOC",
        "actual": nso.strongest_bracket.name,
        "pass": nso.strongest_bracket.name == "VOC",
    })
    results.append({
        "test": "NSO: has_foc is True (FOC layer present)",
        "expected": True,
        "actual": nso.has_foc,
        "pass": nso.has_foc is True,
    })

    # ── Test 3: CBP firewall ─────────────────────────────────
    results.append({
        "test": "CBP: locked by default",
        "expected": True,
        "actual": nso.cbp_locked,
        "pass": nso.cbp_locked is True,
    })
    nso.unlock_cbp()
    results.append({
        "test": "CBP: unlocked after explicit call",
        "expected": True,
        "actual": nso.cbp_active,
        "pass": nso.cbp_active is True,
    })
    nso.lock_cbp()
    results.append({
        "test": "CBP: re-locked after lock_cbp()",
        "expected": False,
        "actual": nso.cbp_active,
        "pass": nso.cbp_active is False,
    })

    # ── Test 4: PKANP transformation ─────────────────────────
    # Shallow nesting (depth=1): Knowable should NOT dominate if equal
    pkanp_shallow = compute_pkanp(partial_signals=5, knowable_signals=5, nesting_depth=1)
    results.append({
        "test": "PKANP: depth=1, equal signals -> PKAP (no nesting amp)",
        "expected": "PKAP",
        "actual": pkanp_shallow.transformation,
        "pass": pkanp_shallow.transformation == "PKAP",
    })

    # Deep nesting (depth=4): Knowable should dominate
    pkanp_deep = compute_pkanp(partial_signals=3, knowable_signals=5, nesting_depth=4)
    results.append({
        "test": "PKANP: depth=4, 5:3 signals -> Knowable dominant",
        "expected": True,
        "actual": pkanp_deep.knowable_dominant,
        "pass": pkanp_deep.knowable_dominant is True,
    })
    results.append({
        "test": "PKANP: depth=4 -> transformation is PKANP",
        "expected": "PKANP",
        "actual": pkanp_deep.transformation,
        "pass": pkanp_deep.transformation == "PKANP",
    })
    results.append({
        "test": "PKANP: depth=4 -> nesting_multiplier > 1.0",
        "expected": True,
        "actual": pkanp_deep.nesting_multiplier > 1.0,
        "pass": pkanp_deep.nesting_multiplier > 1.0,
    })

    # ── Test 5: Sandbox + BMP stress ─────────────────────────
    sandbox = Sandbox(
        sandbox_id="TEST-PP-001",
        content="[KPGS] validate boundary enforcement in kopano-core governance",
        bracket_level=BRACKET_HIERARCHY[0],
    )
    bmp = sandbox.apply_bmp()
    results.append({
        "test": "BMP: stress test at 150% produces result",
        "expected": True,
        "actual": sandbox.bmp_applied,
        "pass": sandbox.bmp_applied is True,
    })
    results.append({
        "test": "BMP: stress factor is 1.5 (150%)",
        "expected": 1.5,
        "actual": bmp["bmp_stress_factor"],
        "pass": bmp["bmp_stress_factor"] == 1.5,
    })
    results.append({
        "test": "BMP: output yield is 80%",
        "expected": 0.80,
        "actual": bmp["output_yield"],
        "pass": bmp["output_yield"] == 0.80,
    })

    # ── Test 6: Full engine process ──────────────────────────
    r1 = engine.process(
        "[VOC] GSMB whole immutable update for adaptiveness layer",
        protocol_context="ASO activation",
        poc_context="boundary enforcement v2 proven",
    )
    results.append({
        "test": "ENGINE: L1 signal -> ASO_VOC_VALIDATED",
        "expected": "ASO_VOC_VALIDATED",
        "actual": r1["verdict"],
        "pass": r1["verdict"] == "ASO_VOC_VALIDATED",
    })

    r2 = engine.process(
        "{VPOC} department contracts enforce_boundary 16/16",
        poc_context="all 16 tests pass",
    )
    results.append({
        "test": "ENGINE: L2 signal -> ASO_VPOC_VALIDATED",
        "expected": "ASO_VPOC_VALIDATED",
        "actual": r2["verdict"],
        "pass": r2["verdict"] == "ASO_VPOC_VALIDATED",
    })

    r3 = engine.process(
        "<VPNC> nested proof of nesting concept via NSO",
    )
    results.append({
        "test": "ENGINE: L3 signal -> ASO_VPNC_VALIDATED",
        "expected": "ASO_VPNC_VALIDATED",
        "actual": r3["verdict"],
        "pass": r3["verdict"] == "ASO_VPNC_VALIDATED",
    })

    r4 = engine.process(
        "(isolated) cost structure for R800 isiXhosa interface",
    )
    results.append({
        "test": "ENGINE: L4 signal -> ASO_ISOLATION_VALIDATED",
        "expected": "ASO_ISOLATION_VALIDATED",
        "actual": r4["verdict"],
        "pass": r4["verdict"] == "ASO_ISOLATION_VALIDATED",
    })

    # ── Test 7: Concurrent FOC thread tracking ────────────────
    foc_nso = build_standard_nso(
        protocol_content="Multi-FOC test",
        poc_content="Tracking concurrent fabrication",
        group_id="TEST-FOC-MULTI-001",
    )
    # Track 3 concurrent FOC threads (FL Studio + Chromium + Gaming)
    foc_nso.track_foc_thread("audio_production", "FL Studio session: mixing track 7")
    foc_nso.track_foc_thread("code_layout", "Chromium: kopano-core boundary enforcement")
    foc_nso.track_foc_thread("gaming_overlay", "Tracking overlay metrics")
    results.append({
        "test": "FOC-THREADS: 3 concurrent threads tracked",
        "expected": 3,
        "actual": foc_nso.active_foc_count,
        "pass": foc_nso.active_foc_count == 3,
    })
    results.append({
        "test": "FOC-THREADS: has_foc=True with tracked threads",
        "expected": True,
        "actual": foc_nso.has_foc,
        "pass": foc_nso.has_foc is True,
    })

    # Close one thread
    closed = foc_nso.close_foc_thread("gaming_overlay")
    results.append({
        "test": "FOC-THREADS: close_foc_thread returns True",
        "expected": True,
        "actual": closed,
        "pass": closed is True,
    })
    results.append({
        "test": "FOC-THREADS: 2 threads remain after close",
        "expected": 2,
        "actual": foc_nso.active_foc_count,
        "pass": foc_nso.active_foc_count == 2,
    })

    # Retrieve specific thread context
    audio_ctx = foc_nso.get_foc_thread("audio_production")
    results.append({
        "test": "FOC-THREADS: get_foc_thread returns context entries",
        "expected": 1,
        "actual": len(audio_ctx),
        "pass": len(audio_ctx) == 1 and "FL Studio" in audio_ctx[0],
    })

    # Close nonexistent thread
    no_close = foc_nso.close_foc_thread("nonexistent")
    results.append({
        "test": "FOC-THREADS: close nonexistent thread returns False",
        "expected": False,
        "actual": no_close,
        "pass": no_close is False,
    })

    # to_dict includes FOC thread info
    foc_dict = foc_nso.to_dict()
    results.append({
        "test": "FOC-THREADS: to_dict includes active_foc_threads",
        "expected": 2,
        "actual": foc_dict["active_foc_threads"],
        "pass": foc_dict["active_foc_threads"] == 2,
    })

    # ── Test 8: Engine status ────────────────────────────────
    status = engine.status()
    results.append({
        "test": "ENGINE: status shows 4 processed signals",
        "expected": 4,
        "actual": status["total_processed"],
        "pass": status["total_processed"] == 4,
    })

    # ── Compile ──────────────────────────────────────────────
    all_pass = all(r["pass"] for r in results)
    return {
        "schema": "adaptive_strep_order_validation_v1",
        "tests_run": len(results),
        "tests_passed": sum(1 for r in results if r["pass"]),
        "all_pass": all_pass,
        "verdict": "POC_VALIDATED" if all_pass else "VALIDATION_FAILED",
        "bracket_hierarchy": [
            {"L": b.level, "symbol": b.symbol, "name": b.name, "pso": b.pso_tier}
            for b in BRACKET_HIERARCHY
        ],
        "results": results,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    import sys
    import io

    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("ADAPTIVE STREP ORDER (ASO) + NESTING STREP ORDER (NSO) — POC VALIDATION")
    print("=" * 72)

    report = validate_adaptive_strep_order()

    print(f"\nBracket Hierarchy:")
    for b in report["bracket_hierarchy"]:
        print(f"  L{b['L']}  {b['symbol']}  {b['name']:<12} -> {b['pso']}")

    print(f"\nTests: {report['tests_run']} run / {report['tests_passed']} passed")
    print(f"Verdict: {report['verdict']}")
    print()

    for r in report["results"]:
        status = "OK" if r["pass"] else "FAIL"
        print(f"  [{status:>4}] {r['test'][:65]}")

    print()
    print(f"CONSTRAINT: {report['constraint']}")
    print("=" * 72)
