from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None


@dataclass
class LoadsheddingWindow:
    start_hour: int
    end_hour: int
    stage: int


DEFAULT_WINDOWS: Dict[int, List[LoadsheddingWindow]] = {
    1: [LoadsheddingWindow(18, 20, 1)],
    2: [LoadsheddingWindow(6, 8, 2), LoadsheddingWindow(18, 20, 2)],
    3: [LoadsheddingWindow(4, 6, 3), LoadsheddingWindow(16, 18, 3)],
    4: [LoadsheddingWindow(0, 2, 4), LoadsheddingWindow(8, 10, 4), LoadsheddingWindow(18, 20, 4)],
}


def _current_stage(area_id: str) -> int:
    provider_url = os.getenv("LOADSHEDDING_PROVIDER_URL")
    if provider_url and httpx:
        try:
            response = httpx.get(provider_url, timeout=5.0)
            if response.status_code == 200:
                payload = response.json()
                stage = int(payload.get("stage", 2))
                return max(0, min(stage, 8))
        except Exception:
            pass
    return 2


def get_loadshedding_status(area_id: str) -> dict:
    stage = _current_stage(area_id)
    windows = [
        {"start_hour": window.start_hour, "end_hour": window.end_hour, "stage": window.stage}
        for window in DEFAULT_WINDOWS.get(stage, [])
    ]
    return {
        "area_id": area_id,
        "stage": stage,
        "windows": windows,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def is_gig_safe(area_id: str, start_time: str, duration_hours: float = 1.0) -> dict:
    status = get_loadshedding_status(area_id)
    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    end_dt = start_dt + timedelta(hours=duration_hours)
    unsafe = False
    for window in status["windows"]:
        window_start = start_dt.replace(hour=window["start_hour"], minute=0, second=0, microsecond=0)
        window_end = start_dt.replace(hour=window["end_hour"], minute=0, second=0, microsecond=0)
        if start_dt < window_end and end_dt > window_start:
            unsafe = True
            break
    return {
        "area_id": area_id,
        "safe": not unsafe,
        "stage": status["stage"],
        "status": status,
    }
