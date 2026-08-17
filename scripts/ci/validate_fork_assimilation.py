#!/usr/bin/env python3
"""Validate the KPGS fork-assimilation inventory and fail closed on unsafe reuse.

Issue #43 treats fork provenance, licensing and assimilation authority as separate
facts. This validator prevents a repository from becoming canonical merely because
it is present in the learning inventory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MATRIX = REPO_ROOT / "governance/kpgs-vnext/fork-assimilation/evolution-matrix.json"
EXPECTED_REPOSITORIES = {
    "RobynAwesome/sketchbook",
    "RobynAwesome/DesignerNewsApp",
    "RobynAwesome/kage",
    "RobynAwesome/claude-code-templates",
    "RobynAwesome/my-react-app",
    "RobynAwesome/paws-and-potjie",
    "RobynAwesome/Skills",
    "RobynAwesome/JavaScriptMastery-skills",
    "RobynAwesome/jwt-auth",
    "RobynAwesome/towers",
    "RobynAwesome/adk_tutorial",
    "RobynAwesome/cars4mars-project",
    "RobynAwesome/OmniRoute",
    "RobynAwesome/JavaScriptMastery-gsap-cc-starter",
    "RobynAwesome/generative-ai",
}
REQUIRED_ENTRY_FIELDS = {
    "repository",
    "repository_kind",
    "upstream",
    "inspection_ref",
    "role",
    "target_layers",
    "kpgs_bindings",
    "disposition",
    "provenance_status",
    "license_status",
    "license_spdx",
    "security_status",
    "dependency_status",
    "reusable_material",
    "independent_reimplementation",
    "validation_owner",
    "validation_status",
    "notes",
}
NO_LICENSE_STATES = {"no_github_detected_license", "unverified_reference_only"}
ASSIMILATION_DISPOSITIONS = {"vendor", "import"}
SAFE_UNLICENSED_DISPOSITIONS = {"reference", "rewrite", "external-workload", "no-import"}
KNOWN_KINDS = {"fork", "first_party_non_fork"}
BINDING_RE = re.compile(r"^(issue:#\d+|protocol:.+|skill:.+)$")


class AssimilationValidationError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssimilationValidationError(f"missing matrix: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssimilationValidationError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AssimilationValidationError("matrix root must be an object")
    return data


def validate_matrix(path: Path = DEFAULT_MATRIX) -> list[dict[str, Any]]:
    matrix = _load(path)
    if matrix.get("schema_version") != "1.1":
        raise AssimilationValidationError("schema_version must be 1.1")
    if matrix.get("issue") != 43:
        raise AssimilationValidationError("matrix must remain bound to issue #43")

    policy = matrix.get("policy")
    if not isinstance(policy, dict):
        raise AssimilationValidationError("policy must be an object")
    allowed_dispositions = set(policy.get("allowed_dispositions", []))
    if not ASSIMILATION_DISPOSITIONS <= allowed_dispositions:
        raise AssimilationValidationError("policy must explicitly enumerate vendor/import dispositions")

    entries = matrix.get("forks")
    if not isinstance(entries, list):
        raise AssimilationValidationError("forks must be an array")
    if len(entries) != 15:
        raise AssimilationValidationError(f"expected 15 inventory entries, found {len(entries)}")

    repositories = [entry.get("repository") for entry in entries if isinstance(entry, dict)]
    if set(repositories) != EXPECTED_REPOSITORIES or len(repositories) != len(set(repositories)):
        missing = EXPECTED_REPOSITORIES - set(repositories)
        unexpected = set(repositories) - EXPECTED_REPOSITORIES
        raise AssimilationValidationError(
            f"repository inventory mismatch; missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )

    for entry in entries:
        if not isinstance(entry, dict):
            raise AssimilationValidationError("every inventory entry must be an object")
        repo = entry.get("repository", "<unknown>")
        missing_fields = REQUIRED_ENTRY_FIELDS - entry.keys()
        if missing_fields:
            raise AssimilationValidationError(f"{repo}: missing fields {sorted(missing_fields)}")

        kind = entry["repository_kind"]
        if kind not in KNOWN_KINDS:
            raise AssimilationValidationError(f"{repo}: unsupported repository_kind {kind!r}")
        if not isinstance(entry["inspection_ref"], str) or not entry["inspection_ref"].strip():
            raise AssimilationValidationError(f"{repo}: inspection_ref is required")
        if not isinstance(entry["role"], str) or not entry["role"].strip():
            raise AssimilationValidationError(f"{repo}: role is required")

        if kind == "fork":
            if not isinstance(entry["upstream"], str) or "/" not in entry["upstream"]:
                raise AssimilationValidationError(f"{repo}: fork must declare owner/repo upstream")
            if entry["provenance_status"] != "fork_parent_verified":
                raise AssimilationValidationError(f"{repo}: fork provenance must be verified")
        else:
            if entry["upstream"] is not None:
                raise AssimilationValidationError(f"{repo}: first-party non-fork must have null upstream")
            if entry["provenance_status"] != "owner_repository_verified_non_fork":
                raise AssimilationValidationError(f"{repo}: first-party provenance must be explicit")

        disposition = entry["disposition"]
        if disposition not in allowed_dispositions:
            raise AssimilationValidationError(f"{repo}: unsupported disposition {disposition!r}")

        bindings = entry["kpgs_bindings"]
        if not isinstance(bindings, list) or not bindings:
            raise AssimilationValidationError(f"{repo}: at least one KPGS issue/protocol/skill binding is required")
        if not all(isinstance(binding, str) and BINDING_RE.match(binding) for binding in bindings):
            raise AssimilationValidationError(f"{repo}: invalid KPGS binding")

        target_layers = entry["target_layers"]
        if not isinstance(target_layers, list) or not target_layers:
            raise AssimilationValidationError(f"{repo}: target_layers must be non-empty")

        license_status = entry["license_status"]
        spdx = entry["license_spdx"]
        if license_status in NO_LICENSE_STATES:
            if spdx is not None:
                raise AssimilationValidationError(f"{repo}: unlicensed/reference-only source cannot declare SPDX")
            if disposition not in SAFE_UNLICENSED_DISPOSITIONS:
                raise AssimilationValidationError(
                    f"{repo}: {license_status} cannot authorize disposition {disposition!r}"
                )
        else:
            if not isinstance(spdx, str) or not spdx.strip():
                raise AssimilationValidationError(f"{repo}: licensed candidate must declare SPDX")

        if disposition in ASSIMILATION_DISPOSITIONS:
            if entry["security_status"] != "complete":
                raise AssimilationValidationError(f"{repo}: {disposition} requires complete security review")
            if entry["dependency_status"] != "complete":
                raise AssimilationValidationError(f"{repo}: {disposition} requires complete dependency review")
            if entry["validation_status"] != "approved_for_assimilation":
                raise AssimilationValidationError(f"{repo}: {disposition} requires approved validation evidence")

        if not isinstance(entry["validation_owner"], str) or not entry["validation_owner"].strip():
            raise AssimilationValidationError(f"{repo}: validation_owner is required")
        if not isinstance(entry["validation_status"], str) or not entry["validation_status"].strip():
            raise AssimilationValidationError(f"{repo}: validation_status is required")

    kage = next(entry for entry in entries if entry["repository"] == "RobynAwesome/kage")
    if kage["disposition"] != "no-import" or kage["license_spdx"] is not None:
        raise AssimilationValidationError("RobynAwesome/kage must remain no-import until reusable permission is evidenced")

    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args(argv)
    try:
        entries = validate_matrix(args.matrix)
    except AssimilationValidationError as exc:
        print(f"KPGS fork assimilation FAIL: {exc}", file=sys.stderr)
        return 1

    licensed = sum(entry["license_spdx"] is not None for entry in entries)
    no_import = sum(entry["disposition"] == "no-import" for entry in entries)
    print(f"KPGS fork assimilation PASS: {len(entries)} sources; {licensed} licensed candidates; {no_import} no-import")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
