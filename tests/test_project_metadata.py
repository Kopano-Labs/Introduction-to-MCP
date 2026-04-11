from pathlib import Path
import tomllib


def test_pyproject_files_are_valid_toml():
    candidates = [
        Path("pyproject.toml"),
        Path("CLI/pyproject.toml"),
    ]
    if Path("kopano-core/pyproject.toml").exists():
        candidates.append(Path("kopano-core/pyproject.toml"))
    if Path("orch/pyproject.toml").exists():
        candidates.append(Path("orch/pyproject.toml"))

    for path in candidates:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        assert "project" in data


def test_readme_does_not_contain_generator_artifact():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "Just say the word!" not in readme


def test_cli_readme_references_mcp_cli_install_surface():
    readme = Path("CLI/README.md").read_text(encoding="utf-8")
    assert "python -m pip install -e ./CLI" in readme
    assert "mcp-cli" in readme


def test_demo_day_artifacts_exist():
    assert Path("DEMO_DAY_RUNBOOK.md").exists()
    assert Path("DEMO_DAY_10_PHASES_50_TASKS.md").exists()
    assert Path("scripts/demo_day_readiness.py").exists()
    assert Path("scripts/demo_day_preflight.ps1").exists()


def test_root_schematics_index_points_to_real_notes():
    index = Path("index.md").read_text(encoding="utf-8")
    assert "[[Schematics/00-Home/Now|Now]]" in index
    assert "[[Schematics/04-Updates/Project Status|Project Status]]" in index
    assert "[[Schematics/06-Reference/Repo Documents Index|Repo Documents Index]]" in index


def test_gitignore_blocks_vendor_directories():
    ignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "node_modules/" in ignore


def test_security_policy_has_vendor_and_secret_rules():
    security = Path("SECURITY.md").read_text(encoding="utf-8")
    assert "Do not commit `node_modules/`" in security
    assert "revoke or rotate" in security
