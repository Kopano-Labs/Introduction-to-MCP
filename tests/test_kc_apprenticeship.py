"""KC apprenticeship manifest and store tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kc_apprenticeship_manifest import build_tasks, write_manifest  # noqa: E402
from kopano.kc_training_store import KcTrainingStore  # noqa: E402


def test_manifest_has_250_tasks(tmp_path: Path) -> None:
    path = write_manifest(tmp_path / "manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["task_count"] == 250
    assert len(payload["tasks"]) == 250
    assert payload["checkpoint_every"] == 50
    codes = [t["code"] for t in payload["tasks"]]
    assert len(set(codes)) == 250


def test_build_tasks_phase_coverage() -> None:
    tasks = build_tasks()
    phases = {t["phase"] for t in tasks}
    assert phases == set(range(1, 11))
    assert len(tasks) == 250
    assert sum(1 for t in tasks if t["code"].endswith("25")) == 10


def test_store_bulk_create(tmp_path: Path) -> None:
    store_path = tmp_path / "context_store.json"
    store = KcTrainingStore(store_path)
    items = [
        {"title": "KC — test A", "teacher_context": "Do A with proof."},
        {"title": "KC — test B", "teacher_context": "Do B with proof."},
    ]
    assert store.bulk_create_assigned(items) == 2
    assert len(store.records) == 2
    payload = store.training_payload()
    assert payload["status"]["total_contexts"] == 2
