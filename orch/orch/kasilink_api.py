from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from .bridge import bridge
from .config import settings
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


def _require_bridge_auth(authorization: Optional[str]) -> None:
    if settings.clerk_secret_key and not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "kasilink-orch"}


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


@router.get("/forecast")
def forecast(category: str, area: str, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    return {"category": category, "area": area, "predicted_demand": "medium", "confidence": 0.67}


@router.get("/loadshedding")
def loadshedding(area_id: str, start_time: Optional[str] = None, duration_hours: float = 1.0, authorization: Optional[str] = Header(default=None)) -> dict:
    _require_bridge_auth(authorization)
    if start_time:
        return is_gig_safe(area_id, start_time, duration_hours)
    return get_loadshedding_status(area_id)


@router.get("/dashboard")
def dashboard() -> dict:
    return {"ai": "transparent", "status": "ready", "features": ["match", "sentiment", "forecast", "loadshedding", "notify"]}


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
