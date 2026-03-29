from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, Session as DbSession, Round, ReasoningBlock, Teacher, init_db
from typing import List
import uvicorn
import asyncio
import json

app = FastAPI(title="orch AGI Command Center API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
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
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/broadcast")
async def broadcast_message(data: dict):
    await manager.broadcast(json.dumps(data))
    return {"status": "broadcasted"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    """List all AGI Lessons."""
    sessions = db.query(DbSession).order_by(DbSession.created_at.desc()).all()
    return [{
        "id": s.id,
        "topic": s.title,
        "created_at": s.created_at.isoformat()
    } for s in sessions]

@app.get("/sessions/{session_id}")
def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """Return a deep hierarchical JSON of the session."""
    session = db.query(DbSession).filter(DbSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    rounds = db.query(Round).filter(Round.session_id == session_id).order_by(Round.round_number).all()
    
    result = {
        "id": session.id,
        "topic": session.title,
        "created_at": session.created_at.isoformat(),
        "rounds": []
    }
    
    for r in rounds:
        round_data = {
            "id": r.id,
            "round_number": r.round_number,
            "blocks": []
        }
        blocks = db.query(ReasoningBlock).filter(ReasoningBlock.round_id == r.id).order_by(ReasoningBlock.created_at).all()
        for b in blocks:
            teacher = db.query(Teacher).filter(Teacher.id == b.teacher_id).first()
            round_data["blocks"].append({
                "block_id": b.id,
                "agent": teacher.name if teacher else "Unknown",
                "role": teacher.role if teacher else "None",
                "content": b.content,
                "reasoning": b.reasoning,
                "value_score": b.value_score,
                "override_score": b.override_score,
                "improvement_hint": b.improvement_hint,
                "is_student": b.is_student
            })
        result["rounds"].append(round_data)
        
    return result

@app.post("/sessions/{session_id}/override")
async def override_score(session_id: str, data: dict, db: Session = Depends(get_db)):
    """Forensic Master Override for a specific reasoning block."""
    block_id = data.get("block_id")
    block = db.query(ReasoningBlock).filter(ReasoningBlock.id == block_id).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
        
    if "override_score" in data:
        block.override_score = data["override_score"]
    if "improvement_hint" in data:
        block.improvement_hint = data["improvement_hint"]
        
    db.commit()
    
    # Broadcast to live UI
    await manager.broadcast(json.dumps({
        "type": "override",
        "block_id": block_id,
        "override_score": block.override_score,
        "improvement_hint": block.improvement_hint
    }))
    
    return {"status": "success"}

def start_api():
    init_db()
    print("🚀 AGI Audit API Online at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
