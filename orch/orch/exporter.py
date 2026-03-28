import json
from pathlib import Path
from .database import SessionLocal, Session, Message

def export_session_to_jsonl(session_id: int, output_dir: Path):
    """Export a specific discussion session to JSONL for fine-tuning."""
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return None
            
        output_file = output_dir / f"session_{session_id}_dataset.jsonl"
        with open(output_file, "w") as f:
            for msg in session.messages:
                # Basic fine-tuning format (System prompt + turn-based conversation)
                entry = {
                    "role": "assistant" if msg.agent_id != "user" else "user",
                    "content": f"[{msg.agent_id.upper()}]: {msg.content}",
                    "metadata": {
                        "round": msg.round_num,
                        "session_id": session_id,
                        "agent": msg.agent_id
                    }
                }
                f.write(json.dumps(entry) + "\n")
        
        return output_file
    finally:
        db.close()

def export_all_to_jsonl(output_dir: Path):
    """Combine all high-quality sessions into a single dataset."""
    db = SessionLocal()
    try:
        sessions = db.query(Session).all()
        dataset_file = output_dir / "orch_full_master_dataset.jsonl"
        
        with open(dataset_file, "w") as f:
            for session in sessions:
                # We group by session for multi-turn training files
                conversation = []
                for msg in session.messages:
                     conversation.append({
                        "role": "user" if msg.agent_id == "user" else "assistant",
                        "content": msg.content
                    })
                
                f.write(json.dumps({"messages": conversation}) + "\n")
        
        return dataset_file
    finally:
        db.close()
