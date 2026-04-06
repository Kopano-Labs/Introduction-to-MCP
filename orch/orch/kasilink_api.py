from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from .bridge import bridge
from .config import settings
from .database import get_db_connection
from .tools.gig_matcher import match_gig
from .tools.loadshedding import get_loadshedding_status, is_gig_safe

router = APIRouter(prefix="/api/kasilink", tags=["kasilink"])


class GigMatchRequest(BaseModel):
    description: str
    location: str
    category: str
    skills: List[str] = Field(default_factory=list)
    providers: List[Dict[str, Any]] = Field(default_factory=list)


class SentimentRequest(BaseModel):
    text: str


class NotifyRequest(BaseModel):
    recipient: str
    message: Optional[str] = None
    gig_data: Optional[Dict[str, Any]] = None
    booking_data: Optional[Dict[str, Any]] = None


class ModerateRequest(BaseModel):
    text: str
    context: Optional[str] = None


class ForecastRequest(BaseModel):
    category: str
    area: str
    horizon_days: int = 7
    recent_demand: List[int] = Field(default_factory=list)


def _require_bridge_auth(authorization: Optional[str]) -> None:
    if settings.clerk_secret_key and not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "kasilink-orch",
        "features": ["match", "sentiment", "forecast", "loadshedding", "moderate", "dashboard", "notify"],
    }


@router.post("/match")
def gig_match(request: GigMatchRequest, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    return match_gig(request.description, request.location, request.category, request.skills, request.providers)


@router.post("/sentiment")
def sentiment(request: SentimentRequest, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    text = request.text.strip()
    score = 1 if any(word in text.lower() for word in ["great", "good", "excellent", "love"]) else -1 if any(
        word in text.lower() for word in ["bad", "terrible", "hate", "scam"]
    ) else 0
    return {"text": request.text, "score": score, "label": "positive" if score > 0 else "negative" if score < 0 else "neutral"}


@router.post("/forecast")
def forecast(request: ForecastRequest, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    baseline = sum(request.recent_demand) / len(request.recent_demand) if request.recent_demand else 5.0
    area_factor = (sum(ord(char) for char in request.area.lower()) % 5) / 10.0
    category_factor = 0.2 if request.category.lower() in {"delivery", "repairs", "cleaning"} else 0.1
    forecast_units = round(baseline * (1 + area_factor + category_factor), 2)
    demand_band = "high" if forecast_units >= 8 else "medium" if forecast_units >= 4 else "low"
    return {
        "category": request.category,
        "area": request.area,
        "horizon_days": request.horizon_days,
        "predicted_jobs": forecast_units,
        "predicted_demand": demand_band,
        "confidence": round(min(0.92, 0.55 + (len(request.recent_demand) * 0.03)), 2),
    }


@router.get("/loadshedding")
def loadshedding(area_id: str, start_time: Optional[str] = None, duration_hours: float = 1.0, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    if start_time:
        return is_gig_safe(area_id, start_time, duration_hours)
    return get_loadshedding_status(area_id)


@router.post("/moderate")
def moderate(request: ModerateRequest, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    lowered = request.text.lower()
    blocked_terms = ["scam", "hate", "kill", "attack", "fraud", "explicit"]
    matched = [term for term in blocked_terms if term in lowered]
    severity = "high" if any(term in matched for term in ["kill", "attack", "explicit"]) else "medium" if matched else "low"
    approved = not matched
    return {
        "approved": approved,
        "severity": severity,
        "matched_terms": matched,
        "reason": "content accepted" if approved else "content requires review",
        "context": request.context,
    }


@router.get("/dashboard")
def dashboard() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM discussions")
    discussions = int(cursor.fetchone()["count"])
    cursor.execute("SELECT COUNT(*) AS count FROM audit_logs")
    audit_logs = int(cursor.fetchone()["count"])
    conn.close()
    return {
        "ai": "transparent",
        "status": "ready",
        "features": ["match", "sentiment", "forecast", "loadshedding", "moderate", "notify"],
        "metrics": {
            "discussions": discussions,
            "audit_logs": audit_logs,
            "whatsapp_bridge_configured": bridge.is_configured(),
        },
    }


@router.post("/notify")
async def notify(request: NotifyRequest, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    if request.gig_data:
        success = await bridge.send_gig_notification(request.gig_data, request.recipient)
    elif request.booking_data:
        success = await bridge.send_booking_confirmation(request.booking_data, request.recipient)
    else:
        success = await bridge.send_message(request.message or "KasiLink notification", request.recipient)
    return {"sent": success}
