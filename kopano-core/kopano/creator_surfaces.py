"""
Creator Surfaces — Phase 8 production module.

Extends Cowork with:
  - Cassy Code: repo-aware coding partner with craft memory
  - Cassy Canvas: prompt-to-UI wireframe generation
  - Cassy Research: source-grounded research pipeline

LPM principle: All surfaces operate offline-first with local state.
"""

from __future__ import annotations

import json
import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .database import get_db_connection, init_db, record_creator_event

CREATOR_DB_PATH = Path(os.environ.get(
    "CREATOR_DB_PATH",
    str(Path.home() / ".kopano" / "creator_surfaces.db"),
))


def _get_creator_db() -> sqlite3.Connection:
    CREATOR_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CREATOR_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS craft_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            surface_id TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_key TEXT NOT NULL,
            pattern_value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            learned_at TEXT NOT NULL,
            UNIQUE(surface_id, pattern_type, pattern_key)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS code_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            language TEXT NOT NULL,
            intent TEXT,
            input_snippet TEXT,
            output_snippet TEXT,
            accepted BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS canvas_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            artifact_type TEXT DEFAULT 'wireframe',
            component_name TEXT,
            output_format TEXT DEFAULT 'description',
            content TEXT NOT NULL,
            tokens_used TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            sources TEXT,
            findings TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            grounded_in TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


# ─── CASSY CODE ──────────────────────────────────────────────────────────────


def learn_pattern(
    pattern_type: str,
    pattern_key: str,
    pattern_value: str,
    confidence: float = 0.7,
) -> dict[str, Any]:
    """Learn a coding pattern from user behavior. Builds craft memory."""
    conn = _get_creator_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO craft_memory (surface_id, pattern_type, pattern_key, pattern_value, confidence, learned_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("cassy-code", pattern_type, pattern_key, pattern_value, confidence, now),
    )
    conn.commit()
    conn.close()
    return {
        "status": "learned",
        "pattern_type": pattern_type,
        "pattern_key": pattern_key,
        "confidence": confidence,
    }


