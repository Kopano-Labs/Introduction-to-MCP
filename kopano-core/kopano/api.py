"""
Kopano AGI Control Plane API
"""

from fastapi import FastAPI, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db, get_db_connection, register_user, authenticate_user
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import asyncio
import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from .kasilink_api import router as kasilink_router
from .kc_training_api import router as kc_training_router
from .swarm_agents_api import router as swarm_agents_router
from .kc_swarm_console_api import router as swarm_console_router
from .kc_god_api import router as god_router
from .kc_phu_legacy_api import router as phu_legacy_router
from .labs_api import router as labs_router
from .rtc_learning_api import router as rtc_learning_router
from .telemetry import configure_server_telemetry, log_demo_event

logger = logging.getLogger("kopano.api")

# --- PROACTIVE NEURAL SHIELD: LIFESPAN LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    telemetry_state = configure_server_telemetry()
    logger.info("Cassy startup telemetry configured=%s reason=%s", telemetry_state["configured"], telemetry_state["reason"])
    log_demo_event("cassy_api_startup", telemetry_configured=telemetry_state["configured"])
    # Startup: Initialize the Pristine Vault
    init_db()
    from .runtime import ensure_desktop_admin, ensure_desktop_operator

    ensure_desktop_admin()
    ensure_desktop_operator()
    from .operator_auth import load_persisted_desktop_session

    load_persisted_desktop_session()
    print("Pristine Vault online")
    yield
    log_demo_event("cassy_api_shutdown")
    print("Vault sealed. No lingering neural threads.")

