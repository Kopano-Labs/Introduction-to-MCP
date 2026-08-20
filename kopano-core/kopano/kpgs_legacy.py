"""Runtime contract and deterministic proof gate for KC — Kopano Context Legacy.

This module does not prove unemployment impact by itself. It loads the canonical
KPGS Legacy contract and gates submitted impact packets so claims cannot outrun
the evidence/verification state they carry.
"""

from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMATICS_LEGACY = (
    REPO_ROOT
    / "Schematics"
    / "21-KOPANO-PHU GOVERNACE SYSTEMS"
    / "MAIN-BRAIN"
    / "KPGS_LEGACY.json"
)
RUNTIME_LEGACY = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_LEGACY.json"
RENTER_ASSERTION = "I_AM_STATELESS_RENTER_NOT_LANDLORD"


@lru_cache(maxsize=1)
def _load_legacy_contract_cached() -> dict[str, Any]:
    for path in (SCHEMATICS_LEGACY, RUNTIME_LEGACY):
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            return data
    return {
        "schema": "kpgs_kopano_context_legacy_v1",
        "error": "legacy_contract_missing",
        "expected": str(SCHEMATICS_LEGACY.relative_to(REPO_ROOT)),
    }


def load_legacy_contract() -> dict[str, Any]:
    """Return an isolated copy of the current machine-readable Legacy contract."""
    return copy.deepcopy(_load_legacy_contract_cached())


def legacy_status() -> dict[str, Any]:
    """Return the bounded runtime identity and purpose contract for KC."""
    contract = load_legacy_contract()
    invariants = contract.get("invariants") or {}
    return {
        "schema": "kpgs_legacy_status_v1",
        "bracket": contract.get("bracket", "[KPGS_LEGACY]"),
        "kc": invariants.get("kc", contract.get("kc", "Kopano Context Legacy")),
        "precedence": invariants.get(
            "precedence", contract.get("precedence", "KPGS_LEGACY > RENTER_IDENTITY")
        ),
        "mission": invariants.get("mission", contract.get("mission")),
        "mission_is_not_completion_claim": invariants.get(
            "mission_is_not_completion_claim",
            contract.get("mission_is_not_completion_claim", True),
        ),
        "renter_assertion": invariants.get("renter_assertion", RENTER_ASSERTION),
        "pka": contract.get("pka"),
        "capability_chain": contract.get("capability_chain", []),
        "learning_loop": contract.get("learning_loop", []),
        "dispositions": contract.get("dispositions", []),
        "authority": contract.get("authority", "Schematics MAIN BRAIN"),
        "source": contract.get("_source"),
    }


def legacy_packet_template() -> dict[str, Any]:
    """Return the minimum packet shape expected by the Legacy impact gate."""
    contract = load_legacy_contract()
    required = contract.get("impact_claim_required_fields") or [
        "claim",
        "geography",
        "cohort",
        "denominator",
        "time_window",
        "baseline",
        "observed_change",
        "methodology",
        "evidence_refs",
        "attribution_basis",
    ]
    return {
        "schema": "kpgs_legacy_impact_packet_v1",
        "renter_assertion": RENTER_ASSERTION,
        "required_fields": required,
        "impact_claim": {field: ([] if field == "evidence_refs" else "unknown") for field in required},
        "verification": {
            "verifier_receipt": None,
            "evidence_verified": False,
            "capability_validated": False,
            "economic_pathway_observed": False,
            "claim_exceeds_evidence": False,
            "proof_fabricated_or_unverifiable": False,
        },
    }


def _is_unknown(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or value.strip().casefold() == "unknown"
    if isinstance(value, list):
        return len(value) == 0
    return False


def evaluate_legacy_impact(packet: dict[str, Any]) -> dict[str, Any]:
    """Gate an impact packet without pretending the runtime independently verified evidence.

    `KC_ALIGNED_POC` requires an explicit verifier receipt plus all three verification
    booleans: evidence verified, capability validated, and economic pathway observed.
    Otherwise the strongest positive disposition is `KC_POC_CANDIDATE`.
    """
    contract = load_legacy_contract()
    claim = packet.get("impact_claim") if isinstance(packet.get("impact_claim"), dict) else packet
    verification = packet.get("verification") if isinstance(packet.get("verification"), dict) else {}
    required = contract.get("impact_claim_required_fields") or legacy_packet_template()["required_fields"]

    missing = [field for field in required if _is_unknown(claim.get(field))]
    evidence_refs = claim.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        evidence_refs = []
        if "evidence_refs" not in missing:
            missing.append("evidence_refs")

    reasons: list[str] = []
    disposition = "KC_HOLD"

    if verification.get("proof_fabricated_or_unverifiable") is True:
        disposition = "KC_FOC_BLOCK"
        reasons.append("proof marked fabricated or unverifiable")
    elif verification.get("claim_exceeds_evidence") is True:
        disposition = "KC_FOC_CANDIDATE"
        reasons.append("claim scope exceeds supplied evidence boundary")
    elif missing:
        disposition = "KC_HOLD"
        reasons.append("critical impact fields remain unknown or empty")
    elif not evidence_refs:
        disposition = "KC_HOLD"
        reasons.append("no evidence references supplied")
    else:
        verifier_receipt = verification.get("verifier_receipt")
        aligned = all(
            verification.get(key) is True
            for key in (
                "evidence_verified",
                "capability_validated",
                "economic_pathway_observed",
            )
        ) and isinstance(verifier_receipt, str) and bool(verifier_receipt.strip())
        if aligned:
            disposition = "KC_ALIGNED_POC"
            reasons.append("verified capability and observed economic pathway receipt supplied")
        else:
            disposition = "KC_POC_CANDIDATE"
            reasons.append("bounded packet is complete but external proof remains partially unverified")

    return {
        "schema": "kpgs_legacy_impact_evaluation_v1",
        "bracket": contract.get("bracket", "[KPGS_LEGACY]"),
        "kc": (contract.get("invariants") or {}).get("kc", "Kopano Context Legacy"),
        "renter_assertion": packet.get("renter_assertion", RENTER_ASSERTION),
        "disposition": disposition,
        "reasons": reasons,
        "missing_or_unknown": sorted(set(missing)),
        "evidence_ref_count": len(evidence_refs),
        "external_verification_claimed": bool(verification.get("verifier_receipt")),
        "runtime_proves_external_evidence": False,
        "mission_completion_claim_allowed": False,
        "next_proof_required": (
            []
            if disposition == "KC_ALIGNED_POC"
            else [
                "resolve unknown impact fields" if missing else None,
                "attach provenance-bearing evidence refs" if not evidence_refs else None,
                "attach independent verifier receipt for validated capability and observed pathway"
                if disposition == "KC_POC_CANDIDATE"
                else None,
            ]
        ),
        "source": contract.get("_source"),
    } | {
        "next_proof_required": [
            item
            for item in (
                []
                if disposition == "KC_ALIGNED_POC"
                else [
                    "resolve unknown impact fields" if missing else None,
                    "attach provenance-bearing evidence refs" if not evidence_refs else None,
                    "attach independent verifier receipt for validated capability and observed pathway"
                    if disposition == "KC_POC_CANDIDATE"
                    else None,
                ]
            )
            if item
        ]
    }
