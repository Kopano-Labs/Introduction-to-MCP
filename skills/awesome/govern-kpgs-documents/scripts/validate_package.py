#!/usr/bin/env python3
"""Dependency-free contract validator for the KPGS-DTS skill package.

This is intentionally a package/manifest validator, not a natural-language parser.
It proves structural invariants without promoting external publication state.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


DOCUMENT_STATES = {"draft", "watch", "operating", "graduated", "deprecated", "archived"}
PROOF_STATES = {"unknown", "foc", "poc", "verified_production"}
KPEFS_VECTORS = {"V1_PLANT", "V2_ANIMAL", "V3_HOMO_SAPIENS", "V4_DIASPORA"}
AUTHORITY_CLASSES = {
    "operator_directive",
    "repo_canonical",
    "governance_receipt",
    "verified_live",
    "personal_context",
    "external_reference",
    "unknown",
}
EVIDENCE_CLASSES = {
    "verified-source",
    "verified-live",
    "site-stated",
    "demo-display",
    "planned",
    "privileged",
    "transactional",
    "unknown",
}
PROOF_IDS = {"PROOF-01", "PROOF-02", "PROOF-03", "PROOF-04"}
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
CANONICAL_ID = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
RENTER_ASSERTION = "I_AM_STATELESS_RENTER_NOT_LANDLORD"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _require(mapping: dict[str, Any], keys: set[str], where: str, errors: list[str]) -> None:
    missing = sorted(keys - mapping.keys())
    if missing:
        errors.append(f"{where}: missing required keys {missing}")


def validate_document_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema",
        "document_id",
        "canonical_id",
        "title",
        "version",
        "status",
        "proof_state",
        "owner",
        "author",
        "source",
        "authority_class",
        "evidence_class",
        "kpefs",
        "protocols",
        "promotion_gate",
        "linked_evidence",
        "renter_assertion",
    }
    _require(manifest, required, "document manifest", errors)
    if errors:
        return errors

    if manifest["schema"] != "kpgs_document_manifest_v1":
        errors.append("document manifest: unexpected schema")
    if not isinstance(manifest["canonical_id"], str) or not CANONICAL_ID.fullmatch(manifest["canonical_id"]):
        errors.append("document manifest: canonical_id must be lowercase_snake_case")
    if not isinstance(manifest["version"], str) or not SEMVER.fullmatch(manifest["version"]):
        errors.append("document manifest: version must be SemVer")
    if manifest["status"] not in DOCUMENT_STATES:
        errors.append(f"document manifest: invalid status {manifest['status']!r}")
    if manifest["proof_state"] not in PROOF_STATES:
        errors.append(f"document manifest: invalid proof_state {manifest['proof_state']!r}")
    if manifest["authority_class"] not in AUTHORITY_CLASSES:
        errors.append(f"document manifest: invalid authority_class {manifest['authority_class']!r}")
    if manifest["evidence_class"] not in EVIDENCE_CLASSES:
        errors.append(f"document manifest: invalid evidence_class {manifest['evidence_class']!r}")
    if manifest["renter_assertion"] != RENTER_ASSERTION:
        errors.append("document manifest: renter assertion mismatch")

    source = manifest.get("source")
    if not isinstance(source, dict):
        errors.append("document manifest: source must be an object")
    else:
        _require(source, {"repository", "ref"}, "document manifest source", errors)
        source_evidence = source.get("evidence_class")
        if source_evidence is not None and source_evidence not in EVIDENCE_CLASSES:
            errors.append(f"document manifest: invalid source evidence_class {source_evidence!r}")

    kpefs = manifest.get("kpefs")
    if not isinstance(kpefs, dict):
        errors.append("document manifest: kpefs must be an object")
    else:
        _require(kpefs, {"primary_vector", "secondary_vectors"}, "document manifest kpefs", errors)
        primary = kpefs.get("primary_vector")
        if primary not in KPEFS_VECTORS:
            errors.append(f"document manifest: invalid KPEFS primary vector {primary!r}")
        secondary = kpefs.get("secondary_vectors", [])
        if not isinstance(secondary, list) or any(item not in KPEFS_VECTORS for item in secondary):
            errors.append("document manifest: invalid KPEFS secondary vector list")
        elif primary in secondary:
            errors.append("document manifest: primary vector must not be duplicated in secondary_vectors")

    gate = manifest.get("promotion_gate")
    if not isinstance(gate, dict) or not isinstance(gate.get("requires"), list):
        errors.append("document manifest: promotion_gate.requires must be a list")
    else:
        invalid_proofs = [item for item in gate["requires"] if item not in PROOF_IDS]
        if invalid_proofs:
            errors.append(f"document manifest: invalid promotion proof ids {invalid_proofs}")

    publication = manifest.get("publication")
    if isinstance(publication, dict):
        state = publication.get("state")
        if state == "indexed" and not publication.get("discovery_receipt"):
            errors.append("document manifest: indexed publication requires discovery_receipt")

    if manifest["status"] == "graduated" and manifest["proof_state"] != "verified_production":
        errors.append("document manifest: graduated requires verified_production proof_state")

    return errors


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    required_paths = [
        root / "SKILL.md",
        root / "skill.json",
        root / "publication.json",
        root / "references" / "KPGS_DTS_SPEC.md",
        root / "references" / "kpgs-document-manifest.schema.json",
        root / "templates" / "KPGS_DOCUMENT_TEMPLATE.md",
        root / "evals" / "cases.json",
        root / "examples" / "KPGS_DTS.manifest.json",
    ]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing package file: {path.relative_to(root)}")
    if errors:
        return errors

    skill = _load_json(root / "skill.json")
    publication = _load_json(root / "publication.json")
    evals = _load_json(root / "evals" / "cases.json")
    manifest = _load_json(root / "examples" / "KPGS_DTS.manifest.json")

    if skill.get("renter_assertion") != RENTER_ASSERTION:
        errors.append("skill.json: renter assertion mismatch")
    if skill.get("status") != "poc":
        errors.append("skill.json: initial package status must remain poc")
    if skill.get("security", {}).get("production_deploy_authorization_from_skill_change") is not False:
        errors.append("skill.json: skill changes must not authorize production deployment")
    if skill.get("security", {}).get("external_ack_fabrication_allowed") is not False:
        errors.append("skill.json: external ACK fabrication must be false")
    if publication.get("publication_state") != "unknown":
        errors.append("publication.json: public discovery must remain unknown until externally verified")
    if publication.get("external_discovery") != "unknown":
        errors.append("publication.json: external discovery must remain unknown until externally verified")
    if not isinstance(evals.get("cases"), list) or len(evals["cases"]) < 5:
        errors.append("evals/cases.json: at least five governance cases are required")

    errors.extend(validate_document_manifest(manifest))
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_package(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("KPGS-DTS package contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