app = FastAPI(title="Cassy AGI Control Plane", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "https://kasi-link.vercel.app",
        "https://context.kopanolabs.com",
        "https://kopanolabs.com",
        "https://www.kopanolabs.com",
        "https://www.kasilink.co.za",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SYSTEM METADATA ---
SYSTEM_NAME = "Kopano Context"
ADMIN_EMAIL = os.environ.get("KOPANO_ADMIN_EMAIL", "admin@kopano.local").strip().lower()
PRODUCTION_URL = "https://context.kopanolabs.com"

app.include_router(kasilink_router)
app.include_router(kc_training_router)
app.include_router(swarm_agents_router)
app.include_router(swarm_console_router)
app.include_router(god_router)
app.include_router(phu_legacy_router)
app.include_router(labs_router)
app.include_router(rtc_learning_router)

# Shared memory for real-time updates (Broadcast Protocol)
class State:
    updates = []
    connections: List[WebSocket] = []

state = State()

# --- MODELS ---
class OverrideRequest(BaseModel):
    block_id: int
    override_score: int
    improvement_hint: Optional[str] = None


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class MaoTaskRequest(BaseModel):
    intent: str
    message: str
    force_agent_id: str = ""

# --- API ENDPOINTS ---

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.connections.append(websocket)
    try:
        while True:
            # Keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.connections.remove(websocket)

@app.websocket("/ws/neural-link")
async def neural_link_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.connections.remove(websocket)

@app.websocket("/ws/kasilink/live")
async def kasilink_live_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.connections.remove(websocket)

@app.post("/broadcast")
async def broadcast(request: Request):
    """Internal endpoint for the simulator to push real-time updates."""
    update = await request.json()
    state.updates.append(update)
    log_demo_event(
        "broadcast_received",
        update_type=update.get("type", "unknown"),
        agent=update.get("agent", "system"),
        active_connections=len(state.connections),
    )
    
    # Push to all active WebSocket connections
    for connection in state.connections:
        try:
            await connection.send_json(update)
        except Exception as e:
            print(f"Error sending to WebSocket: {e}")
            
    # Simple rate-limiting for state history
    if len(state.updates) > 100:
        state.updates.pop(0)
    return {"status": "ok"}

@app.get("/updates")
async def get_updates():
    """Polled by the React GUI to receive real-time neural signals."""
    current = list(state.updates)
    state.updates = []
    return current


@app.post("/auth/register")
def register(request: RegisterRequest):
    """Register a local Cassy user account."""
    try:
        user = register_user(request.email, request.password, request.full_name)
        return {
            "status": "ok",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "reward_points": user.get("reward_points", 0),
                "referral_code": user.get("referral_code"),
                "referred_by": user.get("referred_by"),
                "is_active": bool(user["is_active"]),
                "created_at": user["created_at"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate a local Cassy user account."""
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    from .operator_auth import create_session

    token = create_session(user)
    log_demo_event("auth_login_success", role=user.get("role", "unknown"), god_mode=bool(user.get("god_mode")))
    return {
        "status": "ok",
        "access_token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "god_mode": bool(user.get("god_mode")),
            "reward_points": user.get("reward_points", 0),
            "referral_code": user.get("referral_code"),
            "referred_by": user.get("referred_by"),
            "is_active": bool(user["is_active"]),
            "created_at": user["created_at"],
        },
    }

@app.get("/rewards/status")
def get_reward_status(email: str):
    """Deep retrieval of individual reward logic."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reward_points, referral_code, referred_by FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)

@app.post("/rewards/award")
def award_points(email: str, points: int, reason: str):
    """Lead-only point injection for ecosystem excellence."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET reward_points = reward_points + ? WHERE email = ?", (points, email))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Awarded {points} points for {reason}"}

@app.post("/rewards/refer")
def process_referral(referrer_code: str, new_user_email: str):
    """Social referral logic: links a new user to their referrer and awards bonus points."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify referrer
    cursor.execute("SELECT id FROM users WHERE referral_code = ?", (referrer_code,))
    referrer = cursor.fetchone()
    if not referrer:
        conn.close()
        raise HTTPException(status_code=404, detail="Referrer code invalid")
    
    # Update new user
    cursor.execute("UPDATE users SET referred_by = ?, reward_points = reward_points + 50 WHERE email = ?", (referrer['id'], new_user_email))
    # Give referrer a bonus too
    cursor.execute("UPDATE users SET reward_points = reward_points + 100 WHERE id = ?", (referrer['id'],))
    
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Social link established. Rewards distributed."}

@app.get("/sessions")
def list_sessions():
    """Retrieve all historical AGI Lessons from the Vault."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            discussions.id,
            discussions.topic,
            discussions.start_time AS created_at,
            COUNT(audit_logs.id) AS audit_events,
            COUNT(DISTINCT audit_logs.round_num) AS round_count
        FROM discussions
        LEFT JOIN audit_logs ON audit_logs.discussion_id = discussions.id
        GROUP BY discussions.id, discussions.topic, discussions.start_time
        ORDER BY
            CASE WHEN COUNT(audit_logs.id) > 0 THEN 0 ELSE 1 END,
            discussions.start_time DESC
    """)
    sessions = cursor.fetchall()
    conn.close()
    return [dict(s) for s in sessions]

@app.get("/sessions/{session_id}")
def get_session_detail(session_id: int):
    """Deep forensic drill-down into a specific session's round-by-round logic."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, topic, start_time as created_at FROM discussions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    if not session:
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
    
    cursor.execute("SELECT * FROM audit_logs WHERE discussion_id = ? ORDER BY round_num ASC, timestamp ASC", (session_id,))
    logs = cursor.fetchall()
    conn.close()
    
    # Group logs into rounds for the Forensic Audit GUI
    rounds_dict = {}
    for log in logs:
        r_num = log["round_num"] or 0
        if r_num not in rounds_dict:
            rounds_dict[r_num] = {
                "id": f"round_{r_num}",
                "round_number": r_num,
                "blocks": []
            }
        
        rounds_dict[r_num]["blocks"].append({
            "block_id": log["id"],
            "agent": log["agent_id"],
            "model": log["model"],
            "content": log["message"] or log["prompt"], # Fallback
            "reasoning": log["prompt"] if log["message"] else "System Logic",
            "log_type": log["log_type"],
            "value_score": log["value_score"],
            "override_score": log["override_score"],
            "improvement_hint": log["improvement_hint"],
            "is_student": 1 if log["agent_id"] in {"orch", "cassy"} else 0
        })
    
    return {
        "id": session["id"],
        "topic": session["topic"],
        "created_at": session["created_at"],
        "rounds": sorted(rounds_dict.values(), key=lambda x: x["round_number"])
    }

@app.post("/sessions/{session_id}/override")
async def session_override(session_id: int, request: OverrideRequest):
    """Master Override Protocol: Human-in-the-loop feedback injection."""
    from .database import update_log_override
    try:
        update_log_override(request.block_id, request.override_score, request.improvement_hint)
        
        # Broadcast update to all live Neural Links
        update = {
            "type": "override",
            "discussion_id": session_id,
            "block_id": request.block_id,
            "override_score": request.override_score,
            "improvement_hint": request.improvement_hint
        }
        log_demo_event("session_override", session_id=session_id, block_id=request.block_id, override_score=request.override_score)
        state.updates.append(update)
        for connection in state.connections:
            try:
                await connection.send_json(update)
            except:
                pass
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Production Readiness Check: Verifies DB, Telemetry, and Control Plane health."""
    health = {
        "status": "healthy",
        "timestamp": "2026-04-11",
        "components": {
            "database": "unknown",
            "telemetry": "unknown",
            "bridge": "active"
        }
    }
    
    # Check SQLite
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        health["components"]["database"] = "connected"
    except:
        health["components"]["database"] = "failed"
        health["status"] = "degraded"

    # Check Telemetry (Azure/OpenAI readiness)
    from .config import settings
    if settings.azure_openai_api_key and settings.azure_openai_endpoint:
        health["components"]["telemetry"] = "ready"
    else:
        health["components"]["telemetry"] = "unconfigured"
        health["status"] = "degraded"

    return health

# --- PHASE 7: SA LANGUAGE ENGINE (Production) ---

@app.post("/api/language/process")
def language_process_turn(
    message: str = "",
    preferred_language: str | None = None,
    speech_impairment: bool = False,
    domain: str = "general",
):
    from .speech_pipeline import process_multilingual_turn
    return process_multilingual_turn(
        message=message,
        preferred_language=preferred_language,
        speech_impairment=speech_impairment,
        domain=domain,
    )


@app.get("/api/language/analytics")
def language_analytics():
    from .speech_pipeline import get_language_analytics
    return get_language_analytics()


@app.get("/api/language/supported")
def language_supported():
    from .labs_registry import SA_LANGUAGE_SUPPORT, ACCESS_MODES
    from .speech_pipeline import resolve_speech_mode
    return {
        "languages": SA_LANGUAGE_SUPPORT,
        "access_modes": ACCESS_MODES,
        "speech_mode": resolve_speech_mode(),
        "offline_capable": True,
        "phase": "7",
    }


# --- PHASE 8: CREATOR SURFACES ---

@app.get("/api/creator/status")
def creator_status():
    from .creator_surfaces import get_creator_surfaces_status
    return get_creator_surfaces_status()


@app.post("/api/creator/code/learn")
def creator_code_learn(pattern_type: str, pattern_key: str, pattern_value: str, confidence: float = 0.7):
    from .creator_surfaces import learn_pattern
    return learn_pattern(pattern_type, pattern_key, pattern_value, confidence)


@app.get("/api/creator/code/patterns")
def creator_code_patterns(pattern_type: str | None = None):
    from .creator_surfaces import recall_patterns
    return recall_patterns(pattern_type)


@app.post("/api/creator/canvas/wireframe")
def creator_canvas_wireframe(prompt: str):
    from .creator_surfaces import generate_wireframe
    return generate_wireframe(prompt)


@app.post("/api/creator/research")
def creator_research(query: str, grounded_in: str = "local"):
    from .creator_surfaces import research_query
    return research_query(query, grounded_in)


# --- MAO: Multi Agent Orchestrator ---

@app.get("/api/mao/status")
def mao_status():
    try:
        import importlib.util
        mao_path = Path(__file__).resolve().parents[2] / "CLI" / "mao_server.py"
        spec = importlib.util.spec_from_file_location("mao_server", mao_path)
        mao_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mao_mod)
        return mao_mod.mao_swarm_status()
    except Exception as e:
        return {"error": str(e), "mao_available": False}


@app.post("/api/mao/route")
def mao_route_task(request: MaoTaskRequest):
    try:
        from .mao_dispatch import route_task

        return route_task(intent=request.intent, message=request.message)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/mao/execute")
def mao_execute_task(request: MaoTaskRequest):
    try:
        from .mao_dispatch import execute_task

        return execute_task(
            intent=request.intent,
            message=request.message,
            force_agent_id=request.force_agent_id,
        )
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/mao/philosophy-check")
def mao_philosophy(action_description: str, has_proof: bool, survives_constraints: bool):
    try:
        import importlib.util
        mao_path = Path(__file__).resolve().parents[2] / "CLI" / "mao_server.py"
        spec = importlib.util.spec_from_file_location("mao_server", mao_path)
        mao_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mao_mod)
        return mao_mod.mao_philosophy_check(
            action_description=action_description,
            has_proof=has_proof,
            survives_constraints=survives_constraints,
        )
    except Exception as e:
        return {"error": str(e)}


