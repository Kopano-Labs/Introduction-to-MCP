from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.ci.validate_fork_assimilation import (
    DEFAULT_MATRIX,
    AssimilationValidationError,
    EXPECTED_REPOSITORIES,
    validate_matrix,
)


def write_mutated_matrix(tmp_path: Path, mutate) -> Path:
    matrix = json.loads(DEFAULT_MATRIX.read_text(encoding="utf-8"))
    mutate(matrix)
    path = tmp_path / "evolution-matrix.json"
    path.write_text(json.dumps(matrix), encoding="utf-8")
    return path


def test_inventory_covers_all_15_learning_window_repositories():
    entries = validate_matrix()

    assert len(entries) == 15
    assert {entry["repository"] for entry in entries} == EXPECTED_REPOSITORIES


def test_two_first_party_workloads_are_not_misrepresented_as_forks():
    entries = {entry["repository"]: entry for entry in validate_matrix()}

    for repo in ("RobynAwesome/paws-and-potjie", "RobynAwesome/cars4mars-project"):
        assert entries[repo]["repository_kind"] == "first_party_non_fork"
        assert entries[repo]["upstream"] is None
        assert entries[repo]["disposition"] == "external-workload"


def test_kage_is_hard_gated_reference_only():
    entries = {entry["repository"]: entry for entry in validate_matrix()}
    kage = entries["RobynAwesome/kage"]

    assert kage["upstream"] == "MengTo/kage"
    assert kage["license_spdx"] is None
    assert kage["disposition"] == "no-import"


def test_licensed_candidates_preserve_known_upstream_and_spdx():
    entries = {entry["repository"]: entry for entry in validate_matrix()}

    assert (entries["RobynAwesome/Skills"]["upstream"], entries["RobynAwesome/Skills"]["license_spdx"]) == (
        "MengTo/Skills",
        "MIT",
    )
    assert entries["RobynAwesome/JavaScriptMastery-skills"]["license_spdx"] == "MIT"
    assert entries["RobynAwesome/claude-code-templates"]["license_spdx"] == "MIT"
    assert entries["RobynAwesome/OmniRoute"]["license_spdx"] == "MIT"
    assert entries["RobynAwesome/generative-ai"]["license_spdx"] == "Apache-2.0"


def test_unlicensed_source_cannot_be_promoted_to_import(tmp_path: Path):
    def mutate(matrix):
        next(entry for entry in matrix["forks"] if entry["repository"] == "RobynAwesome/kage")["disposition"] = "import"

    path = write_mutated_matrix(tmp_path, mutate)
    with pytest.raises(AssimilationValidationError, match="cannot authorize|must remain no-import"):
        validate_matrix(path)


def test_fork_without_upstream_is_rejected(tmp_path: Path):
    def mutate(matrix):
        next(entry for entry in matrix["forks"] if entry["repository"] == "RobynAwesome/Skills")["upstream"] = None

    path = write_mutated_matrix(tmp_path, mutate)
    with pytest.raises(AssimilationValidationError, match="must declare owner/repo upstream"):
        validate_matrix(path)


def test_import_requires_security_dependency_and_validation_completion(tmp_path: Path):
    def mutate(matrix):
        entry = next(entry for entry in matrix["forks"] if entry["repository"] == "RobynAwesome/Skills")
        entry["disposition"] = "import"

    path = write_mutated_matrix(tmp_path, mutate)
    with pytest.raises(AssimilationValidationError, match="requires complete security review"):
        validate_matrix(path)


def test_each_source_maps_to_kpgs_work():
    entries = validate_matrix()

    assert all(entry["kpgs_bindings"] for entry in entries)
    assert all(entry["validation_owner"] == "KPGS issue #43" for entry in entries)
