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


def require_apache_2_license(path: Path) -> None:
    require(path.is_file(), "Apache-2.0 state requires a root LICENSE file")
    text = path.read_text(encoding="utf-8")
    for marker in (
        "Apache License",
        "Version 2.0, January 2004",
        "Grant of Patent License",
        "Submission of Contributions",
        "END OF TERMS AND CONDITIONS",
    ):
        require(marker in text, f"root LICENSE is missing canonical Apache-2.0 marker: {marker}")


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
    promotion_rule = decision.get("promotion_rule", "")
    third_party_rule = decision.get("third_party_rule", "")

    require("human" in promotion_rule.lower(), "promotion rule must require human authorization")
    require("third-party" in third_party_rule.lower() or "third party" in third_party_rule.lower(), "third-party preservation rule is missing")

    if status == "AWAITING_HUMAN_DECISION":
        recommendation = decision.get("recommendation", {})
        require(current.get("canonical_spdx") is None, "pending state cannot claim a canonical SPDX license")
        require(current.get("repository_wide_license_claim_allowed") is False, "pending state cannot allow repository-wide licensing claims")
        require(recommendation.get("status") == "RECOMMENDED_NOT_AUTHORIZED", "recommendation must remain non-authoritative while pending")
        require(not LICENSE.exists(), "root LICENSE appeared while decision record still says awaiting human decision")
    else:
        human = decision.get("human_decision", {})
        canonical = current.get("canonical_spdx")
        require(human.get("status") == "AUTHORIZED", "human-approved state requires explicit AUTHORIZED decision evidence")
        require(human.get("spdx") == canonical, "human decision SPDX must match current canonical SPDX")
        require(bool(human.get("authorized_by")), "human-approved state requires authorized_by evidence")
        require(bool(human.get("authorization_source")), "human-approved state requires authorization source evidence")
        require(current.get("repository_wide_license_claim_allowed") in {True, False}, "approved state must explicitly declare repository-wide claim authority")
        require("third-party" in current.get("scope", "").lower() or "third party" in current.get("scope", "").lower(), "approved scope must preserve third-party boundaries")

        if canonical == "Apache-2.0":
            require(current.get("root_license_file_present") is True, "Apache-2.0 state must declare root LICENSE present")
            require(current.get("repository_wide_license_claim_allowed") is True, "canonical Apache-2.0 state must authorize repository-authored licensing claims")
            require_apache_2_license(LICENSE)
        elif canonical == "MIT":
            require(LICENSE.is_file(), "approved MIT state requires a root LICENSE file")
        elif canonical in {"PROPRIETARY", "UNLICENSED", None}:
            require(current.get("repository_wide_license_claim_allowed") is False, "non-open repository states cannot authorize open repository-wide SPDX claims")

    contributing = CONTRIBUTING.read_text(encoding="utf-8")
    require("provenance" in contributing.lower(), "contribution policy must preserve provenance")
    require("license" in contributing.lower(), "contribution policy must state license handling")

    notices = NOTICES.read_text(encoding="utf-8")
    require("does **not** relicense" in notices or "does not relicense" in notices.lower(), "third-party notice registry must state that root licensing does not relicense upstream material")

    policy = POLICY.read_text(encoding="utf-8")
    for phrase in ("Existing third-party material", "Generated code and assets", "KPGS skill promotion gate"):
        require(phrase in policy, f"policy missing required section: {phrase}")

    if status == "HUMAN_APPROVED" and current.get("canonical_spdx") == "Apache-2.0":
        require("ACTIVE — HUMAN APPROVED" in policy, "Apache-2.0 policy must be active and human approved")
        require("Canonical license state: `HUMAN_APPROVED / Apache-2.0`." in policy, "policy must expose canonical Apache-2.0 decision")
        require("Apache License 2.0" in contributing, "CONTRIBUTING.md must expose Apache-2.0 contribution terms")

    canonical = current.get("canonical_spdx")
    print("KPGS-LICENSE PASS: repository license state is explicit and provenance promotion rules are structurally governed.")
    print(f"Decision status: {status}; canonical SPDX: {canonical}.")


if __name__ == "__main__":
    main()