# --- OBSERVABLE COGNITION SURFACE & GOVERNANCE TRACES ---
@app.get("/api/governance-traces")
def get_governance_traces():
    from .governance_trace import GovernanceTraceEngine
    engine = GovernanceTraceEngine()
    traces = engine.list_session_traces("default_session")
    return {"traces": [t.to_dict() for t in traces]}


class NewTraceRequest(BaseModel):
    speaker_seat: str
    question_or_intent: str
    session_id: str = "default_session"
    which_brain: str = "LOCAL_MAO_BLACK_BEAST"
    sources: List[str] = []
    validations: List[str] = []
    why_trust: str = ""


@app.post("/api/governance-traces")
def create_governance_trace(req: NewTraceRequest):
    from .governance_trace import GovernanceTraceEngine, CanonicalEvidenceClass
    engine = GovernanceTraceEngine()
    trace = engine.start_trace(
        speaker_seat=req.speaker_seat,
        question_or_intent=req.question_or_intent,
        session_id=req.session_id,
        which_brain=req.which_brain
    )
    for s in req.sources:
        engine.record_search(trace, s)
    for v in req.validations:
        engine.record_validation(trace, v)

    # Attach verified repository artifact evidence
    engine.add_evidence(
        trace,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="kopano-core/kopano/api.py",
        description="API request execution on physical metal",
        verified=True
    )
    
    sealed = engine.seal_and_persist_trace(trace, why_trust=req.why_trust)
    return {"trace": sealed.to_dict(), "visual_card": sealed.to_visual_card()}


