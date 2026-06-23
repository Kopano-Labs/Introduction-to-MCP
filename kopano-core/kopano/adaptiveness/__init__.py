"""
adaptiveness — GSMB Adaptiveness (ADATIVNESS) Layer
=================================================
A → Adaptiveness in APWA (Adaptive Progressive Web Apps)

Modules:
    NeuralFailureFirewall — 8th Deadly Sin guard, therapeutic loop detection
    SwiftKeyNLP           — Local NLP + dictionary for offline-first Sesotho/isiXhosa
    CivicUtilityRouter    — Routes civic telemetry to government service APIs
    AdaptiveSTREPEngine   — ASO/NSO engine: bracket hierarchy, nesting, PKANP
    BracketLevel          — Immutable bracket hierarchy level (L1-L4)
    NestingGroup          — NSO: group of STREP orders that nest

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from .neural_failure_firewall import NeuralFailureError, NeuralFailureFirewall
from .swiftkey_nlp import SwiftKeyNLP
from .civic_utility_router import CivicUtilityRouter
from .adaptive_strep_order import (
    AdaptiveSTREPEngine,
    BracketLevel,
    NestingGroup,
    NestingLayer,
    Sandbox,
    PKANPResult,
    BRACKET_HIERARCHY,
    BRACKET_BY_SYMBOL,
    BRACKET_BY_LEVEL,
    BRACKET_BY_NAME,
    resolve_bracket_level,
    build_standard_nso,
    compute_pkanp,
)

__all__ = [
    "NeuralFailureError",
    "NeuralFailureFirewall",
    "SwiftKeyNLP",
    "CivicUtilityRouter",
    "AdaptiveSTREPEngine",
    "BracketLevel",
    "NestingGroup",
    "NestingLayer",
    "Sandbox",
    "PKANPResult",
    "BRACKET_HIERARCHY",
    "BRACKET_BY_SYMBOL",
    "BRACKET_BY_LEVEL",
    "BRACKET_BY_NAME",
    "resolve_bracket_level",
    "build_standard_nso",
    "compute_pkanp",
]
