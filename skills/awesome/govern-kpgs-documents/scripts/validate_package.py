#!/usr/bin/env python3
"""Dependency-free contract validator for the KPGS-DTS publication adapter.

The canonical KPGS skill-package authority lives under
``governance/kpgs-vnext/skills/``. This validator mirrors the hard structural
subset needed by this package without creating a second runtime or promoting
external publication state.
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
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:[-+][0-9A-Za-z.-]+)?$")
CANONICAL_ID = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")
RENTER_VERSION = re.compile(r"^[0-9]+\.[0-9]+$")

SKILL_STATES = {"draft", "validated", "approved", "deprecated", "blocked"}
SKILL_PLATFORMS = {"human", "agent", "stateless-renter", "browser", "server", "cli"}
DEPENDENCY_KINDS = {"skill", "package", "service", "tool", "runtime"}
PROVENANCE_ORIGINS = {"kpgs-original", "adapted", "imported", "fork-derived-reference"}
LICENSE_STATES = {"verified-compatible", "pending", "incompatible", "unknown"}
SOURCE_RELATIONSHIPS = {"inspiration", "adaptation", "import", "upstream", "reference"}
VALIDATION_METHODS = {"schema", "unit", "integration", "e2e", "security", "accessibility", "human-review", "model-eval"}
RECOVERABILITY = {"retry", "user-action", "operator-action", "not-recoverable"}
RENTER_ASSERTION = "I_AM_STATELESS_RENTER_NOT_LANDLORD"

SKILL_REQUIRED = {
    "name",
    "version",
    "description",
    "category",
    "state",
    "runtime",
    "inputs",
    "outputs",
    "required_capabilities",
    "dependencies",
    "provenance",
    "validation",
    "failures",
}


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


def validate_skill_manifest(skill: dict[str, Any]) -> list[str]:
    """Validate the canonical vNext skill-manifest shape used by this package."""
    errors: list[str] = []
    _require(skill, SKILL_REQUIRED, "skill.json", errors)
    unexpected = sorted(set(skill) - SKILL_REQUIRED)
    if unexpected:
        errors.append(f"skill.json: unexpected top-level keys {unexpected}")
    if errors:
        return errors

    if not isinstance(skill["name"], str) or not SKILL_NAME.fullmatch(skill["name"]):
        errors.append("skill.json: name must match canonical kebab-case contract")
    if not isinstance(skill["version"], str) or not SEMVER.fullmatch(skill["version"]):
        errors.append("skill.json: version must be SemVer")
    if not isinstance(skill["description"], str) or len(skill["description"]) < 10:
        errors.append("skill.json: description is too short")
    if not isinstance(skill["category"], str) or len(skill["category"]) < 2:
        errors.append("skill.json: category is invalid")
    if skill["state"] not in SKILL_STATES:
        errors.append(f"skill.json: invalid state {skill['state']!r}")

    runtime = skill.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("skill.json: runtime must be an object")
    else:
        _require(runtime, {"renter_protocol", "platforms"}, "skill.json runtime", errors)
        if not isinstance(runtime.get("renter_protocol"), str) or not RENTER_VERSION.fullmatch(runtime["renter_protocol"]):
            errors.append("skill.json: runtime.renter_protocol must be X.Y")
        platforms = runtime.get("platforms")
        if not isinstance(platforms, list) or not platforms or any(p not in SKILL_PLATFORMS for p in platforms):
            errors.append("skill.json: runtime.platforms violates canonical enum")

    for field in ("inputs", "outputs"):
        contract = skill.get(field)
        if not isinstance(contract, dict):
            errors.append(f"skill.json: {field} must be an object")
        else:
            _require(contract, {"schema_ref"}, f"skill.json {field}", errors)
            schema_ref = contract.get("schema_ref")
            if schema_ref is not None and not isinstance(schema_ref, str):
                errors.append(f"skill.json: {field}.schema_ref must be string or null")

    capabilities = skill.get("required_capabilities")
    if not isinstance(capabilities, list):
        errors.append("skill.json: required_capabilities must be a list")
    else:
        for index, capability in enumerate(capabilities):
            if not isinstance(capability, dict):
                errors.append(f"skill.json: capability {index} must be an object")
                continue
            _require(capability, {"name", "resource_scope"}, f"skill.json capability {index}", errors)

    dependencies = skill.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("skill.json: dependencies must be a list")
    else:
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict):
                errors.append(f"skill.json: dependency {index} must be an object")
                continue
            _require(dependency, {"kind", "name", "version_constraint"}, f"skill.json dependency {index}", errors)
            if dependency.get("kind") not in DEPENDENCY_KINDS:
                errors.append(f"skill.json: dependency {index} has invalid kind")

    provenance = skill.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("skill.json: provenance must be an object")
    else:
        _require(provenance, {"origin", "license_status", "sources"}, "skill.json provenance", errors)
        if provenance.get("origin") not in PROVENANCE_ORIGINS:
            errors.append("skill.json: provenance.origin is invalid")
        if provenance.get("license_status") not in LICENSE_STATES:
            errors.append("skill.json: provenance.license_status is invalid")
        sources = provenance.get("sources")
        if not isinstance(sources, list):
            errors.append("skill.json: provenance.sources must be a list")
        else:
            for index, source in enumerate(sources):
                if not isinstance(source, dict):
                    errors.append(f"skill.json: provenance source {index} must be an object")
                    continue
                _require(source, {"ref", "relationship"}, f"skill.json provenance source {index}", errors)
                if source.get("relationship") not in SOURCE_RELATIONSHIPS:
                    errors.append(f"skill.json: provenance source {index} has invalid relationship")

    validation = skill.get("validation")
    if not isinstance(validation, dict):
        errors.append("skill.json: validation must be an object")
    else:
        _require(validation, {"hard_gates", "methods"}, "skill.json validation", errors)
        methods = validation.get("methods")
        if not isinstance(methods, list) or not methods or any(method not in VALIDATION_METHODS for method in methods):
            errors.append("skill.json: validation.methods violates canonical enum")

    failures = skill.get("failures")
    if not isinstance(failures, list):
        errors.append("skill.json: failures must be a list")
    else:
        for index, failure in enumerate(failures):
            if not isinstance(failure, dict):
                errors.append(f"skill.json: failure {index} must be an object")
                continue
            _require(failure, {"code", "recoverability", "user_message"}, f"skill.json failure {index}", errors)
            if failure.get("recoverability") not in RECOVERABILITY:
                errors.append(f"skill.json: failure {index} has invalid recoverability")

    return errors


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

    errors.extend(validate_skill_manifest(skill))
    if skill.get("state") != "draft":
        errors.append("skill.json: package must remain draft until conformance evidence is complete")
    provenance = skill.get("provenance", {})
    if provenance.get("license_status") != "unknown":
        errors.append("skill.json: license status must remain unknown until canonical licensing policy is resolved")

    hard_gates = skill.get("validation", {}).get("hard_gates", [])
    required_gate_fragments = (
        "Public indexing",
        "skill-only change",
        "External acknowledgements",
        "UNKNOWN or MAYBE",
    )
    for fragment in required_gate_fragments:
        if not any(fragment in gate for gate in hard_gates):
            errors.append(f"skill.json: missing hard gate containing {fragment!r}")

    if publication.get("surface_role") != "publication-adapter":
        errors.append("publication.json: skills/awesome package must identify as publication-adapter")
    if publication.get("canonical_contract_path") != "governance/kpgs-vnext/skills/SKILL_PACKAGE.md":
        errors.append("publication.json: canonical skill contract path mismatch")
    if publication.get("canonical_skill_schema_path") != "governance/kpgs-vnext/skills/skill-manifest.schema.json":
        errors.append("publication.json: canonical skill schema path mismatch")
    if publication.get("canonical_runtime_registration") != "pending":
        errors.append("publication.json: canonical runtime registration must remain pending in this skills-only PR")
    if publication.get("publication_state") != "unknown":
        errors.append("publication.json: public discovery must remain unknown until externally verified")
    if publication.get("external_discovery") != "unknown":
        errors.append("publication.json: external discovery must remain unknown until externally verified")
    if publication.get("license_status") != "unknown":
        errors.append("publication.json: license status must remain unknown until canonical policy is resolved")
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
    print("KPGS-DTS publication adapter contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