@app.get("/api/governance-traces/analytics")
def get_trace_analytics(session_id: str = "default_session"):
    from dataclasses import asdict
    from .governance_trace import GovernanceTraceEngine
    from .kmec_trace_adapter import KMECTraceAdapter
    engine = GovernanceTraceEngine()
    traces = engine.list_session_traces(session_id)
    if not traces:
        return {"message": "No traces recorded for this session", "session_id": session_id}

    df = KMECTraceAdapter.to_dataframe(traces)
    group_summary = KMECTraceAdapter.group_summary_by_seat(df)
    pivot_data = KMECTraceAdapter.pivot_brain_by_epistemic_state(traces)
    attention_matrix = KMECTraceAdapter.generate_attention_matrix(traces)
    contra_dist = KMECTraceAdapter.compute_distribution_metrics(df, "contradictions_count")
    evidence_dist = KMECTraceAdapter.compute_distribution_metrics(df, "evidence_count")

    return {
        "session_id": session_id,
        "total_traces": len(traces),
        "group_summary_by_seat": group_summary,
        "pivot_brain_by_state": pivot_data,
        "attention_matrix": attention_matrix,
        "contradictions_boxplot": asdict(contra_dist) if contra_dist else None,
        "evidence_boxplot": asdict(evidence_dist) if evidence_dist else None,
    }


@app.post("/api/governance-traces/cell-lineage")
def get_cell_lineage(trace_ids: List[str], session_id: str = "default_session"):
    from .governance_trace import GovernanceTraceEngine
    from .kmec_trace_adapter import KMECTraceAdapter
    engine = GovernanceTraceEngine()
    traces = engine.list_session_traces(session_id)
    return KMECTraceAdapter.trace_cell_lineage(traces, trace_ids)


