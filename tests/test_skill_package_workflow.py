from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts/ci/manage_skill_package.py"
    spec = importlib.util.spec_from_file_location("kpgs_manage_skill_package_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def seed_repo(repo: Path) -> None:
    scripts = repo / "scripts/ci"
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/ci/validate_skill_registry.py", scripts / "validate_skill_registry.py")
    registry = repo / "governance/kpgs-vnext/skills/registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "registry_version": "1.0.0",
                "authority": "governance/kpgs-vnext/skills",
                "selection_policy": {
                    "production_states": ["validated", "approved"],
                    "require_capability_lease": True,
                    "require_provenance": True,
                    "require_license_status": True,
                },
                "skills": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_create_workflow_scaffolds_versions_registers_and_validates(tmp_path: Path) -> None:
    module = load_module()
    seed_repo(tmp_path)
    package_root = tmp_path / "governance/kpgs-vnext/skills/core"
    registry = tmp_path / "governance/kpgs-vnext/skills/registry.json"

    args = module.argparse.Namespace(
        repo_root=tmp_path,
        registry=registry,
        package_root=package_root,
        name="example-governed-skill",
        version="1.4.0",
        category="governance",
        summary="Explain and execute one bounded governed example.",
        capability="example.execute",
        resource_scope="active-task",
        authority_class="canonical-core",
        tag=["example", "governance"],
        command="create",
    )
    package = module.create_workflow(args)

    manifest = json.loads((package / "skill.json").read_text(encoding="utf-8"))
    registry_value = json.loads(registry.read_text(encoding="utf-8"))
    assert manifest["name"] == "example-governed-skill"
    assert manifest["version"] == "1.4.0"
    assert manifest["state"] == "draft"
    assert manifest["required_capabilities"] == [
        {"name": "example.execute", "resource_scope": "active-task", "optional": False}
    ]
    assert "what it can access" in (package / "SKILL.md").read_text(encoding="utf-8").lower()
    assert registry_value["skills"][0]["name"] == "example-governed-skill"
    assert registry_value["skills"][0]["version"] == "1.4.0"
    assert registry_value["skills"][0]["package_path"] == "governance/kpgs-vnext/skills/core/example-governed-skill"

    # Re-run the canonical validator against the newly generated package.
    module.validate(repo_root=tmp_path, registry_path=registry)


def test_failed_registration_does_not_duplicate_identity(tmp_path: Path) -> None:
    module = load_module()
    seed_repo(tmp_path)
    package_root = tmp_path / "governance/kpgs-vnext/skills/core"
    registry = tmp_path / "governance/kpgs-vnext/skills/registry.json"
    package = module.scaffold(
        repo_root=tmp_path,
        package_root=package_root,
        name="single-identity",
        version="0.1.0",
        category="demo",
        summary="One identity only.",
        capability="demo.execute",
        resource_scope="active-task",
    )
    module.register(
        repo_root=tmp_path,
        registry_path=registry,
        package_dir=package,
        authority_class="canonical-core",
        summary="One identity only.",
        tags=["demo"],
    )

    try:
        module.register(
            repo_root=tmp_path,
            registry_path=registry,
            package_dir=package,
            authority_class="canonical-core",
            summary="One identity only.",
            tags=["demo"],
        )
    except module.SkillPackageWorkflowError as exc:
        assert "already contains" in str(exc)
    else:
        raise AssertionError("duplicate skill identity was not rejected")
