from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "kopano-core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from kopano.skill_runtime import (  # noqa: E402
    CanonicalSkillRuntime,
    SkillAuthorizationDenied,
    SkillNotLoadable,
)


def load_capability_module():
    path = ROOT / "governance/kpgs-vnext/security/capability_lease.py"
    spec = importlib.util.spec_from_file_location("kpgs_capability_lease_for_skill_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_fixture(repo: Path, *, state: str = "validated") -> None:
    package = repo / "skills/demo/demo-skill"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demonstrate governed skill execution.\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (package / "skill.json").write_text(
        json.dumps(
            {
                "name": "demo-skill",
                "version": "1.2.3",
                "description": "Demonstrate governed skill execution.",
                "category": "demo",
                "state": state,
                "runtime": {
                    "renter_protocol": "1.0",
                    "platforms": ["stateless-renter"],
                    "languages": ["json"],
                },
                "inputs": {"schema_ref": None, "description": "integer"},
                "outputs": {"schema_ref": None, "description": "integer"},
                "required_capabilities": [
                    {"name": "demo.execute", "resource_scope": "active-task", "optional": False}
                ],
                "dependencies": [],
                "provenance": {
                    "origin": "kpgs-original",
                    "license_status": "compatible",
                    "license_spdx": "MIT",
                    "sources": [{"ref": "test-fixture", "relationship": "origin", "commit": None}],
                },
                "validation": {
                    "hard_gates": ["output must be an even integer"],
                    "methods": ["deterministic-test"],
                    "evidence_refs": ["tests/test_canonical_skill_runtime.py"],
                },
                "failures": [
                    {
                        "code": "VALIDATION_FAILED",
                        "recoverability": "retry",
                        "user_message": "The output failed its declared check.",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
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
                "skills": [
                    {
                        "name": "demo-skill",
                        "version": "1.2.3",
                        "category": "demo",
                        "package_path": "skills/demo/demo-skill",
                        "authority_class": "canonical-core",
                        "discovery": {"summary": "Demo skill", "tags": ["demo"]},
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def authority_and_token(capability: str = "demo.execute"):
    lease = load_capability_module()
    authority = lease.CapabilityLeaseAuthority(
        lease.KeyRing({"k1": b"a" * 32}, "k1"),
        clock=lambda: datetime(2026, 8, 19, 0, 0, tzinfo=timezone.utc),
    )
    token = authority.issue(
        subject_id="renter:test",
        subject_kind="renter",
        tenant_id="tenant:test",
        domain_id="domain:test",
        task_id="task:test",
        capabilities=[
            {"name": capability, "resource_scope": "active-task", "constraints": ["test-only"]}
        ],
        policy_decision_ref="policy:test",
        governing_spec_ref="spec:test",
        correlation_id="corr:test",
        evidence_ref="evidence:test",
    )
    return authority, token


def test_skill_executes_only_after_capability_authorization_and_emits_bound_receipt(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    authority, token = authority_and_token()
    evidence: list[dict] = []
    calls = 0

    runtime = CanonicalSkillRuntime(
        repo_root=tmp_path,
        capability_authorizer=authority.authorize,
        evidence_sink=lambda receipt: evidence.append(dict(receipt)),
    )

    def handler(value: int) -> int:
        nonlocal calls
        calls += 1
        return value * 2

    runtime.register_handler(
        "demo-skill",
        "1.2.3",
        handler,
        output_validator=lambda output: (isinstance(output, int) and output % 2 == 0, "output is even integer"),
    )
    result = runtime.execute(
        name="demo-skill",
        version="1.2.3",
        platform="stateless-renter",
        lease_token=token,
        tenant_id="tenant:test",
        domain_id="domain:test",
        task_id="task:test",
        correlation_id="corr:test",
        input_value=21,
    )

    assert result.output == 42
    assert calls == 1
    assert result.receipt["schema"] == "kpgs.skill-execution-receipt.v1"
    assert result.receipt["skill"]["name"] == "demo-skill"
    assert result.receipt["skill"]["version"] == "1.2.3"
    assert result.receipt["input_digest"]
    assert result.receipt["output_digest"]
    assert result.receipt["capability_lease_ids"]
    assert result.receipt["capability_decisions"][0]["capability"] == "demo.execute"
    assert result.receipt["validation"]["passed"] is True
    assert result.receipt["outcome"] == "completed"
    assert result.receipt["authority_effect"] == "none"
    assert evidence == [result.receipt]


def test_undeclared_capability_blocks_before_handler(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    authority, token = authority_and_token("different.execute")
    calls = 0
    runtime = CanonicalSkillRuntime(repo_root=tmp_path, capability_authorizer=authority.authorize)

    def handler(value):
        nonlocal calls
        calls += 1
        return value

    runtime.register_handler("demo-skill", "1.2.3", handler)
    with pytest.raises(SkillAuthorizationDenied, match="capability denied before execution"):
        runtime.execute(
            name="demo-skill",
            version="1.2.3",
            platform="stateless-renter",
            lease_token=token,
            tenant_id="tenant:test",
            domain_id="domain:test",
            task_id="task:test",
            correlation_id="corr:test",
            input_value={"unsafe": False},
        )
    assert calls == 0


def test_draft_registered_skill_is_discoverable_but_not_loadable(tmp_path: Path) -> None:
    write_fixture(tmp_path, state="draft")
    authority, token = authority_and_token()
    runtime = CanonicalSkillRuntime(repo_root=tmp_path, capability_authorizer=authority.authorize)
    runtime.register_handler("demo-skill", "1.2.3", lambda value: value)

    assert runtime.discover("demo")[0]["name"] == "demo-skill"
    with pytest.raises(SkillNotLoadable, match="not production-loadable: draft"):
        runtime.execute(
            name="demo-skill",
            version="1.2.3",
            platform="stateless-renter",
            lease_token=token,
            tenant_id="tenant:test",
            domain_id="domain:test",
            task_id="task:test",
            correlation_id="corr:test",
            input_value=1,
        )
