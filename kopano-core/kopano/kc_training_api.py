"""FastAPI routes for KC apprenticeship CRUD (Studio Training page)."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pathlib import Path

from .kc_training_store import KcTrainingStore, default_store_path

router = APIRouter(prefix="/api/kc", tags=["kc-training"])

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = _REPO_ROOT / "docs" / "swarm-ops" / "apprenticeship" / "kc_apprenticeship_150.json"


class CreateRecordRequest(BaseModel):
    title: str
    teacher_context: str


class SubmitRequest(BaseModel):
    student_response: str


class ReviewRequest(BaseModel):
    teacher_review: str


def _store() -> KcTrainingStore:
    return KcTrainingStore()


@router.get("/training")
def get_training() -> dict:
    return _store().training_payload()


@router.get("/brain-opinion")
def get_brain_opinion() -> dict:
    """KC (memory) does not execute; teacher_review on each record is the stored teacher opinion."""
    store = _store()
    records = store.list_records()
    with_review = [r for r in records if r.teacher_review]
    latest = with_review[0] if with_review else None
    counts = store.status_payload()["status_counts"]
    return {
        "role": "KC is the brain (vault + ledger), not the worker. Cassey/Cursor write teacher_review.",
        "total_contexts": len(records),
        "status_counts": counts,
        "opinion_count": len(with_review),
        "latest_opinion": None
        if latest is None
        else {
            "record_id": latest.id,
            "title": latest.title,
            "status": latest.status,
            "teacher_review": latest.teacher_review,
            "updated_at": latest.updated_at,
        },
        "closure": (
            "Apprenticeship 150: manifest on branch, steward evidence on records. "
            "Promote only with bounded proof. No fake swarm, no Kimi ack in repo."
        ),
    }


@router.post("/records")
def create_record(body: CreateRecordRequest) -> dict:
    record = _store().create(body.title, body.teacher_context)
    return {"record": asdict(record)}


@router.post("/records/{record_id}/submit")
def submit_record(record_id: str, body: SubmitRequest) -> dict:
    try:
        record = _store().submit(record_id, body.student_response)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"record": asdict(record)}


@router.post("/records/{record_id}/review")
def review_record(record_id: str, body: ReviewRequest) -> dict:
    try:
        record = _store().review(record_id, body.teacher_review)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"record": asdict(record)}


@router.post("/records/{record_id}/promote")
def promote_record(record_id: str) -> dict:
    try:
        record = _store().promote(record_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"record": asdict(record)}


@router.post("/seed-training")
def seed_training() -> dict:
    """Seed one starter task if the store is empty."""
    store = _store()
    if store.records:
        return {"seeded": 0, "message": "store already has records; use seed-apprenticeship-150 or activate script"}
    store.create(
        "KC - Starter apprenticeship task",
        "Read SWARM_OPERATIONS.md and run python scripts/kc_guard.py all. Submit bounded evidence only.",
    )
    return {"seeded": 1, "store_path": str(store.path)}


@router.post("/seed-apprenticeship-150")
def seed_apprenticeship_150(replace: bool = False) -> dict:
    """Load 150 tasks from the git-tracked manifest into the local KC store."""
    if not _MANIFEST.is_file():
        raise HTTPException(status_code=404, detail=f"manifest missing: {_MANIFEST}")
    import json

    payload = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    tasks = payload.get("tasks", [])
    if len(tasks) != 150:
        raise HTTPException(status_code=500, detail=f"expected 150 tasks, found {len(tasks)}")

    store_path = default_store_path()
    if replace and store_path.exists():
        store_path.unlink()
    store = KcTrainingStore(store_path)
    if store.records and not replace:
        return {
            "seeded": 0,
            "total": len(store.records),
            "store_path": str(store.path),
            "message": "store not empty; pass replace=true to reseed",
        }
    items = [{"title": t["title"], "teacher_context": t["teacher_context"]} for t in tasks]
    seeded = store.bulk_create_assigned(items)
    return {"seeded": seeded, "total": len(store.records), "store_path": str(store.path)}
