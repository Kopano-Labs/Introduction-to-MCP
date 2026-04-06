from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
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


def _normalize_stage(stage: int) -> int:
    return max(0, min(int(stage), 8))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_datetime(value: Optional[str]) -> datetime:
    if not value:
        return _utc_now()
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _default_windows_for_stage(stage: int, area_id: str) -> List[Dict[str, Any]]:
    now = _utc_now()
    area_offset = sum(ord(char) for char in area_id) % 3
    windows = []
    for window in DEFAULT_WINDOWS.get(stage, []):
        start_hour = (window.start_hour + area_offset * 2) % 24
        end_hour = (window.end_hour + area_offset * 2) % 24
        start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        if end <= start:
            end += timedelta(days=1)
        if end < now:
            start += timedelta(days=1)
            end += timedelta(days=1)
        windows.append(
            {
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
                "stage": window.stage,
            }
        )
    return windows


def _parse_provider_payload(payload: Dict[str, Any], area_id: str) -> Dict[str, Any]:
    stage = _normalize_stage(payload.get("stage", 2))
    windows_payload = payload.get("windows") or payload.get("events") or []
    windows: List[Dict[str, Any]] = []
    for item in windows_payload:
        if not isinstance(item, dict):
            continue
        start = item.get("start") or item.get("start_time")
        end = item.get("end") or item.get("end_time")
        if not start or not end:
            continue
        windows.append(
            {
                "start": str(start),
                "end": str(end),
                "stage": _normalize_stage(item.get("stage", stage)),
            }
        )
    if not windows:
        windows = _default_windows_for_stage(stage, area_id)
    return {"stage": stage, "windows": windows}


def _current_stage(area_id: str) -> int:
    provider_url = os.getenv("LOADSHEDDING_PROVIDER_URL")
    if provider_url and httpx:
        try:
            response = httpx.get(provider_url, timeout=5.0)
            if response.status_code == 200:
                payload = response.json()
                stage = int(payload.get("stage", 2))
                return _normalize_stage(stage)
        except Exception:
            pass
    return 2


def _provider_status(area_id: str) -> Dict[str, Any]:
    provider_url = os.getenv("LOADSHEDDING_PROVIDER_URL")
    if provider_url and httpx:
        try:
            response = httpx.get(provider_url, timeout=5.0)
            if response.status_code == 200:
                payload = response.json()
                return _parse_provider_payload(payload, area_id)
        except Exception:
            pass
    stage = _current_stage(area_id)
    return {"stage": stage, "windows": _default_windows_for_stage(stage, area_id)}


def _current_and_next_windows(windows: List[Dict[str, Any]], now: datetime) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    current_window = None
    next_window = None
    ordered = sorted(windows, key=lambda item: item["start"])
    for window in ordered:
        start = _coerce_datetime(window["start"])
        end = _coerce_datetime(window["end"])
        if start <= now < end:
            current_window = window
            break
        if start > now and next_window is None:
            next_window = window
    if current_window is None and next_window is None and ordered:
        next_window = ordered[0]
    return current_window, next_window


def get_loadshedding_status(area_id: str) -> dict:
    provider_status = _provider_status(area_id)
    now = _utc_now()
    windows = []
    for window in provider_status["windows"]:
        start = _coerce_datetime(window["start"])
        end = _coerce_datetime(window["end"])
        windows.append(
            {
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
                "stage": _normalize_stage(window["stage"]),
            }
        )
    current_window, next_window = _current_and_next_windows(windows, now)
    return {
        "area_id": area_id,
        "stage": provider_status["stage"],
        "windows": windows,
        "active_now": current_window is not None,
        "current_window": current_window,
        "next_window": next_window,
        "updated_at": now.isoformat().replace("+00:00", "Z"),
    }


def is_gig_safe(area_id: str, start_time: str, duration_hours: float = 1.0, buffer_minutes: int = 30) -> dict:
    status = get_loadshedding_status(area_id)
    start_dt = _coerce_datetime(start_time)
    end_dt = start_dt + timedelta(hours=duration_hours)
    buffered_start = start_dt - timedelta(minutes=buffer_minutes)
    buffered_end = end_dt + timedelta(minutes=buffer_minutes)
    unsafe = False
    conflicting_windows = []
    for window in status["windows"]:
        window_start = _coerce_datetime(window["start"])
        window_end = _coerce_datetime(window["end"])
        if buffered_start < window_end and buffered_end > window_start:
            unsafe = True
            conflicting_windows.append(window)
    recommendation = (
        "Safe to schedule."
        if not unsafe
        else "Reschedule or confirm backup power before accepting this gig."
    )
    return {
        "area_id": area_id,
        "safe": not unsafe,
        "stage": status["stage"],
        "start_time": start_dt.isoformat().replace("+00:00", "Z"),
        "end_time": end_dt.isoformat().replace("+00:00", "Z"),
        "buffer_minutes": buffer_minutes,
        "conflicting_windows": conflicting_windows,
        "recommendation": recommendation,
        "status": status,
    }
