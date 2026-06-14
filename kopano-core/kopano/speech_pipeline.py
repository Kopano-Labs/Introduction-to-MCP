"""
Speech Pipeline — Production layer for SA Language Engine (Phase 7)

LPM Principle: Offline-first. Phrasebook is deterministic and always available.
Cloud STT/TTS is the enhancement layer, not the backbone.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .labs_registry import SA_LANGUAGE_SUPPORT, ACCESS_MODES
from .language_runtime import (
    LANGUAGE_BY_ID,
    PHRASEBOOK,
    DOMAIN_GLOSSARY,
    detect_language,
    translate_text,
    build_multilingual_response,
)
from .sa_access import build_access_plan, execute_access_session

SpeechMode = Literal["offline", "hybrid", "cloud"]

SPEECH_DB_PATH = Path(os.environ.get(
    "SPEECH_DB_PATH",
    str(Path.home() / ".kopano" / "speech_cache.db"),
))


def _get_speech_db() -> sqlite3.Connection:
    SPEECH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SPEECH_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tts_cache (
            text_hash TEXT PRIMARY KEY,
            language_id TEXT NOT NULL,
            text_content TEXT NOT NULL,
            audio_path TEXT,
            provider TEXT DEFAULT 'offline',
            cached_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stt_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            language_id TEXT NOT NULL,
            raw_text TEXT,
            cleaned_text TEXT,
            confidence REAL,
            mode TEXT DEFAULT 'offline',
            processed_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS language_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_id TEXT NOT NULL,
            action TEXT NOT NULL,
            domain TEXT DEFAULT 'general',
            ts TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def _detect_network() -> bool:
    """Quick check if network is reachable. LPM: fail closed = offline."""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except (OSError, socket.timeout):
        return False


def _text_hash(text: str, language_id: str) -> str:
    return hashlib.sha256(f"{language_id}:{text}".encode()).hexdigest()[:16]


def resolve_speech_mode() -> SpeechMode:
    """Determine current speech mode based on environment and network."""
    forced = os.environ.get("SPEECH_MODE", "").lower()
    if forced in ("offline", "hybrid", "cloud"):
        return forced  # type: ignore

    has_network = _detect_network()
    has_api_key = bool(os.environ.get("AZURE_SPEECH_KEY") or os.environ.get("GOOGLE_SPEECH_KEY"))

    if has_network and has_api_key:
        return "hybrid"
    return "offline"


def speech_to_text(
    audio_input: str | bytes | None = None,
    text_fallback: str = "",
    preferred_language: str | None = None,
    mode: SpeechMode | None = None,
) -> dict[str, Any]:
    """
    Process speech input → text. In offline mode, accepts text_fallback directly.
    In hybrid/cloud mode, would process audio through STT provider.
    """
    active_mode = mode or resolve_speech_mode()
    detected_lang = detect_language(text_fallback or "", preferred_language=preferred_language)
    now = datetime.now(timezone.utc).isoformat()

    if active_mode == "offline" or audio_input is None:
        cleaned = " ".join((text_fallback or "").split())
        confidence = 0.95 if cleaned else 0.0

        conn = _get_speech_db()
        conn.execute(
            "INSERT INTO stt_sessions (session_id, language_id, raw_text, cleaned_text, confidence, mode, processed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (_text_hash(cleaned, detected_lang["id"]), detected_lang["id"], text_fallback, cleaned, confidence, "offline", now),
        )
        conn.execute(
            "INSERT INTO language_usage (language_id, action, ts) VALUES (?, ?, ?)",
            (detected_lang["id"], "stt_offline", now),
        )
        conn.commit()
        conn.close()

        return {
            "text": cleaned,
            "language": detected_lang,
            "confidence": confidence,
            "mode": "offline",
            "provider": "phrasebook-fallback",
            "requires_confirmation": confidence < 0.8,
        }

    # Hybrid/cloud mode — STT provider call (Azure Speech / Google Speech)
    # Production stub: when API keys are configured, this calls the provider
    return {
        "text": text_fallback,
        "language": detected_lang,
        "confidence": 0.85,
        "mode": active_mode,
        "provider": "azure_speech" if os.environ.get("AZURE_SPEECH_KEY") else "google_speech",
        "requires_confirmation": True,
        "note": "Cloud STT available but not yet wired — uses text fallback",
    }


def text_to_speech(
    text: str,
    target_language: str | None = None,
    mode: SpeechMode | None = None,
) -> dict[str, Any]:
    """
    Convert text → speech output. In offline mode, returns the text with
    phonetic hints and cached pronunciation guidance.
    """
    active_mode = mode or resolve_speech_mode()
    lang = detect_language("", preferred_language=target_language)
    text_h = _text_hash(text, lang["id"])
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_speech_db()
    cached = conn.execute(
        "SELECT audio_path, provider FROM tts_cache WHERE text_hash = ?", (text_h,)
    ).fetchone()

    if cached and cached["audio_path"]:
        conn.close()
        return {
            "text": text,
            "language": lang,
            "mode": "cached",
            "audio_path": cached["audio_path"],
            "provider": cached["provider"],
        }

    conn.execute(
        "INSERT OR REPLACE INTO tts_cache (text_hash, language_id, text_content, provider, cached_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (text_h, lang["id"], text, "offline", now),
    )
    conn.execute(
        "INSERT INTO language_usage (language_id, action, ts) VALUES (?, ?, ?)",
        (lang["id"], "tts_request", now),
    )
    conn.commit()
    conn.close()

    if active_mode == "offline":
        return {
            "text": text,
            "language": lang,
            "mode": "offline",
            "audio_path": None,
            "provider": "text-display",
            "display_text": text,
            "phonetic_hint": _get_phonetic_hint(text, lang["id"]),
        }

    return {
        "text": text,
        "language": lang,
        "mode": active_mode,
        "audio_path": None,
        "provider": "azure_tts" if os.environ.get("AZURE_SPEECH_KEY") else "pending",
        "note": "Cloud TTS available but audio generation pending configuration",
    }


def _get_phonetic_hint(text: str, language_id: str) -> str | None:
    """Return a basic phonetic hint for common SA language phrases."""
    hints = {
        "zu-za": {"sawubona": "sah-woo-BOH-nah", "ngiyabonga": "ngee-yah-BOHN-gah"},
        "xh-za": {"molo": "MOH-loh", "enkosi": "en-KOH-see"},
        "tn-za": {"dumela": "doo-MEH-lah", "ke a leboga": "keh ah leh-BOH-gah"},
        "af-za": {"dankie": "DAHN-kee", "hallo": "HAH-loh"},
        "ts-za": {"avuxeni": "ah-voo-SHEH-nee"},
        "ve-za": {"ndaa": "NDAH-ah"},
    }
    lang_hints = hints.get(language_id, {})
    lower = text.lower().strip()
    return lang_hints.get(lower)


def process_multilingual_turn(
    message: str,
    preferred_language: str | None = None,
    speech_impairment: bool = False,
    domain: str = "general",
    mode: SpeechMode | None = None,
) -> dict[str, Any]:
    """
    Full production turn: STT → language detection → access plan → response → TTS.
    This is the Phase 7 production pipeline.
    """
    active_mode = mode or resolve_speech_mode()

    stt_result = speech_to_text(
        text_fallback=message,
        preferred_language=preferred_language,
        mode=active_mode,
    )

    access_plan = build_access_plan(
        preferred_language=preferred_language,
        speech_impairment=speech_impairment,
    )

    session_result = execute_access_session(
        message=stt_result["text"],
        preferred_language=preferred_language,
        speech_impairment=speech_impairment,
    )

    multilingual = build_multilingual_response(
        text=stt_result["text"],
        preferred_language=preferred_language,
        domain=domain,
    )

    tts_result = text_to_speech(
        text=multilingual["translation"]["translated_text"],
        target_language=multilingual["language"]["id"],
        mode=active_mode,
    )

    return {
        "input": {
            "original_message": message,
            "stt": stt_result,
        },
        "processing": {
            "detected_language": multilingual["language"],
            "access_mode": access_plan["recommended_mode"],
            "confidence": session_result["confidence"],
            "requires_confirmation": session_result["requires_confirmation"],
        },
        "output": {
            "translated": multilingual["translation"],
            "labels": multilingual["response_labels"],
            "glossary": multilingual["glossary_terms"],
            "tts": tts_result,
        },
        "pipeline": {
            "mode": active_mode,
            "offline_capable": True,
            "lpm_status": "production",
            "phase": "7",
        },
    }


def get_language_analytics() -> dict[str, Any]:
    """Return usage analytics for the language engine."""
    conn = _get_speech_db()
    usage = conn.execute(
        "SELECT language_id, action, COUNT(*) as count FROM language_usage "
        "GROUP BY language_id, action ORDER BY count DESC"
    ).fetchall()
    total_sessions = conn.execute("SELECT COUNT(*) as c FROM stt_sessions").fetchone()["c"]
    total_tts = conn.execute("SELECT COUNT(*) as c FROM tts_cache").fetchone()["c"]
    conn.close()

    return {
        "total_stt_sessions": total_sessions,
        "total_tts_entries": total_tts,
        "usage_by_language": [dict(row) for row in usage],
        "supported_languages": len(SA_LANGUAGE_SUPPORT),
        "offline_capable": True,
    }
