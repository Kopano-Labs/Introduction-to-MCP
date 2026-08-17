#!/usr/bin/env python3
"""Validate and query the canonical KPGS skill registry.

The registry is discovery metadata, not an authority escalation surface. A registered
skill remains non-loadable for production unless its manifest state is validated or
approved and the caller separately holds the declared capability lease.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "governance/kpgs-vnext/skills/registry.json"
REQUIRED_MANIFEST_KEYS = {
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
PRODUCTION_STATES = {"validated", "approved"}
AUTHORITY_CLASSES = {"canonical-core", "publication-adapter"}


class RegistryValidationError(ValueError):
    """Raised when registry or package conformance fails."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryValidationError(f"missing file: {path.relative_to(REPO_ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryValidationError(f"invalid JSON: {path.relative_to(REPO_ROOT)}: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryValidationError(f"expected JSON object: {path.relative_to(REPO_ROOT)}")
    return data


def _frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def validate_registry(registry_path: Path = DEFAULT_REGISTRY, repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    registry = _read_json(registry_path)
    if registry.get("registry_version") != "1.0.0":
        raise RegistryValidationError("registry_version must be 1.0.0")
    if registry.get("authority") != "governance/kpgs-vnext/skills":
        raise RegistryValidationError("canonical registry authority must remain governance/kpgs-vnext/skills")

    policy = registry.get("selection_policy")
    if not isinstance(policy, dict):
        raise RegistryValidationError("selection_policy must be an object")
    if set(policy.get("production_states", [])) != PRODUCTION_STATES:
        raise RegistryValidationError("production_states must be exactly validated + approved")
    if policy.get("require_capability_lease") is not True:
        raise RegistryValidationError("canonical registry must require a capability lease")
    if policy.get("require_provenance") is not True:
        raise RegistryValidationError("canonical registry must require provenance")
    if policy.get("require_license_status") is not True:
        raise RegistryValidationError("canonical registry must require license status")

    entries = registry.get("skills")
    if not isinstance(entries, list) or not entries:
        raise RegistryValidationError("skills must be a non-empty array")

    seen: set[tuple[str, str]] = set()
    validated: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise RegistryValidationError("each registry skill entry must be an object")

        name = entry.get("name")
        version = entry.get("version")
        category = entry.get("category")
        package_path = entry.get("package_path")
        authority_class = entry.get("authority_class")
        discovery = entry.get("discovery")

        if not all(isinstance(value, str) and value for value in (name, version, category, package_path)):
            raise RegistryValidationError("registry entries require non-empty name/version/category/package_path")
        if authority_class not in AUTHORITY_CLASSES:
            raise RegistryValidationError(f"{name}@{version}: unsupported authority_class {authority_class!r}")
        if not isinstance(discovery, dict) or not isinstance(discovery.get("summary"), str):
            raise RegistryValidationError(f"{name}@{version}: discovery.summary is required")
        tags = discovery.get("tags")
        if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag for tag in tags):
            raise RegistryValidationError(f"{name}@{version}: discovery.tags must be a non-empty string array")

        identity = (name, version)
        if identity in seen:
            raise RegistryValidationError(f"duplicate registry identity: {name}@{version}")
        seen.add(identity)

        package_dir = repo_root / package_path
        manifest_path = package_dir / "skill.json"
        skill_md_path = package_dir / "SKILL.md"
        manifest = _read_json(manifest_path)
        if not skill_md_path.is_file():
            raise RegistryValidationError(f"{name}@{version}: missing SKILL.md")

        missing_keys = REQUIRED_MANIFEST_KEYS - manifest.keys()
        if missing_keys:
            raise RegistryValidationError(f"{name}@{version}: manifest missing {sorted(missing_keys)}")
        if manifest["name"] != name or manifest["version"] != version or manifest["category"] != category:
            raise RegistryValidationError(f"{name}@{version}: registry identity does not match skill.json")
        if _frontmatter_name(skill_md_path) != name:
            raise RegistryValidationError(f"{name}@{version}: SKILL.md frontmatter name does not match registry")

        provenance = manifest.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("origin"):
            raise RegistryValidationError(f"{name}@{version}: provenance.origin is required")
        if "license_status" not in provenance or not provenance.get("license_status"):
            raise RegistryValidationError(f"{name}@{version}: provenance.license_status is required")
        if not isinstance(provenance.get("sources"), list) or not provenance["sources"]:
            raise RegistryValidationError(f"{name}@{version}: provenance.sources must not be empty")

        capabilities = manifest.get("required_capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            raise RegistryValidationError(f"{name}@{version}: required_capabilities must not be empty")

        validation = manifest.get("validation")
        if not isinstance(validation, dict) or not validation.get("methods"):
            raise RegistryValidationError(f"{name}@{version}: validation.methods must not be empty")

        manifest_state = manifest.get("state")
        production_loadable = manifest_state in PRODUCTION_STATES
        validated.append(
            {
                **entry,
                "state": manifest_state,
                "production_loadable": production_loadable,
                "required_capabilities": capabilities,
            }
        )

    return validated


def discover(
    query: str = "",
    *,
    platform: str | None = None,
    production_only: bool = False,
    registry_path: Path = DEFAULT_REGISTRY,
    repo_root: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    """Return registry entries matching text/platform constraints without granting execution authority."""
    entries = validate_registry(registry_path, repo_root)
    needle = query.casefold().strip()
    results: list[dict[str, Any]] = []

    for entry in entries:
        if production_only and not entry["production_loadable"]:
            continue

        manifest = _read_json(repo_root / entry["package_path"] / "skill.json")
        platforms = manifest.get("runtime", {}).get("platforms", [])
        if platform and platform not in platforms:
            continue

        haystack = " ".join(
            [
                entry["name"],
                entry["category"],
                entry["discovery"]["summary"],
                *entry["discovery"]["tags"],
            ]
        ).casefold()
        if needle and needle not in haystack:
            continue
        results.append(entry)

    return results


def _print_entries(entries: Iterable[dict[str, Any]]) -> None:
    for entry in entries:
        status = "production-loadable" if entry["production_loadable"] else f"not-loadable:{entry['state']}"
        print(f"{entry['name']}@{entry['version']}\t{entry['authority_class']}\t{status}\t{entry['package_path']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--discover", default=None, metavar="QUERY", help="Search the validated registry.")
    parser.add_argument("--platform", help="Filter discovery by declared runtime platform.")
    parser.add_argument("--production-only", action="store_true", help="Return only validated/approved packages.")
    args = parser.parse_args(argv)

    try:
        if args.discover is not None:
            entries = discover(
                args.discover,
                platform=args.platform,
                production_only=args.production_only,
                registry_path=args.registry,
            )
            _print_entries(entries)
        else:
            entries = validate_registry(args.registry)
            print(f"KPGS skill registry PASS: {len(entries)} registered package(s)")
            _print_entries(entries)
    except RegistryValidationError as exc:
        print(f"KPGS skill registry FAIL: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
