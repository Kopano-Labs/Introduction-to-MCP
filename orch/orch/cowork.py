from __future__ import annotations

import json
from typing import Any

from .database import get_db_connection, init_db, record_creator_event
from .dev_watch import record_dev_activity


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

DEFAULT_ARTIFACTS = [
    {
        "artifact_type": "prompt",
        "title": "Codex-Parity Prompt Pack",
        "summary": "System and orchestration prompts for IDE, OS, CLI, skill, and connector parity.",
        "status": "active",
        "link": "Orch Labs / MCP Console",
    },
    {
        "artifact_type": "api",
        "title": "Cloud Connector Matrix",
        "summary": "Azure-first and AWS-secondary connector contracts for Demo Day workflows.",
        "status": "building",
        "link": "/api/labs/overview",
    },
    {
        "artifact_type": "screen",
        "title": "Forge Control Surface",
        "summary": "Shared creator workspace for rooms, lanes, artifacts, and lessons.",
        "status": "building",
        "link": "orch/gui/src/App.tsx",
    },
    {
        "artifact_type": "note",
        "title": "Phase Completion Notes",
        "summary": "Short execution log for risks, decisions, and next steps.",
        "status": "draft",
        "link": "Schematics/04-Updates/Implementation Plan.md",
    },
]


def _row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row) if row is not None else {}


def _normalize_lane(lane: str) -> str:
    if lane not in {"research", "build", "review"}:
        return "build"
    return lane


