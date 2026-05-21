"""KC apprenticeship status snapshots (teacher_review = KC opinion, not chat)."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = REPO_ROOT / "docs" / "swarm-ops" / "apprenticeship" / "checkpoints"


def _verdict_bucket(teacher_review: str | None) -> str:
    if not teacher_review:
        return "pending"
    text = teacher_review.strip()
    lower = text.lower()
    if lower.startswith("save"):
        return "Save"
    if lower.startswith("watch"):
        return "Watch"
    if lower.startswith("kill"):
        return "Kill"
    return "other"


def _ordered_record_ids(store: Any) -> list[str]:
    return sorted(store.records.keys(), key=lambda rid: int(rid.split("-", 1)[1]))


def summarize_store(
    store: Any,
    manifest_tasks: list[dict[str, str]] | None = None,
    milestone: int | None = None,
) -> dict[str, Any]:
    """Build KC status payload from context store records.

    When milestone is set, only the first N manifest-ordered records are included
    (cumulative KC status @ 50, 100, … — not the final store applied to every file).
    """
    status_counts: Counter[str] = Counter()
    verdict_counts: Counter[str] = Counter()
    samples: list[dict[str, str]] = []

    codes_by_rid: dict[str, str] = {}
    record_ids = _ordered_record_ids(store)
    if manifest_tasks:
        for index, rid in enumerate(record_ids):
            if index < len(manifest_tasks):
                codes_by_rid[rid] = manifest_tasks[index]["code"]
    if milestone is not None:
        record_ids = record_ids[:milestone]

    for rid in record_ids:
        record = store.records[rid]
        status_counts[record.status] += 1
        bucket = _verdict_bucket(record.teacher_review)
        verdict_counts[bucket] += 1
        if record.teacher_review and len(samples) < 5:
            code = codes_by_rid.get(rid, rid)
            samples.append(
                {
                    "id": rid,
                    "code": code,
                    "status": record.status,
                    "teacher_review": (record.teacher_review or "")[:240],
                }
            )

    total = len(record_ids)
    processed = sum(
        1
        for rid in record_ids
        if store.records[rid].status in {"reviewed", "promoted"}
    )
    promoted = status_counts.get("promoted", 0)
    save_n = verdict_counts.get("Save", 0)
    watch_n = verdict_counts.get("Watch", 0)
    kill_n = verdict_counts.get("Kill", 0)

    manifest_total = len(manifest_tasks) if manifest_tasks else len(store.records)
    closure = (
        f"KC opinion at {milestone or processed}/{manifest_total}: "
        f"Save={save_n} Watch={watch_n} Kill={kill_n} pending={verdict_counts.get('pending', 0)}; "
        f"promoted={promoted}. KC does not chat — read teacher_review per record."
    )

    return {
        "schema": "kc_apprenticeship_status_v1",
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "milestone_tasks": milestone,
        "total_tasks": total,
        "processed_reviewed_or_promoted": processed,
        "status_counts": dict(status_counts),
        "kc_opinion_counts": dict(verdict_counts),
        "promoted": promoted,
        "closure_line": closure,
        "sample_opinions": samples,
        "store_path": str(store.path),
    }


def write_checkpoint(
    milestone: int,
    store: Any,
    manifest_tasks: list[dict[str, str]],
    git_sha: str | None = None,
) -> Path:
    """Write JSON + markdown KC status at a 50-task milestone."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    payload = summarize_store(store, manifest_tasks, milestone=milestone)
    if git_sha:
        payload["git_sha"] = git_sha

    json_path = CHECKPOINT_DIR / f"kc_status_at_{milestone:03d}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_path = CHECKPOINT_DIR / f"KC_STATUS_AT_{milestone:03d}.md"
    counts = payload["kc_opinion_counts"]
    st = payload["status_counts"]
    lines = [
        f"# KC status @ {milestone} tasks",
        "",
        f"**Timestamp:** {payload['ts']}",
        "",
        "## Store",
        "",
        f"- Total: {payload['total_tasks']}",
        f"- Promoted: {payload['promoted']}",
        f"- Status: `{json.dumps(st)}`",
        "",
        "## KC opinion (teacher_review)",
        "",
        f"- Save: {counts.get('Save', 0)}",
        f"- Watch: {counts.get('Watch', 0)}",
        f"- Kill: {counts.get('Kill', 0)}",
        f"- Pending: {counts.get('pending', 0)}",
        "",
        f"> {payload['closure_line']}",
        "",
        "## Samples",
        "",
    ]
    for sample in payload["sample_opinions"]:
        lines.append(f"- **{sample['code']}** ({sample['status']}): {sample['teacher_review']}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path


def print_checkpoint_report(payload: dict[str, Any]) -> None:
    """Stdout report for operator (Cursor) — KC still does not chat."""
    m = payload.get("milestone_tasks", "?")
    print(f"\n=== KC STATUS @ {m} tasks ===")
    print(payload["closure_line"])
    print(f"status_counts: {payload['status_counts']}")
    print(f"kc_opinion: {payload['kc_opinion_counts']}")
    print(f"promoted: {payload['promoted']}/{payload['total_tasks']}")
    print("=" * 40)
