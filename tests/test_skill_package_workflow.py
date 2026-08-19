from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

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


class SkillPackageWorkflowTests(unittest.TestCase):
    def test_create_workflow_scaffolds_versions_registers_and_validates(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            seed_repo(repo)
            package_root = repo / "governance/kpgs-vnext/skills/core"
            registry = repo / "governance/kpgs-vnext/skills/registry.json"

            args = module.argparse.Namespace(
                repo_root=repo,
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
            self.assertEqual(manifest["name"], "example-governed-skill")
            self.assertEqual(manifest["version"], "1.4.0")
            self.assertEqual(manifest["state"], "draft")
            self.assertEqual(
                manifest["required_capabilities"],
                [{"name": "example.execute", "resource_scope": "active-task", "optional": False}],
            )
            self.assertIn(
                "what it can access",
                (package / "SKILL.md").read_text(encoding="utf-8").lower(),
            )
            self.assertEqual(registry_value["skills"][0]["name"], "example-governed-skill")
            self.assertEqual(registry_value["skills"][0]["version"], "1.4.0")
            self.assertEqual(
                registry_value["skills"][0]["package_path"],
                "governance/kpgs-vnext/skills/core/example-governed-skill",
            )

            module.validate(repo_root=repo, registry_path=registry)

    def test_failed_registration_does_not_duplicate_identity(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            seed_repo(repo)
            package_root = repo / "governance/kpgs-vnext/skills/core"
            registry = repo / "governance/kpgs-vnext/skills/registry.json"
            package = module.scaffold(
                repo_root=repo,
                package_root=package_root,
                name="single-identity",
                version="0.1.0",
                category="demo",
                summary="One identity only.",
                capability="demo.execute",
                resource_scope="active-task",
            )
            module.register(
                repo_root=repo,
                registry_path=registry,
                package_dir=package,
                authority_class="canonical-core",
                summary="One identity only.",
                tags=["demo"],
            )

            with self.assertRaisesRegex(module.SkillPackageWorkflowError, "already contains"):
                module.register(
                    repo_root=repo,
                    registry_path=registry,
                    package_dir=package,
                    authority_class="canonical-core",
                    summary="One identity only.",
                    tags=["demo"],
                )


if __name__ == "__main__":
    unittest.main()
