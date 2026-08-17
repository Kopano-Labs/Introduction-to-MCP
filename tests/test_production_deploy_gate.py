from scripts.ci.production_deploy_gate import authorize_deploy, is_production_affecting


def test_governance_only_diff_does_not_authorize_production_deploy():
    authorized, reason, matched = authorize_deploy(
        [
            "governance/kpgs-vnext/skills/kpgs-dts/SKILL.md",
            "governance/web-estate/estate.yaml.md",
        ]
    )

    assert authorized is False
    assert matched == []
    assert "outside" in reason


def test_skill_only_diff_does_not_authorize_production_deploy():
    authorized, _, matched = authorize_deploy(
        [
            "skills/pka/watch-what-you-call/SKILL.md",
            "skills/kpgs-dts/README.md",
        ]
    )

    assert authorized is False
    assert matched == []


def test_documentation_only_diff_does_not_authorize_production_deploy():
    authorized, _, matched = authorize_deploy(
        [
            "README.md",
            "docs/runtime-architecture.md",
            "infra/DEPLOY_GUIDE.md",
            "kopano-core/README.md",
        ]
    )

    assert authorized is False
    assert matched == []


def test_infrastructure_change_authorizes_production_deploy():
    authorized, reason, matched = authorize_deploy(["infra/main.bicep"])

    assert authorized is True
    assert reason == "production-affecting diff"
    assert matched == ["infra/main.bicep"]


def test_runtime_change_authorizes_production_deploy():
    authorized, _, matched = authorize_deploy(
        [
            "governance/policy.md",
            "kopano-core/kopano/runtime.py",
        ]
    )

    assert authorized is True
    assert matched == ["kopano-core/kopano/runtime.py"]


def test_root_runtime_files_are_explicitly_authorized():
    assert is_production_affecting("main.py") is True
    assert is_production_affecting("pyproject.toml") is True
    assert is_production_affecting("uv.lock") is True
    assert is_production_affecting("Dockerfile") is True


def test_manual_dispatch_is_explicit_release_intent():
    authorized, reason, matched = authorize_deploy([], explicit_release=True)

    assert authorized is True
    assert reason == "explicit workflow_dispatch release intent"
    assert matched == []
