from __future__ import annotations

from typing import Any

from .database import get_db_connection, init_db


DEFAULT_TASKS = [
    {
        "title": "Research current product direction",
        "description": "Audit current product patterns before implementation.",
        "owner": "Lead",
        "priority": "critical",
        "lane": "research",
    },
    {
        "title": "Build first implementation slice",
        "description": "Convert scoped plan into code and tests.",
        "owner": "DEV_1",
        "priority": "high",
        "lane": "build",
    },
    {
        "title": "Verify and document changes",
        "description": "Run tests, check launch surface, and update Schematics.",
        "owner": "DEV_2",
        "priority": "high",
        "lane": "review",
    },
]


def _row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row) if row is not None else {}


def create_cowork_room(name: str, mission: str, lead: str = "Lead") -> dict[str, Any]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cowork_rooms (name, mission, lead, status) VALUES (?, ?, ?, ?)",
        (name, mission, lead, "active"),
    )
    room_id = cursor.lastrowid
    for task in DEFAULT_TASKS:
        cursor.execute(
            """
            INSERT INTO cowork_tasks (room_id, title, description, owner, status, priority, lane)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (room_id, task["title"], task["description"], task["owner"], "queued", task["priority"], task["lane"]),
        )
    conn.commit()
    conn.close()
    return get_cowork_room(room_id)


def add_cowork_task(
    room_id: int,
    title: str,
    description: str,
    owner: str,
    priority: str = "high",
    lane: str = "build",
) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO cowork_tasks (room_id, title, description, owner, status, priority, lane)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (room_id, title, description, owner, "queued", priority, lane),
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_cowork_task(task_id)


def update_cowork_task(task_id: int, status: str) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cowork_tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()
    return get_cowork_task(task_id)


def reassign_cowork_task(task_id: int, owner: str) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cowork_tasks SET owner = ? WHERE id = ?", (owner, task_id))
    conn.commit()
    conn.close()
    return get_cowork_task(task_id)


def get_cowork_task(task_id: int) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cowork_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row)


def list_cowork_rooms() -> list[dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cowork_rooms ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_cowork_room(room_id: int) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cowork_rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    cursor.execute("SELECT * FROM cowork_tasks WHERE room_id = ? ORDER BY id ASC", (room_id,))
    tasks = cursor.fetchall()
    conn.close()
    if room is None:
        return {}
    snapshot = dict(room)
    snapshot["tasks"] = [dict(task) for task in tasks]
    snapshot["lanes"] = {
        "research": [dict(task) for task in tasks if task["lane"] == "research"],
        "build": [dict(task) for task in tasks if task["lane"] == "build"],
        "review": [dict(task) for task in tasks if task["lane"] == "review"],
    }
    snapshot["dispatch_summary"] = {
        "total_tasks": len(snapshot["tasks"]),
        "queued": sum(1 for task in snapshot["tasks"] if task["status"] == "queued"),
        "in_progress": sum(1 for task in snapshot["tasks"] if task["status"] == "in_progress"),
        "completed": sum(1 for task in snapshot["tasks"] if task["status"] == "completed"),
        "owners": sorted({task["owner"] for task in snapshot["tasks"]}),
    }
    return snapshot
