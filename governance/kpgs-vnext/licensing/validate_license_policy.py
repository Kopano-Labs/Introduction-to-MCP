#!/usr/bin/env python3
"""Structural governance gate for KPGS repository licensing and provenance policy."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DECISION = HERE / "license-decision.json"
POLICY = HERE / "PROVENANCE_AND_LICENSE_POLICY.md"
CONTRIBUTING = REPO / "CONTRIBUTING.md"
NOTICES = REPO / "THIRD_PARTY_NOTICES.md"
LICENSE = REPO / "LICENSE"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-LICENSE FAIL: {message}")


def main() -> None:
    decision = json.loads(DECISION.read_text(encoding="utf-8"))

    require(decision.get("repository") == "RobynAwesome/Introduction-to-MCP", "decision must bind to the canonical repository")
    require(decision.get("issue") == 47, "decision must bind to governance issue #47")
    require(POLICY.is_file(), "provenance/license policy document is missing")
    require(CONTRIBUTING.is_file(), "CONTRIBUTING.md is missing")
    require(NOTICES.is_file(), "THIRD_PARTY_NOTICES.md is missing")

    status = decision.get("decision_status")
    require(status in {"AWAITING_HUMAN_DECISION", "HUMAN_APPROVED"}, "unsupported decision_status")

    current = decision.get("current_repository_state", {})
    recommendation = decision.get("recommendation", {})
    promotion_rule = decision.get("promotion_rule", "")
    third_party_rule = decision.get("third_party_rule", "")

    require("human" in promotion_rule.lower(), "promotion rule must require human authorization")
    require("third-party" in third_party_rule.lower() or "third party" in third_party_rule.lower(), "third-party preservation rule is missing")

    if status == "AWAITING_HUMAN_DECISION":
        require(current.get("canonical_spdx") is None, "pending state cannot claim a canonical SPDX license")
        require(current.get("repository_wide_license_claim_allowed") is False, "pending state cannot allow repository-wide licensing claims")
        require(recommendation.get("status") == "RECOMMENDED_NOT_AUTHORIZED", "recommendation must remain non-authoritative while pending")
        require(not LICENSE.exists(), "root LICENSE appeared while decision record still says awaiting human decision")
    else:
        require(recommendation.get("status") != "RECOMMENDED_NOT_AUTHORIZED" or current.get("canonical_spdx") is not None, "human-approved state must carry an explicit legal outcome")
        require(current.get("repository_wide_license_claim_allowed") in {True, False}, "approved state must explicitly declare repository-wide claim authority")
        if current.get("canonical_spdx") in {"MIT", "Apache-2.0"}:
            require(LICENSE.is_file(), "approved open-source SPDX state requires a root LICENSE file")

    contributing = CONTRIBUTING.read_text(encoding="utf-8")
    require("provenance" in contributing.lower(), "contribution policy must preserve provenance")
    require("license" in contributing.lower(), "contribution policy must state license handling")

    policy = POLICY.read_text(encoding="utf-8")
    for phrase in ("Existing third-party material", "Generated code and assets", "KPGS skill promotion gate"):
        require(phrase in policy, f"policy missing required section: {phrase}")

    print("KPGS-LICENSE PASS: repository license state is explicit and provenance promotion rules are structurally governed.")
    print(f"Decision status: {status}; recommendation: {recommendation.get('spdx')} ({recommendation.get('status')}).")


if __name__ == "__main__":
    main()
