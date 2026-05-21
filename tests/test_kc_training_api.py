"""KC training API smoke tests (no live server required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

STORE = REPO_ROOT / "kopano-core" / ".kc" / "context_store_test.json"


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    store = tmp_path / "context_store.json"
    manifest = REPO_ROOT / "docs/swarm-ops/apprenticeship/kc_apprenticeship_150.json"
    tasks = json.loads(manifest.read_text(encoding="utf-8"))["tasks"][:3]
    from kopano.kc_training_store import KcTrainingStore

    ks = KcTrainingStore(store)
    ks.bulk_create_assigned(
        [{"title": t["title"], "teacher_context": t["teacher_context"]} for t in tasks]
    )
    for rec in ks.list_records():
        ks.submit(rec.id, "student evidence")
        ks.review(rec.id, "Save — test opinion.")
        ks.promote(rec.id)

    monkeypatch.setattr("kopano.kc_training_store.default_store_path", lambda: store)
    monkeypatch.setattr("kopano.kc_training_api.default_store_path", lambda: store)
    from kopano.api import app

    return TestClient(app)


def test_training_and_brain_opinion(client: TestClient) -> None:
    training = client.get("/api/kc/training")
    assert training.status_code == 200
    body = training.json()
    assert body["status"]["total_contexts"] == 3
    assert body["status"]["status_counts"]["promoted"] == 3

    opinion = client.get("/api/kc/brain-opinion")
    assert opinion.status_code == 200
    op = opinion.json()
    assert op["opinion_count"] == 3
    assert op["latest_opinion"]["teacher_review"].startswith("Save")
