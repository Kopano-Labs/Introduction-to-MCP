#!/usr/bin/env python3
"""Scaffold, register and validate canonical KPGS skill packages.

This tool writes repository artifacts only. It does not approve a skill, issue a
capability lease or execute the skill. Registration remains discovery metadata.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "governance/kpgs-vnext/skills/registry.json"
DEFAULT_ROOT = REPO_ROOT / "governance/kpgs-vnext/skills/core"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class SkillPackageWorkflowError(ValueError):
    pass


def _load_registry_validator(repo_root: Path):
    path = repo_root / "scripts/ci/validate_skill_registry.py"
    spec = importlib.util.spec_from_file_location("kpgs_validate_skill_registry", path)
    if spec is None or spec.loader is None:
        raise SkillPackageWorkflowError("could not load canonical registry validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SkillPackageWorkflowError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SkillPackageWorkflowError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SkillPackageWorkflowError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: MappingLike) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


MappingLike = dict[str, Any]


def scaffold(
    *,
    repo_root: Path,
    package_root: Path,
    name: str,
    version: str,
    category: str,
    summary: str,
    capability: str,
    resource_scope: str,
) -> Path:
    if not NAME_PATTERN.fullmatch(name):
        raise SkillPackageWorkflowError("name must be lowercase kebab-case")
    if not SEMVER_PATTERN.fullmatch(version):
        raise SkillPackageWorkflowError("version must be semantic x.y.z")
    for field_name, value in {
        "category": category,
        "summary": summary,
        "capability": capability,
        "resource_scope": resource_scope,
    }.items():
        if not value.strip():
            raise SkillPackageWorkflowError(f"{field_name} is required")

    package_dir = (package_root / name).resolve()
    root = repo_root.resolve()
    if root != package_dir and root not in package_dir.parents:
        raise SkillPackageWorkflowError("package path must stay inside repository root")
    if package_dir.exists():
        raise SkillPackageWorkflowError(f"package already exists: {package_dir}")
    package_dir.mkdir(parents=True)

    skill_md = f"""---
name: {name}
description: {summary}
---

# {name}

## What this skill does

{summary}

## What it can access

This skill requires `{capability}` scoped to `{resource_scope}`. The skill itself does not grant that access; the active task must supply a valid capability lease.

## Procedure

1. Confirm the active human task and governing specification.
2. Confirm the required capability lease and resource scope.
3. Execute only the bounded task described by the active handler.
4. Validate the output using the declared validation method.
5. Emit an execution receipt and return a plain-language result.

## Failure and recovery