def _status_for_lane(lane: str) -> str:
    return {
        "research": "queued",
        "build": "in_progress",
        "review": "completed",
    }.get(lane, "queued")


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
    for artifact in DEFAULT_ARTIFACTS:
        cursor.execute(
            """
            INSERT INTO cowork_artifacts (room_id, artifact_type, title, summary, status, link)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (room_id, artifact["artifact_type"], artifact["title"], artifact["summary"], artifact["status"], artifact["link"]),
        )
    conn.commit()
    conn.close()
    record_creator_event("room_created", room_id=room_id, metadata=json.dumps({"lead": lead}))
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
    record_creator_event("task_created", room_id=room_id, task_id=task_id, metadata=json.dumps({"lane": lane, "owner": owner}))
    record_dev_activity(
        event_type="task_created",
        room_id=room_id,
        task_id=task_id,
        owner=owner,
        payload={"lane": lane, "priority": priority, "title": title},
    )
    return get_cowork_task(task_id)


def update_cowork_task(task_id: int, status: str) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, owner FROM cowork_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    cursor.execute("UPDATE cowork_tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()
    if row:
        record_creator_event("task_status_changed", room_id=row["room_id"], task_id=task_id, metadata=json.dumps({"status": status}))
        record_dev_activity(
            event_type="task_status_changed",
            room_id=row["room_id"],
            task_id=task_id,
            owner=row["owner"],
            payload={"status": status},
        )
    return get_cowork_task(task_id)


def update_cowork_task_details(
    task_id: int,
    title: str,
    description: str,
    owner: str,
    priority: str,
) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, owner FROM cowork_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    cursor.execute(
        """
        UPDATE cowork_tasks
        SET title = ?, description = ?, owner = ?, priority = ?
        WHERE id = ?
        """,
        (title, description, owner, priority, task_id),
    )
    conn.commit()
    conn.close()
    if row:
        record_creator_event(
            "task_updated",
            room_id=row["room_id"],
            task_id=task_id,
            metadata=json.dumps({"owner": owner, "priority": priority}),
        )
        record_dev_activity(
            event_type="task_updated_before",
            room_id=row["room_id"],
            task_id=task_id,
            owner=row["owner"],
            payload={"title": title, "priority": priority},
        )
        record_dev_activity(
            event_type="task_updated_after",
            room_id=row["room_id"],
            task_id=task_id,
            owner=owner,
            payload={"title": title, "priority": priority},
        )
    return get_cowork_task(task_id)


def reassign_cowork_task(task_id: int, owner: str) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, owner FROM cowork_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    cursor.execute("UPDATE cowork_tasks SET owner = ? WHERE id = ?", (owner, task_id))
    conn.commit()
    conn.close()
    if row:
        record_creator_event("task_owner_changed", room_id=row["room_id"], task_id=task_id, metadata=json.dumps({"owner": owner}))
        record_dev_activity(
            event_type="task_owner_changed_from",
            room_id=row["room_id"],
            task_id=task_id,
            owner=row["owner"],
            payload={"to_owner": owner},
        )
        record_dev_activity(
            event_type="task_owner_changed_to",
            room_id=row["room_id"],
            task_id=task_id,
            owner=owner,
            payload={"from_owner": row["owner"]},
        )
    return get_cowork_task(task_id)


def move_cowork_task(task_id: int, lane: str) -> dict[str, Any]:
    lane = _normalize_lane(lane)
    status = _status_for_lane(lane)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, owner FROM cowork_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    cursor.execute("UPDATE cowork_tasks SET lane = ?, status = ? WHERE id = ?", (lane, status, task_id))
    conn.commit()
    conn.close()
    if row:
        record_creator_event(
            "task_moved",
            room_id=row["room_id"],
            task_id=task_id,
            metadata=json.dumps({"lane": lane, "status": status}),
        )
        record_dev_activity(
            event_type="task_moved",
            room_id=row["room_id"],
            task_id=task_id,
            owner=row["owner"],
            payload={"lane": lane, "status": status},
        )
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


def add_cowork_artifact(
    room_id: int,
    artifact_type: str,
    title: str,
    summary: str,
    status: str = "draft",
    link: str | None = None,
) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO cowork_artifacts (room_id, artifact_type, title, summary, status, link)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (room_id, artifact_type, title, summary, status, link),
    )
    artifact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    record_creator_event(
        "artifact_created",
        room_id=room_id,
        metadata=json.dumps({"artifact_type": artifact_type, "artifact_id": artifact_id}),
    )
    return get_cowork_artifact(artifact_id)


def update_cowork_artifact(
    artifact_id: int,
    artifact_type: str,
    title: str,
    summary: str,
    status: str,
    link: str | None = None,
) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id FROM cowork_artifacts WHERE id = ?", (artifact_id,))
    row = cursor.fetchone()
    cursor.execute(
        """
        UPDATE cowork_artifacts
        SET artifact_type = ?, title = ?, summary = ?, status = ?, link = ?
        WHERE id = ?
        """,
        (artifact_type, title, summary, status, link, artifact_id),
    )
    conn.commit()
    conn.close()
    if row:
        record_creator_event(
            "artifact_updated",
            room_id=row["room_id"],
            metadata=json.dumps({"artifact_id": artifact_id, "artifact_type": artifact_type, "status": status}),
        )
    return get_cowork_artifact(artifact_id)


def list_cowork_artifacts(room_id: int) -> list[dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cowork_artifacts WHERE room_id = ? ORDER BY id DESC", (room_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_cowork_artifact(artifact_id: int) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cowork_artifacts WHERE id = ?", (artifact_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row)


def get_creator_analytics() -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM cowork_rooms")
    total_rooms = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM cowork_tasks")
    total_tasks = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM cowork_artifacts")
    total_artifacts = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM cowork_tasks WHERE status = 'completed'")
    completed_tasks = cursor.fetchone()["count"]
    cursor.execute(
        """
        SELECT owner, COUNT(*) AS count
        FROM cowork_tasks
        GROUP BY owner
        ORDER BY count DESC, owner ASC
        """
    )
    throughput = [dict(row) for row in cursor.fetchall()]
    cursor.execute(
        """
        SELECT event_type, COUNT(*) AS count
        FROM creator_analytics_events
        GROUP BY event_type
        ORDER BY count DESC, event_type ASC
        """
    )
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "rooms": total_rooms,
        "tasks": total_tasks,
        "artifacts": total_artifacts,
        "completed_tasks": completed_tasks,
        "creator_throughput": throughput,
        "event_volume": events,
    }


def get_cowork_room(room_id: int) -> dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cowork_rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    cursor.execute("SELECT * FROM cowork_tasks WHERE room_id = ? ORDER BY id ASC", (room_id,))
    tasks = cursor.fetchall()
    cursor.execute("SELECT * FROM cowork_artifacts WHERE room_id = ? ORDER BY id DESC", (room_id,))
    artifacts = cursor.fetchall()
    conn.close()
    if room is None:
        return {}
    snapshot = dict(room)
    snapshot["tasks"] = [dict(task) for task in tasks]
    snapshot["artifacts"] = [dict(artifact) for artifact in artifacts]
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
    snapshot["artifact_summary"] = {
        "total_artifacts": len(snapshot["artifacts"]),
        "artifact_types": sorted({artifact["artifact_type"] for artifact in snapshot["artifacts"]}),
    }
    return snapshot