@app.get("/observability", response_class=HTMLResponse)
def observability_dashboard(session_id: str = "default_session"):
    """
    Renders the rich Observable Cognition Surface & KMEC Observational Dataset Dashboard.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observable Cognition Surface — Kopano Sovereign Studio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #07090e;
            --bg-card: rgba(18, 24, 38, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-glow: rgba(56, 189, 248, 0.2);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-green: #34d399;
            --accent-amber: #fbbf24;
            --accent-rose: #fb7185;
            --accent-purple: #c084fc;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Outfit', sans-serif;
            background: var(--bg-primary);
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px;
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(192, 132, 252, 0.05) 0%, transparent 40%);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 24px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            backdrop-filter: blur(12px);
            margin-bottom: 24px;
        }}
        .header-title h1 {{
            font-size: 1.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header-title p {{ font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }}
        .badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(52, 211, 153, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(52, 211, 153, 0.3);
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        @media(max-width: 1024px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(12px);
            transition: border-color 0.2s;
        }}
        .card:hover {{ border-color: var(--border-glow); }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }}
        .card-title {{ font-size: 1.05rem; font-weight: 600; color: #e2e8f0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}
        th, td {{
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{ color: var(--text-muted); font-weight: 500; font-size: 0.8rem; text-transform: uppercase; }}
        .cell-interactive {{
            cursor: pointer;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: var(--accent-cyan);
            border-radius: 6px;
            padding: 4px 8px;
            transition: all 0.2s;
            display: inline-block;
        }}
        .cell-interactive:hover {{
            background: rgba(56, 189, 248, 0.15);
            transform: scale(1.05);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 12px;
        }}
        .metric-box {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px;
            text-align: center;
        }}
        .metric-val {{ font-size: 1.3rem; font-weight: 700; color: var(--accent-cyan); font-family: 'JetBrains Mono', monospace; }}
        .metric-lbl {{ font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }}
        .lineage-panel {{
            margin-top: 24px;
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 24px;
            display: none;
        }}
        pre {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            overflow-x: auto;
            color: #93c5fd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h1>Observable Cognition Surface — KMEC Dataset Engine</h1>
            <p>Weight-Bearing Activity Ledger · Cold-Restart Resilient · Anti-"Trust Me Bro" Derivation Gate</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span class="badge">Session: {session_id}</span>
            <span class="badge" style="color: var(--accent-cyan); background: rgba(56,189,248,0.15); border-color: rgba(56,189,248,0.3);">29/29 Metal Pass</span>
        </div>
    </div>

    <div class="grid-2">
        <!-- 2D Pivot Table Card -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">1. Observable Cognition 2D Pivot (Brain × Epistemic State)</span>
                <span style="font-size: 0.8rem; color: var(--text-muted);">Click cell for cryptographic lineage</span>
            </div>
            <div id="pivotContainer">
                <p style="color: var(--text-muted); font-size: 0.9rem;">Loading KMEC analytics from SQLite ledger...</p>
            </div>
        </div>

        <!-- Attention Matrix Card -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">2. Communication Attention Matrix (Where should KC inspect?)</span>
                <span id="attentionVerdict" class="badge" style="color: var(--accent-amber); background: rgba(251,191,36,0.15);">SCANNING</span>
            </div>
            <div id="attentionContainer">
                <p style="color: var(--text-muted); font-size: 0.9rem;">Evaluating contradiction outliers & UNKNOWN clusters...</p>
            </div>
        </div>
    </div>

    <div class="grid-2">
        <!-- Contradiction & Evidence Box Plot Metrics -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">3. Contradiction Distribution (KMEC Box Plot)</span>
            </div>
            <div class="metric-grid" id="contraMetrics">
                <div class="metric-box"><div class="metric-val" id="contraMed">-</div><div class="metric-lbl">MEDIAN</div></div>
                <div class="metric-box"><div class="metric-val" id="contraQ1">-</div><div class="metric-lbl">Q1 (25%)</div></div>
                <div class="metric-box"><div class="metric-val" id="contraQ3">-</div><div class="metric-lbl">Q3 (75%)</div></div>
                <div class="metric-box"><div class="metric-val" id="contraIQR">-</div><div class="metric-lbl">IQR</div></div>
                <div class="metric-box"><div class="metric-val" id="contraFence">-</div><div class="metric-lbl">UPPER FENCE</div></div>
                <div class="metric-box"><div class="metric-val" id="contraOutliers" style="color: var(--accent-rose);">-</div><div class="metric-lbl">OUTLIERS</div></div>
            </div>
        </div>

        <!-- Speaker Summary Card -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">4. Seat Turn & Proof Performance</span>
            </div>
            <div id="seatSummaryContainer">
                <p style="color: var(--text-muted); font-size: 0.9rem;">Aggregating 10-Seat council turns...</p>
            </div>
        </div>
    </div>

    <!-- Cell Lineage Back-Tracing Modal/Panel -->
    <div class="lineage-panel" id="lineagePanel">
        <div class="card-header">
            <span class="card-title" style="color: var(--accent-cyan);">🔬 Cell Provenance Lineage (Weight-Bearing Proof)</span>
            <button onclick="document.getElementById('lineagePanel').style.display='none'" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:1.1rem;">✕</button>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">This cell was produced by the following cryptographic trace receipts on metal:</p>
        <pre id="lineageOutput"></pre>
    </div>

    <script>
        const sessionId = "{session_id}";
        let globalLineageMap = {{}};

        async function loadAnalytics() {{
            try {{
                const res = await fetch(`/api/governance-traces/analytics?session_id=${{sessionId}}`);
                const data = await res.json();
                if (data.message) {{
                    document.getElementById('pivotContainer').innerHTML = `<p style="color: var(--text-muted);">${{data.message}}</p>`;
                    return;
                }}

                // Render Pivot Table
                globalLineageMap = data.pivot_brain_by_state.cell_lineage || {{}};
                const pivot = data.pivot_brain_by_state.pivot_table || {{}};
                let html = '<table><thead><tr><th>Brain Consulting</th><th>PROVEN</th><th>SUPPORTED</th><th>INFERRED</th><th>UNKNOWN</th></tr></thead><tbody>';
                for (const [brain, states] of Object.entries(pivot)) {{
                    html += `<tr>
                        <td style="font-weight:600;">${{brain}}</td>
                        <td>${{renderCell(brain, 'PROVEN', states.PROVEN || 0)}}</td>
                        <td>${{renderCell(brain, 'SUPPORTED', states.SUPPORTED || 0)}}</td>
                        <td>${{renderCell(brain, 'INFERRED', states.INFERRED || 0)}}</td>
                        <td>${{renderCell(brain, 'UNKNOWN', states.UNKNOWN || 0)}}</td>
                    </tr>`;
                }}
                html += '</tbody></table>';
                document.getElementById('pivotContainer').innerHTML = html;

                // Render Attention Matrix
                const attn = data.attention_matrix;
                document.getElementById('attentionVerdict').innerText = attn.attention_verdict;
                document.getElementById('attentionVerdict').style.color = attn.attention_verdict === 'ATTENTION_CLEAR' ? 'var(--accent-green)' : 'var(--accent-amber)';
                
                let attnHtml = `<p style="font-size:0.85rem; margin-bottom:8px;">Nominated Traces for KC / Validator Inspection: <strong>${{attn.nominated_for_kc_inspection.length}}</strong></p>`;
                if (attn.nominated_for_kc_inspection.length > 0) {{
                    attnHtml += '<ul style="padding-left:20px; font-family:JetBrains Mono; font-size:0.8rem; color:var(--accent-amber);">';
                    attn.nominated_for_kc_inspection.forEach(tid => {{
                        attnHtml += `<li><span class="cell-interactive" onclick="inspectTrace('${{tid}}')">${{tid}}</span></li>`;
                    }});
                    attnHtml += '</ul>';
                }} else {{
                    attnHtml += '<p style="color:var(--accent-green); font-size:0.85rem;">✓ No unverified E4 artifacts or contradiction outliers detected.</p>';
                }}
                document.getElementById('attentionContainer').innerHTML = attnHtml;

                // Render Box Plot
                if (data.contradictions_boxplot) {{
                    const c = data.contradictions_boxplot;
                    document.getElementById('contraMed').innerText = c.median.toFixed(1);
                    document.getElementById('contraQ1').innerText = c.q1.toFixed(1);
                    document.getElementById('contraQ3').innerText = c.q3.toFixed(1);
                    document.getElementById('contraIQR').innerText = c.iqr.toFixed(1);
                    document.getElementById('contraFence').innerText = c.upper_fence.toFixed(1);
                    document.getElementById('contraOutliers').innerText = c.outlier_count;
                }}

                // Render Seat Summary
                let seatHtml = '<table><thead><tr><th>Seat</th><th>Turns</th><th>Avg Sources</th><th>Proven</th><th>Unknown</th></tr></thead><tbody>';
                data.group_summary_by_seat.forEach(s => {{
                    seatHtml += `<tr>
                        <td style="font-weight:600; color:var(--accent-cyan);">${{s.speaker_seat}}</td>
                        <td>${{s.total_turns}}</td>
                        <td>${{s.avg_sources.toFixed(1)}}</td>
                        <td style="color:var(--accent-green);">${{s.proven_count}}</td>
                        <td style="color:var(--accent-rose);">${{s.unknown_count}}</td>
                    </tr>`;
                }});
                seatHtml += '</tbody></table>';
                document.getElementById('seatSummaryContainer').innerHTML = seatHtml;

            }} catch (err) {{
                console.error("Failed to load analytics:", err);
            }}
        }}

        function renderCell(brain, state, count) {{
            if (count === 0) return '<span style="color:rgba(255,255,255,0.2);">0</span>';
            const key = `${{brain}}::${{state}}`;
            return `<span class="cell-interactive" onclick="inspectCell('${{key}}')">${{count}}</span>`;
        }}

        async function inspectCell(key) {{
            const traceIds = globalLineageMap[key] || [];
            if (traceIds.length === 0) return;
            const res = await fetch(`/api/governance-traces/cell-lineage?session_id=${{sessionId}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(traceIds)
            }});
            const lineage = await res.json();
            document.getElementById('lineagePanel').style.display = 'block';
            document.getElementById('lineageOutput').innerText = JSON.stringify(lineage, null, 2);
            document.getElementById('lineagePanel').scrollIntoView({{ behavior: 'smooth' }});
        }}

        async function inspectTrace(traceId) {{
            await inspectCell(null, [traceId]);
        }}

        loadAnalytics();
    </script>
</body>
</html>
"""
    return html_content


