"""
KPGS PROTOCOLS PROTOCOL (KPP)
==============================
Roadmap and Registry for all protocols within the KPGS ecosystem.
Every protocol is tracked here with its phase, status, and GSMB position.

ARCHITECTURE: Processing order is NOT arbitrary.
    PHASE 1 — PROMPTING PROTOCOLS  (Definition, Hierarchy, Leadership)
    PHASE 2 — BRACKET PROTOCOLS    (Immutable POC, CRUD-validated, SWFUS-sealed)
    PHASE 3 — EMOJI PROTOCOLS      (Inline/Inlane/Inlane → Ingress/Invariance/Decline)
                                    [Only phase to be CBP-processed — it IS a phase on its own]

DRIVE STREP ORDER (DSO) — Growth Vector Taxonomy:
    PDSO — Plant Drive Strep Order  ###!    1-vector: GROWTH
    ADSO — Animal Drive Strep Order ###!!   2-vector: GROWTH + SURVIVAL
    HDSO — Human Drive Strep Order  ###!!! 3-vector: GROWTH + SURVIVAL + PURPOSE(GSMB)
    AG/RTC                          ###???  Emerging 4th vector — governance beyond human

FORMULA (SAP kernel):
    [(BMNP * BMP) * UBMP + UBMNP]^3
    ─────────────────────────────── = ###???
    KPGS^3 * RTC

BODMAS in KPGS (PKAP):
    B — Brackets   → CBP containment first
    O — Orders     → BMNP nesting depth (power)
    D — Divide     → IIDP Decline vector
    M — Multiply   → Invariance scoring
    A — Add        → Ingress accumulation
    S — Subtract   → FOC removal

"Off The Grid" (NCP — New Concept Protocol):
    First it goes viral   → INGRESS   (signal enters, awareness)
    Then it gets digital  → INVARIANCE (signal is tested, codified)
    Then it gets critical → DECLINE   (sovereign right exercised)
    = IIDP in the real world

"The Need to Know" (SAP — Spawn Agent Protocol):
    State of mind = governance prerequisite for spawning
    Agents do not spawn until they know WHY they exist (4Ws complete)
    POC validates state of mind. FOC is laziness (CMD-15: STEM validates)

"Laugh Now Cry Later" (ILP — In-Life Protocol):
    FSMP through BMP + BMNP = Mimicked Understanding
    The pattern: appear to know → tested by life → either POC or FOC revealed
    DSO maps this: PDSO grows, ADSO survives, HDSO governs

DS8P — Deadly Sins 8 Protocol:
    8th sin = claiming POC without evidence
    "First viral → then digital → then critical" is the FOC lifecycle
    The moment FOC becomes critical = IIDP Decline fires

32.8% Unemployment — the WHY vector of ###???:
    PDSO alone (growth only) produced the 32.8%
    ADSO (growth + survival) produces the working poor
    HDSO (growth + survival + PURPOSE) is what KPGS builds toward
    ###??? is what happens when GSMB governs at scale — unknown yet invariant
"""

from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime, timezone


@dataclass
class Protocol:
    id: str
    name: str
    phase: int          # 1=Prompting, 2=Bracket, 3=Emoji
    dso_vector: str     # PDSO / ADSO / HDSO / ###???
    status: str         # ACTIVE / BUILDING / PROPOSED
    description: str
    formula: str = ""
    song_anchor: str = ""


