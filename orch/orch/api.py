from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, Session as DbSession, Message
from typing import List
import uvicorn
import asyncio
import json

app = FastAPI(title="orch AGI Command Center API")

# Add CORS for the React GUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active connections for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def shadow_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.shadow_connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Wait for signals
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/broadcast")
async def broadcast_message(data: dict):
    """Internal endpoint for simulator to push updates to the UI."""
    await manager.broadcast(json.dumps(data))
    return {"status": "broadcasted"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    """List all AGI Council Sessions."""
    sessions = db.query(DbSession).order_by(DbSession.created_at.desc()).all()
    return [{
        "id": s.id,
        "topic": s.topic,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "agents": s.agents.split(",") if s.agents else []
    } for s in sessions]

@app.get("/sessions/{session_id}")
def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    """Get the full transcript and deep reasoning for a specific session."""
    session = db.query(DbSession).filter(DbSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.id).all()
    return {
        "id": session.id,
        "topic": session.topic,
        "agents": session.agents.split(",") if session.agents else [],
        "messages": [{
            "round": m.round_num,
            "agent": m.agent_id,
            "content": m.content,
            "reasoning": m.reasoning,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None
        } for m in messages]
    }

@app.get("/live")
def get_live_session(db: Session = Depends(get_db)):
    """Get the latest activity in the Data Lake."""
    latest_session = db.query(DbSession).order_by(DbSession.created_at.desc()).first()
    if not latest_session:
        return {"status": "idle"}
    return get_session_detail(latest_session.id, db)

def start_api():
    print("🚀 Starting AGI Command Center API at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
