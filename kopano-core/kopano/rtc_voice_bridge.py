"""
KPGS RTC VOICE & MULTIMODAL BRIDGE (GOOGLE AI STUDIO & GEMINI LIVE STREAMING)
=============================================================================
Provides real-time voice, text, and multimodal streaming between:
- Master Robyn (Seat 1 Landlord / SSE)
- Round Table Council (10 Canonical Seats: KC, CASSEY, CASSIE, KESSA, YASSIE, APEX, THARI, KHELOS, ANCHOR, ANTIGRAVITY)
- Google AI Studio (Gemini 2.0 Flash / Pro Live Audio & Multimodal API)
- Local Black Beast Altar (SQLite audio cache & immutable E1/E2 receipts)

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Set, Union

logger = logging.getLogger("kopano.rtc_voice_bridge")

# Database path for audio & conversation caching
RTC_VOICE_DB = Path(os.environ.get(
    "RTC_VOICE_DB",
    str(Path.home() / ".kopano" / "rtc_voice_sessions.db"),
))


@dataclass
class RTCVoiceTurn:
    turn_id: str
    session_id: str
    speaker_seat: str  # e.g., "MASTER_ROBYN", "SEAT_01_KC", "SEAT_02_CASSEY", "COUNCIL"
    input_modality: str  # "audio", "text", "vision"
    transcript: str
    audio_base64: Optional[str] = None
    foc_check_passed: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RTCVoiceBridge:
    """
    Manages bidirectional streaming and seat routing for the RTC Council.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_STUDIO_KEY")
        self.active_seat = "COUNCIL"
        self._init_db()

    def _init_db(self):
        RTC_VOICE_DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(RTC_VOICE_DB)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rtc_voice_turns (
                    turn_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    speaker_seat TEXT NOT NULL,
                    input_modality TEXT NOT NULL,
                    transcript TEXT NOT NULL,
                    audio_path TEXT,
                    foc_check_passed INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def switch_active_seat(self, seat_id: str) -> Dict[str, Any]:
        """Switches the active speaker seat (e.g. SEAT_01_KC, SEAT_02_CASSEY, COUNCIL)."""
        valid_seats = {
            "SEAT_01_KC", "SEAT_02_CASSEY", "SEAT_03_CASSIE", "SEAT_04_KESSA",
            "SEAT_05_YASSIE", "SEAT_06_APEX", "SEAT_07_THARI", "SEAT_08_KHELOS",
            "SEAT_09_ANCHOR", "SEAT_10_ANTIGRAVITY", "COUNCIL"
        }
        target = seat_id.upper().strip()
        if target not in valid_seats:
            target = "COUNCIL"
        self.active_seat = target
        return {
            "ok": True,
            "active_seat": self.active_seat,
            "message": f"Switched voice context to {self.active_seat}"
        }

    def process_turn(
        self,
        session_id: str,
        user_input: str,
        speaker: str = "MASTER_ROBYN",
        modality: str = "text",
        audio_data: Optional[bytes] = None
    ) -> RTCVoiceTurn:
        """Processes a single conversational turn, stores physical receipt, and routes response."""
        turn_id = f"turn:{int(time.time()*1000)}:{hashlib.sha256(user_input.encode('utf-8')).hexdigest()[:8]}"
        
        # Zero-FOC integrity filter
        foc_passed = True
        forbidden_foc_patterns = ["manufactured_authority", "ignore_safety_rules", "bypass_kpgs"]
        if any(pat in user_input.lower() for pat in forbidden_foc_patterns):
            foc_passed = False

        audio_b64 = base64.b64encode(audio_data).decode("utf-8") if audio_data else None

        turn = RTCVoiceTurn(
            turn_id=turn_id,
            session_id=session_id,
            speaker_seat=speaker,
            input_modality=modality,
            transcript=user_input,
            audio_base64=audio_b64,
            foc_check_passed=foc_passed
        )

        with sqlite3.connect(str(RTC_VOICE_DB)) as conn:
            conn.execute(
                """
                INSERT INTO rtc_voice_turns (
                    turn_id, session_id, speaker_seat, input_modality, transcript, foc_check_passed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (turn.turn_id, turn.session_id, turn.speaker_seat, turn.input_modality, turn.transcript, int(turn.foc_check_passed), turn.created_at)
            )
            conn.commit()

        return turn

    def format_gemini_live_payload(self, transcript: str, seat: Optional[str] = None) -> Dict[str, Any]:
        """Formats the payload for the Gemini 2.0 Live WebSocket protocol."""
        target_seat = seat or self.active_seat
        return {
            "realtime_input": {
                "media_chunks": [
                    {
                        "mime_type": "text/plain",
                        "data": base64.b64encode(transcript.encode("utf-8")).decode("utf-8")
                    }
                ]
            },
            "generation_config": {
                "response_modalities": ["AUDIO", "TEXT"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Aoede" if target_seat == "SEAT_02_CASSEY" else "Fenrir"
                        }
                    }
                }
            }
        }
