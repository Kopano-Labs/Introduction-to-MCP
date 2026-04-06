from __future__ import annotations

from pathlib import Path
from typing import Any

from .database import get_db_connection, init_db


ROOT = Path(__file__).resolve().parents[2]

PATTERN_CATALOG = [
    {
        "lesson_key": "python-fastapi-api",
        "title": "FastAPI service patterns",
        "track": "python-core",
        "source": "orch/orch/api.py",
        "notes": "Router composition, lifespan setup, and JSON responses.",
    },
    {
        "lesson_key": "python-pytest-contracts",
        "title": "pytest contract patterns",
        "track": "python-core",
        "source": "tests/test_labs_api.py",
        "notes": "Small focused endpoint tests with deterministic expectations.",
    },
    {
        "lesson_key": "react-launch-surface",
        "title": "React launch surface patterns",
        "track": "frontend-core",
        "source": "orch/gui/src/App.tsx",
        "notes": "Stateful sections, typed models, and launch-oriented UI composition.",
    },
    {
        "lesson_key": "schematics-discipline",
        "title": "Schematics as operating system",
        "track": "product-craft",
        "source": "Schematics/04-Updates/Implementation Plan.md",
        "notes": "Keep roadmap, comms, status, and execution state synchronized.",
    },
]


def _upsert_lesson(cursor: Any, lesson: dict[str, str], status: str, confidence: int) -> None:
    cursor.execute(
        """
        INSERT INTO orch_code_lessons (lesson_key, title, track, source, status, confidence, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(lesson_key) DO UPDATE SET
            title = excluded.title,
            track = excluded.track,
            source = excluded.source,
            status = excluded.status,
            confidence = excluded.confidence,
            notes = excluded.notes,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            lesson["lesson_key"],
            lesson["title"],
            lesson["track"],
            lesson["source"],
            status,
            confidence,
            lesson["notes"],
        ),
    )


def teach_repo_patterns() -> dict[str, Any]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    taught = []
    for lesson in PATTERN_CATALOG:
        source_path = ROOT / lesson["source"]
        status = "learned" if source_path.exists() else "queued"
        confidence = 85 if source_path.exists() else 20
        _upsert_lesson(cursor, lesson, status=status, confidence=confidence)
        taught.append({**lesson, "status": status, "confidence": confidence})
    conn.commit()
    conn.close()
    return {
        "mode": "repo-pattern-teaching",
        "taught_lessons": taught,
        "next_focus": recommend_next_lessons(limit=3),
    }


def recommend_next_lessons(limit: int = 5) -> list[dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT lesson_key, title, track, source, status, confidence, notes
        FROM orch_code_lessons
        ORDER BY
            CASE status
                WHEN 'queued' THEN 0
                WHEN 'learning' THEN 1
                WHEN 'learned' THEN 2
                ELSE 3
            END,
            confidence ASC,
            id ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_orch_code_profile() -> dict[str, Any]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT lesson_key, title, track, source, status, confidence, notes FROM orch_code_lessons ORDER BY id ASC"
    )
    lessons = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "title": "Orch Code",
        "teaching_basis": "current repo patterns first",
        "tracks": sorted({lesson["track"] for lesson in lessons}) if lessons else [],
        "lessons": lessons,
        "summary": {
            "total_lessons": len(lessons),
            "learned_lessons": sum(1 for lesson in lessons if lesson["status"] == "learned"),
        },
    }