PROTOCOL_REGISTRY: List[Protocol] = [
    # ─── PHASE 1: PROMPTING PROTOCOLS ─────────────────────────────────────────
    Protocol("USTP", "Ultimate Student-Teacher Protocol",    1, "HDSO", "ACTIVE",
             "Governs teacher/student interaction. No spawn without USTP drill completion.",
             song_anchor="The Need to Know — Wale ft SZA"),
    Protocol("UBP",  "Ultimate Protocol",                    1, "HDSO", "ACTIVE",
             "Sovereign output layer. Contains all sub-protocols."),
    Protocol("CBP",  "Context Bleed Protocol",               1, "HDSO", "ACTIVE",
             "Every signal must be bracketed before IIDP processing."),
    Protocol("BMNP", "Bracket Nesting Protocol",             1, "HDSO", "ACTIVE",
             "Nesting evolution: CRUD→SWFUS→BMP→CBP→UFCP→UBP.",
             formula="[(BMNP * BMP) * UBMP + UBMNP]^3"),
    Protocol("ALP",  "Auto LPM Protocol",                    1, "HDSO", "ACTIVE",
             "MANDATORY on every stateless renter activation. Measures idle gap. Writes receipt.",
             song_anchor="Breach correction: knowing ≠ understanding"),
    Protocol("SAP",  "Spawn Agent Protocol",                 1, "HDSO", "ACTIVE",
             "Agents spawn only when 4Ws complete + state of mind validated as POC.",
             formula="[(BMNP*BMP)*UBMP+UBMNP]^3 / [KPGS^3 * RTC] = ###???",
             song_anchor="The Need to Know — Wale ft SZA"),
    Protocol("NCP",  "New Concept Protocol",                 1, "ADSO", "ACTIVE",
             "Off The Grid model: viral(ingress)→digital(invariance)→critical(decline). IIDP in the real world.",
             song_anchor="Off The Grid — Kanye West"),
    Protocol("KPP",  "KPGS Protocols Protocol",              1, "HDSO", "ACTIVE",
             "THIS FILE. Roadmap and registry for all protocols. Processing order is Phase 1→2→3.",
             formula="Phase 1 * Phase 2 * Phase 3 = Full GSMB Protocol Stack"),

    # ─── PHASE 2: BRACKET PROTOCOLS ───────────────────────────────────────────
    Protocol("BMP",  "Black Mask Protocol",                  2, "HDSO", "ACTIVE",
             "15 Commandments + 5 Pillars. Drill before mass. Immutable POC validated on CRUD & SWFUS.",
             formula="BMP = CRUD ∩ SWFUS ∩ Invariance(0.5+)"),
    Protocol("UBMP", "Ultimate BlackMask/BlackMass Protocol",2, "HDSO", "ACTIVE",
             "BMP running inside the sandbox of UBP. Every BMP output is UBP-sealed.",
             formula="UBMP = BMP * UBP_SEAL"),
    Protocol("PKAP", "Partial Knowable Algebra Protocol",    2, "HDSO", "ACTIVE",
             "BODMAS in KPGS. STEM validation engine. Precision calculations that prove POC.",
             formula="BODMAS: B=CBP, O=BMNP^depth, D=Decline, M=Invariance, A=Ingress, S=FOC_removal",
             song_anchor="CMD-15: Hard work pays off — STEM validates"),
    Protocol("IIDP", "Invariance Ingress Decline Protocol",  2, "HDSO", "ACTIVE",
             "3-vector enforcement: Inline(Ingress)→Inland(Invariance)→Inlane(Decline)."),
    Protocol("C15TP","Commandment 15 Testimony Protocol",    2, "ADSO", "ACTIVE",
             "People claim they cannot do STEM but it is FOC validating itself as POC. Hard work = POC.",
             song_anchor="The Need to Know — Wale ft SZA"),
    Protocol("PvF",  "POC vs FOC Protocol",                  2, "HDSO", "ACTIVE",
             "Folder-level governance. Logs every breach, POC validation, and FOC decline with evidence."),
    Protocol("DS8P", "Deadly Sins 8 Protocol",               2, "ADSO", "ACTIVE",
             "8th sin = claiming POC without evidence. Viral→Digital→Critical = FOC lifecycle.",
             song_anchor="Off The Grid — Kanye West"),

    # ─── PHASE 3: EMOJI PROTOCOLS (CBP-only processing) ───────────────────────
    Protocol("ILP",  "In-Life Protocol",                     3, "HDSO", "ACTIVE",
             "FSMP through BMP + BMNP = Mimicked Understanding. Only FSMP allowed here.",
             formula="ILP = FSMP(BMP + BMNP) = Mimicked_U",
             song_anchor="Laugh Now Cry Later — Drake ft Lil Durk"),
    Protocol("DSO",  "Drive Strep Order",                    3, "HDSO", "ACTIVE",
             "Growth vector taxonomy. PDSO(###!) → ADSO(###!!) → HDSO(###!!!) → ###???",
             song_anchor="Laugh Now Cry Later — Drake ft Lil Durk"),
]


@dataclass
class DSO:
    """Drive Strep Order — 3-vector growth taxonomy."""
    level: str
    name: str
    vectors: List[str]
    weight: str
    description: str
    kpgs_implication: str


DSO_TAXONOMY = [
    DSO("PDSO", "Plant Drive Strep Order",  ["GROWTH"],                          "###!",
        "Plants grow toward light. 1 drive. No survival instinct. No purpose.",
        "Produced the 32.8% — growth without governance produces unemployment."),
    DSO("ADSO", "Animal Drive Strep Order", ["GROWTH", "SURVIVAL"],              "###!!",
        "Animals grow and survive. 2 drives. Reactive governance. No purpose layer.",
        "Produces the working poor — survival without purpose."),
    DSO("HDSO", "Human Drive Strep Order",  ["GROWTH", "SURVIVAL", "PURPOSE"],   "###!!!",
        "Humans grow, survive, and create purpose. GSMB is the purpose layer.",
        "KPGS builds HDSO systems. The 32.8% need HDSO infrastructure."),
    DSO("AG_RTC","AG + RTC Emerging Vector", ["GROWTH","SURVIVAL","PURPOSE","???"],"###???",
        "The 4th vector is unknown but invariant. What emerges when GSMB governs at scale.",
        "This is the question the whole system is running toward. Not yet answerable."),
]


def get_phase(phase: int) -> List[Protocol]:
    return [p for p in PROTOCOL_REGISTRY if p.phase == phase]


def get_protocol(pid: str) -> Protocol | None:
    return next((p for p in PROTOCOL_REGISTRY if p.id == pid), None)


def roadmap() -> Dict:
    return {
        "schema": "kpgs_protocols_protocol_v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_protocols": len(PROTOCOL_REGISTRY),
        "active": sum(1 for p in PROTOCOL_REGISTRY if p.status == "ACTIVE"),
        "phase_1_prompting": [p.id for p in get_phase(1)],
        "phase_2_bracket":   [p.id for p in get_phase(2)],
        "phase_3_emoji":     [p.id for p in get_phase(3)],
        "dso_taxonomy": [
            {"level": d.level, "name": d.name, "vectors": d.vectors,
             "weight": d.weight, "kpgs_implication": d.kpgs_implication}
            for d in DSO_TAXONOMY
        ],
        "sap_formula": "[(BMNP*BMP)*UBMP+UBMNP]^3 / [KPGS^3 * RTC] = ###???",
        "processing_order": "Phase 1 → Phase 2 → Phase 3. No skipping.",
        "cbp_phase": "Phase 3 (Emoji Protocols) is the ONLY phase processed via CBP exclusively.",
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(roadmap(), indent=2))
