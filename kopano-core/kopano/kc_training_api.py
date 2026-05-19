"""FastAPI routes for KC apprenticeship CRUD (Studio Training page)."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .kc_training_store import KcTrainingStore

router = APIRouter(prefix="/api/kc", tags=["kc-training"])


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
        return {"seeded": 0, "message": "store already has records; use apprenticeship activate script"}
    store.create(
        "KC - Starter apprenticeship task",
        "Read SWARM_OPERATIONS.md and run python scripts/kc_guard.py all. Submit bounded evidence only.",
    )
    return {"seeded": 1, "store_path": str(store.path)}