def recall_patterns(pattern_type: str | None = None) -> list[dict[str, Any]]:
    """Recall learned coding patterns from craft memory."""
    conn = _get_creator_db()
    if pattern_type:
        rows = conn.execute(
            "SELECT * FROM craft_memory WHERE surface_id = 'cassy-code' AND pattern_type = ? ORDER BY confidence DESC",
            (pattern_type,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM craft_memory WHERE surface_id = 'cassy-code' ORDER BY confidence DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_code_session(
    language: str,
    intent: str,
    input_snippet: str,
    output_snippet: str,
    accepted: bool = False,
) -> dict[str, Any]:
    """Record a coding session for pattern learning."""
    conn = _get_creator_db()
    now = datetime.now(timezone.utc).isoformat()
    import hashlib
    session_id = hashlib.sha256(f"{now}:{intent}".encode()).hexdigest()[:12]
    conn.execute(
        "INSERT INTO code_sessions (session_id, language, intent, input_snippet, output_snippet, accepted, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (session_id, language, intent, input_snippet, output_snippet, accepted, now),
    )
    conn.commit()
    conn.close()

    if accepted:
        learn_pattern(
            pattern_type=f"lang:{language}",
            pattern_key=intent,
            pattern_value=output_snippet[:500],
            confidence=0.8,
        )

    return {"session_id": session_id, "accepted": accepted, "language": language}


# ─── CASSY CANVAS ────────────────────────────────────────────────────────────


COMPONENT_TEMPLATES = {
    "button": {
        "type": "component",
        "framework": "react-tailwind",
        "template": '<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">{label}</button>',
    },
    "card": {
        "type": "component",
        "framework": "react-tailwind",
        "template": '<div className="p-6 bg-white rounded-xl shadow-md border border-gray-100"><h3 className="text-lg font-semibold">{title}</h3><p className="mt-2 text-gray-600">{description}</p></div>',
    },
    "input": {
        "type": "component",
        "framework": "react-tailwind",
        "template": '<input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="{placeholder}" />',
    },
    "navbar": {
        "type": "layout",
        "framework": "react-tailwind",
        "template": '<nav className="flex items-center justify-between px-6 py-4 bg-white shadow-sm"><div className="text-xl font-bold">{brand}</div><div className="flex gap-4">{links}</div></nav>',
    },
    "hero": {
        "type": "layout",
        "framework": "react-tailwind",
        "template": '<section className="flex flex-col items-center justify-center min-h-[60vh] px-6 text-center"><h1 className="text-5xl font-bold tracking-tight">{headline}</h1><p className="mt-4 text-xl text-gray-600 max-w-2xl">{subheadline}</p></section>',
    },
}


def generate_wireframe(
    prompt: str,
    output_format: str = "description",
) -> dict[str, Any]:
    """Generate a wireframe description from a natural language prompt."""
    conn = _get_creator_db()
    now = datetime.now(timezone.utc).isoformat()

    prompt_lower = prompt.lower()
    components_used = []
    for name, template in COMPONENT_TEMPLATES.items():
        if name in prompt_lower:
            components_used.append({"name": name, **template})

    if not components_used:
        if any(w in prompt_lower for w in ["landing", "home", "page"]):
            components_used = [
                {"name": "navbar", **COMPONENT_TEMPLATES["navbar"]},
                {"name": "hero", **COMPONENT_TEMPLATES["hero"]},
                {"name": "card", **COMPONENT_TEMPLATES["card"]},
            ]
        elif any(w in prompt_lower for w in ["form", "input", "login", "signup"]):
            components_used = [
                {"name": "input", **COMPONENT_TEMPLATES["input"]},
                {"name": "button", **COMPONENT_TEMPLATES["button"]},
            ]
        else:
            components_used = [
                {"name": "card", **COMPONENT_TEMPLATES["card"]},
                {"name": "button", **COMPONENT_TEMPLATES["button"]},
            ]

    content = json.dumps({
        "prompt": prompt,
        "layout": "vertical-stack",
        "components": [c["name"] for c in components_used],
        "suggested_structure": components_used,
    })

    conn.execute(
        "INSERT INTO canvas_artifacts (prompt, artifact_type, output_format, content, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (prompt, "wireframe", output_format, content, now),
    )
    conn.commit()
    conn.close()

    return {
        "wireframe": {
            "prompt": prompt,
            "components": components_used,
            "layout": "vertical-stack",
            "framework": "react-tailwind",
        },
        "offline": True,
        "surface": "cassy-canvas",
    }


# ─── CASSY RESEARCH ──────────────────────────────────────────────────────────


def research_query(
    query: str,
    grounded_in: str = "local",
) -> dict[str, Any]:
    """Execute a research query against local knowledge base."""
    conn = _get_creator_db()
    now = datetime.now(timezone.utc).isoformat()

    REPO_ROOT = Path(__file__).resolve().parents[2]
    schematics_path = REPO_ROOT / "Schematics"
    docs_path = REPO_ROOT / "docs"

    local_sources = []
    if schematics_path.exists():
        for f in schematics_path.rglob("*.md"):
            local_sources.append(str(f.relative_to(REPO_ROOT)))
    if docs_path.exists():
        for f in docs_path.rglob("*.md"):
            local_sources.append(str(f.relative_to(REPO_ROOT)))

    findings = f"Query: {query}\nLocal sources available: {len(local_sources)}\nGrounded in: {grounded_in}"

    conn.execute(
        "INSERT INTO research_entries (query, sources, findings, confidence, grounded_in, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (query, json.dumps(local_sources[:20]), findings, 0.6, grounded_in, now),
    )
    conn.commit()
    conn.close()

    return {
        "query": query,
        "sources_available": len(local_sources),
        "sample_sources": local_sources[:10],
        "grounded_in": grounded_in,
        "confidence": 0.6,
        "surface": "cassy-research",
        "offline": True,
    }


# ─── UNIFIED SURFACE STATUS ─────────────────────────────────────────────────


def get_creator_surfaces_status() -> dict[str, Any]:
    """Return status of all creator surfaces."""
    conn = _get_creator_db()
    patterns = conn.execute("SELECT COUNT(*) as c FROM craft_memory").fetchone()["c"]
    sessions = conn.execute("SELECT COUNT(*) as c FROM code_sessions").fetchone()["c"]
    canvases = conn.execute("SELECT COUNT(*) as c FROM canvas_artifacts").fetchone()["c"]
    researches = conn.execute("SELECT COUNT(*) as c FROM research_entries").fetchone()["c"]
    conn.close()

    return {
        "surfaces": {
            "cassy-forge": {"status": "production", "phase": 8},
            "cassy-code": {"status": "building", "phase": 8, "patterns_learned": patterns, "sessions": sessions},
            "cassy-canvas": {"status": "building", "phase": 8, "artifacts": canvases},
            "cassy-research": {"status": "building", "phase": 8, "entries": researches},
        },
        "total_craft_memory": patterns,
        "offline_capable": True,
        "lpm_status": "production",
    }