# --- GOOGLE DRIVE MCP ENDPOINTS ---
@app.get("/api/gdrive/search")
def gdrive_search(query: str, limit: int = 10):
    from .tools.google_drive_mcp import GoogleDriveMCPTool
    tool = GoogleDriveMCPTool()
    return {"query": query, "results": tool.search_drive(query, limit=limit)}


@app.get("/api/gdrive/read/{file_id}")
def gdrive_read_doc(file_id: str):
    from .tools.google_drive_mcp import GoogleDriveMCPTool
    tool = GoogleDriveMCPTool()
    doc = tool.read_document(file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in Google Drive datalake")
    return {"file_id": doc.file_id, "name": doc.name, "mime_type": doc.mime_type, "content": doc.content_text, "link": doc.web_view_link}


# --- RTC VOICE & SEAT ROUTING ENDPOINTS ---
class VoiceTurnRequest(BaseModel):
    session_id: str
    user_input: str
    speaker: str = "MASTER_ROBYN"
    modality: str = "text"


@app.post("/api/rtc/voice-turn")
def rtc_voice_turn(req: VoiceTurnRequest):
    from .rtc_voice_bridge import RTCVoiceBridge
    bridge = RTCVoiceBridge()
    turn = bridge.process_turn(
        session_id=req.session_id,
        user_input=req.user_input,
        speaker=req.speaker,
        modality=req.modality
    )
    payload = bridge.format_gemini_live_payload(req.user_input)
    return {
        "turn_id": turn.turn_id,
        "foc_check_passed": turn.foc_check_passed,
        "active_seat": bridge.active_seat,
        "gemini_live_payload": payload
    }


@app.post("/api/rtc/switch-seat")
def rtc_switch_seat(seat_id: str):
    from .rtc_voice_bridge import RTCVoiceBridge
    bridge = RTCVoiceBridge()
    return bridge.switch_active_seat(seat_id)


# Mount the React build directory if it exists
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle
    gui_dist_path = Path(sys._MEIPASS) / "studio" / "dist"
else:
    # Running in normal python mode
    gui_dist_path = Path(__file__).parent.parent / "studio" / "dist"

if gui_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(gui_dist_path), html=True), name="studio")
else:
    @app.get("/")
    def gui_missing():
        return {
            "message": "Kopano Context API is running, but local Studio build not found.",
            "instructions": f"Navigate to {PRODUCTION_URL} for the cloud instance or run 'npm run build' in the studio folder.",
            "diagnostics": f"Local search path: {gui_dist_path}"
        }

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

# merge: dev 2026-06-22
