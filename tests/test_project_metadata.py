from pathlib import Path
import tomllib


def test_pyproject_files_are_valid_toml():
    for path in [
        Path("pyproject.toml"),
        Path("CLI/pyproject.toml"),
        Path("orch/pyproject.toml"),
    ]:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        assert "project" in data


def test_readme_does_not_contain_generator_artifact():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "Just say the word!" not in readme
