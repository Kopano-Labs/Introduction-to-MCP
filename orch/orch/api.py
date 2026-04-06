"""
orch AGI Control Plane API
Author Links:
- LinkedIn: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
- GitHub: https://github.com/RobynAwesome/
"""

from fastapi import FastAPI, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db, get_db_connection, register_user, authenticate_user
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager
from .kasilink_api import router as kasilink_router
from .labs_api import router as labs_router

# --- PROACTIVE NEURAL SHIELD: LIFESPAN LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the Pristine Vault
    init_db()
    print("Pristine Vault online")
    yield
    print("Vault sealed. No lingering neural threads.")

app = FastAPI(title="orch AGI Control Plane", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://kasi-link.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kasilink_router)
app.include_router(labs_router)

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
    """Register a local Orch user account."""
    try:
        user = register_user(request.email, request.password, request.full_name)
        return {"status": "ok", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate a local Orch user account."""
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "ok", "user": user}

@app.get("/sessions")
def list_sessions():
    """Retrieve all historical AGI Lessons from the Vault."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, start_time as created_at FROM discussions ORDER BY start_time DESC")
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
            "is_student": 1 if log["agent_id"] == "orch" else 0
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
        state.updates.append(update)
        for connection in state.connections:
            try:
                await connection.send_json(update)
            except:
                pass
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- STATIC FILE SERVING (GUI) ---
# Mount the React build directory if it exists
gui_dist_path = Path(__file__).parent.parent / "gui" / "dist"
if gui_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(gui_dist_path), html=True), name="gui")
else:
    @app.get("/")
    def gui_missing():
        return {
            "message": "Orch API is running, but GUI build not found.",
            "instructions": "Run 'cd orch/gui && npm install && npm run build' to enable the browser interface."
        }

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
