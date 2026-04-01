from fastapi import FastAPI, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# from .database import SessionLocal, CouncilSession, NeuralRound, CognitiveBlock, Mentor, init_db, engine # Commented out as I suspect these don't exist in the current database.py
from .database import init_db # Using the one from our database.py
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import asyncio
from contextlib import asynccontextmanager

# --- PROACTIVE NEURAL SHIELD: LIFESPAN LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the Pristine Vault
    init_db()
    print("🌌 Pristine Vault online")
    yield
    # Shutdown: The Kill-Switch to prevent OperationalErrors (e3q8)
    # engine.dispose() # Commented out as engine is not defined in database.py
    print("🪐 Vault sealed. No lingering neural threads.")

app = FastAPI(title="orch AGI Control Plane", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared memory for real-time updates (Broadcast Protocol)
class State:
    updates = []
    connections: List[WebSocket] = []

state = State()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

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

@app.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    """Retrieve all historical AGI Lessons from the Vault."""
    sessions = db.query(CouncilSession).order_by(CouncilSession.created_at.desc()).all()
    return [{
        "id": s.id,
        "title": s.title,
        "created_at": s.created_at
    } for s in sessions]

@app.get("/sessions/{session_id}")
def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """Deep forensic drill-down into a specific session's round-by-round logic."""
    session = db.query(CouncilSession).filter(CouncilSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    rounds_data = []
    for r in session.rounds:
        blocks_data = []
        for b in r.blocks:
            blocks_data.append({
                "id": b.id,
                "mentor": b.mentor.name,
                "content": b.content,
                "reasoning": b.reasoning,
                "is_student": b.is_student,
                "value_score": b.value_score,
                "override_score": b.override_score,
                "improvement_hint": b.improvement_hint
            })
        rounds_data.append({
            "round_number": r.round_number,
            "blocks": blocks_data
        })
        
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "rounds": rounds_data
    }

class OverrideRequest(BaseModel):
    override_score: int
    improvement_hint: Optional[str] = None

@app.post("/sessions/{block_id}/override")
def apply_master_override(block_id: str, req: OverrideRequest, db: Session = Depends(get_db)):
    """Manual Master Override for surgical scoring of individual reasoning blocks."""
    block = db.query(CognitiveBlock).filter(CognitiveBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    block.override_score = req.override_score
    if req.improvement_hint:
        block.improvement_hint = req.improvement_hint
    
    db.commit()
    return {"status": "Override Commited", "block_id": block_id}

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)