If authority, evidence or validation is missing, stop before consequential execution and explain the next safe action. Never convert discovery, registration or confidence into permission.
"""
    (package_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    manifest: MappingLike = {
        "name": name,
        "version": version,
        "description": summary,
        "category": category,
        "state": "draft",
        "runtime": {
            "renter_protocol": "1.0",
            "platforms": ["human", "agent", "stateless-renter", "server"],
            "languages": ["markdown", "json"],
        },
        "inputs": {"schema_ref": None, "description": "Task-scoped input supplied by the caller."},
        "outputs": {"schema_ref": None, "description": "Validated task-scoped output plus an execution receipt."},
        "required_capabilities": [
            {"name": capability, "resource_scope": resource_scope, "optional": False}
        ],
        "dependencies": [
            {"kind": "runtime", "name": "kpgs-stateless-renter-protocol", "version_constraint": "1.0"}
        ],
        "provenance": {
            "origin": "kpgs-original",
            "license_status": "unknown",
            "license_spdx": None,
            "sources": [
                {
                    "ref": "human-authored-scaffold",
                    "relationship": "origin",
                    "commit": None,
                }
            ],
        },
        "validation": {
            "hard_gates": [
                "No execution without the declared capability lease",
                "No fabricated validation evidence",
            ],
            "methods": ["schema"],
            "evidence_refs": [],
        },
        "failures": [
            {
                "code": "CAPABILITY_DENIED",
                "recoverability": "user-action",
                "user_message": "This action is not permitted for the active task. Request the required scoped permission and try again.",
            },
            {
                "code": "VALIDATION_FAILED",
                "recoverability": "retry",
                "user_message": "The output did not pass its declared checks, so it was not accepted. Correct the input or implementation and retry.",
            },
        ],
    }
    _write_json(package_dir / "skill.json", manifest)
    return package_dir


def register(
    *,
    repo_root: Path,
    registry_path: Path,
    package_dir: Path,
    authority_class: str,
    summary: str,
    tags: list[str],
) -> None:
    if authority_class not in {"canonical-core", "publication-adapter"}:
        raise SkillPackageWorkflowError("unsupported authority_class")
    manifest = _read_json(package_dir / "skill.json")
    try:
        relative_path = package_dir.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise SkillPackageWorkflowError("package must be inside repository root") from exc

    registry = _read_json(registry_path)
    entries = registry.get("skills")
    if not isinstance(entries, list):
        raise SkillPackageWorkflowError("registry skills must be an array")
    identity = (manifest.get("name"), manifest.get("version"))
    if any((entry.get("name"), entry.get("version")) == identity for entry in entries if isinstance(entry, dict)):
        raise SkillPackageWorkflowError(f"registry already contains {identity[0]}@{identity[1]}")
    entries.append(
        {
            "name": manifest["name"],
            "version": manifest["version"],
            "category": manifest["category"],
            "package_path": relative_path,
            "authority_class": authority_class,
            "discovery": {"summary": summary, "tags": sorted(set(tags))},
        }
    )
    _write_json(registry_path, registry)


def validate(*, repo_root: Path, registry_path: Path) -> None:
    validator = _load_registry_validator(repo_root)
    validator.validate_registry(registry_path, repo_root)


def create_workflow(args: argparse.Namespace) -> Path:
    repo_root = args.repo_root.resolve()
    registry_path = args.registry.resolve()
    package_root = args.package_root.resolve()
    package_dir = scaffold(
        repo_root=repo_root,
        package_root=package_root,
        name=args.name,
        version=args.version,
        category=args.category,
        summary=args.summary,
        capability=args.capability,
        resource_scope=args.resource_scope,
    )
    try:
        register(
            repo_root=repo_root,
            registry_path=registry_path,
            package_dir=package_dir,
            authority_class=args.authority_class,
            summary=args.summary,
            tags=args.tag,
        )
        validate(repo_root=repo_root, registry_path=registry_path)
    except Exception:
        # The package remains on disk for inspection, but registry mutation is
        # restored so a failed create cannot poison canonical discovery.
        registry = _read_json(registry_path)
        registry["skills"] = [
            entry
            for entry in registry.get("skills", [])
            if not (
                isinstance(entry, dict)
                and entry.get("name") == args.name
                and entry.get("version") == args.version
            )
        ]
        _write_json(registry_path, registry)
        raise
    return package_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--package-root", type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Scaffold, register and conformance-validate a new draft skill.")
    create.add_argument("--name", required=True)
    create.add_argument("--version", default="0.1.0")
    create.add_argument("--category", required=True)
    create.add_argument("--summary", required=True)
    create.add_argument("--capability", required=True)
    create.add_argument("--resource-scope", default="active-task")
    create.add_argument("--authority-class", default="canonical-core")
    create.add_argument("--tag", action="append", required=True)

    validate_cmd = sub.add_parser("validate", help="Validate the canonical registry and registered packages.")

    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            package_dir = create_workflow(args)
            print(f"KPGS skill package CREATED+DRAFT+REGISTERED+CONFORMANCE-PASS: {package_dir}")
        elif args.command == "validate":
            validate(repo_root=args.repo_root.resolve(), registry_path=args.registry.resolve())
            print("KPGS skill package registry PASS")
        else:
            raise SkillPackageWorkflowError("unsupported command")
    except Exception as exc:
        print(f"KPGS skill package workflow FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
