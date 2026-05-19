"""KC teacher-student apprenticeship CRUD store (local JSON)."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

STATUSES = frozenset({"assigned", "in_progress", "submitted", "reviewed", "promoted"})


def default_store_path() -> Path:
    return Path(__file__).resolve().parent.parent / ".kc" / "context_store.json"


def now_millis() -> int:
    return int(time.time() * 1000)


@dataclass
class KcRecord:
    id: str
    title: str
    teacher_context: str
    student_response: str | None
    teacher_review: str | None
    status: str
    created_at: int
    updated_at: int


class KcTrainingStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_store_path()
        self.next_id = 1
        self.records: dict[str, KcRecord] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.next_id = int(payload.get("next_id", 1))
        self.records = {
            key: KcRecord(**value) for key, value in payload.get("records", {}).items()
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "next_id": self.next_id,
            "records": {key: asdict(value) for key, value in self.records.items()},
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def create(self, title: str, teacher_context: str) -> KcRecord:
        now = now_millis()
        record_id = f"kc-{self.next_id}"
        self.next_id += 1
        record = KcRecord(
            id=record_id,
            title=title,
            teacher_context=teacher_context,
            student_response=None,
            teacher_review=None,
            status="assigned",
            created_at=now,
            updated_at=now,
        )
        self.records[record_id] = record
        self.save()
        return record

    def bulk_create_assigned(self, items: list[dict[str, str]]) -> int:
        created = 0
        for item in items:
            self.create(item["title"], item["teacher_context"])
            created += 1
        return created

    def list_records(self) -> list[KcRecord]:
        return sorted(self.records.values(), key=lambda r: r.updated_at, reverse=True)

    def status_payload(self) -> dict[str, Any]:
        counts = {s: 0 for s in sorted(STATUSES)}
        latest: KcRecord | None = None
        for record in self.records.values():
            counts[record.status] = counts.get(record.status, 0) + 1
            if latest is None or record.updated_at > latest.updated_at:
                latest = record
        return {
            "store_path": str(self.path),
            "total_contexts": len(self.records),
            "status_counts": counts,
            "latest_context": None
            if latest is None
            else {
                "id": latest.id,
                "title": latest.title,
                "status": latest.status,
                "updated_at": latest.updated_at,
            },
            "owner_proof": "local_only_domain_first_unproven",
        }

    def get(self, record_id: str) -> KcRecord:
        if record_id not in self.records:
            raise KeyError(record_id)
        return self.records[record_id]

    def submit(self, record_id: str, student_response: str) -> KcRecord:
        record = self.get(record_id)
        record.student_response = student_response
        record.status = "submitted"
        record.updated_at = now_millis()
        self.save()
        return record

    def review(self, record_id: str, teacher_review: str) -> KcRecord:
        record = self.get(record_id)
        record.teacher_review = teacher_review
        record.status = "reviewed"
        record.updated_at = now_millis()
        self.save()
        return record

    def promote(self, record_id: str) -> KcRecord:
        record = self.get(record_id)
        record.status = "promoted"
        record.updated_at = now_millis()
        self.save()
        return record

    def training_payload(self) -> dict[str, Any]:
        return {
            "status": self.status_payload(),
            "records": [asdict(r) for r in self.list_records()],
        }
