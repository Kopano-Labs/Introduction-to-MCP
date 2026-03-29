import json
from pathlib import Path
from .database import SessionLocal, CouncilSession, NeuralRound, CognitiveBlock, Mentor

def export_session_to_jsonl(session_id: str, output_dir: Path):
    """Export a specific discussion session to JSONL for fine-tuning."""
    db = SessionLocal()
    try:
        session = db.query(CouncilSession).filter(CouncilSession.id == session_id).first()
        if not session:
            return None
            
        output_file = output_dir / f"session_{session_id}_dataset.jsonl"
        with open(output_file, "w") as f:
            for rnd in session.rounds:
                for block in rnd.blocks:
                    mentor = db.query(Mentor).filter(Mentor.id == block.mentor_id).first()
                    entry = {
                        "role": "assistant" if not block.is_student else "user",
                        "content": f"[{mentor.name.upper()}]: {block.content}",
                        "metadata": {
                            "round": rnd.round_number,
                            "session_id": session_id,
                            "agent": mentor.name,
                            "reasoning": block.reasoning
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
        sessions = db.query(CouncilSession).all()
        dataset_file = output_dir / "orch_full_master_dataset.jsonl"
        
        with open(dataset_file, "w") as f:
            for session in sessions:
                conversation = []
                for rnd in session.rounds:
                    for block in rnd.blocks:
                        mentor = db.query(Mentor).filter(Mentor.id == block.mentor_id).first()
                        conversation.append({
                            "role": "user" if block.is_student else "assistant",
                            "content": block.content
                        })
                
                f.write(json.dumps({"messages": conversation}) + "\n")
        
        return dataset_file
    finally:
        db.close()
