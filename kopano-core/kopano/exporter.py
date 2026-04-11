import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .database import get_db_connection

def export_session_to_jsonl(session_id: int, output_dir: Path, format: str = "chatml") -> Optional[Path]:
    """
    Export a specific discussion session to JSONL for fine-tuning.
    Formats: 'chatml', 'alpaca', 'raw'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get discussion topic
        cursor.execute("SELECT topic FROM discussions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        topic = row["topic"]

        # Get messages
        cursor.execute("""
            SELECT round_num, agent_id, agent_model, prompt, response, is_moderator_direction 
            FROM messages 
            WHERE discussion_id = ? 
            ORDER BY round_num ASC, timestamp ASC
        """, (session_id,))
        messages = cursor.fetchall()

        if not messages:
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"session_{session_id}_{format}_dataset.jsonl"
        output_file = output_dir / filename
        
        with open(output_file, "w", encoding="utf-8") as f:
            if format == "chatml":
                # ChatML format: {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]}
                conversation = [{"role": "system", "content": f"Topic: {topic}"}]
                for msg in messages:
                    # User-like message (prompt) followed by agent response
                    if msg["prompt"]:
                        conversation.append({"role": "user", "content": msg["prompt"]})
                    conversation.append({"role": "assistant", "content": f"[{msg['agent_id']} ({msg['agent_model']})]: {msg['response']}"})
                
                f.write(json.dumps({"messages": conversation}) + "\n")
            
            elif format == "alpaca":
                # Alpaca format: {"instruction": "...", "input": "...", "output": "..."}
                for msg in messages:
                    entry = {
                        "instruction": f"In a discussion about {topic}, what did {msg['agent_id']} say?",
                        "input": msg["prompt"] or "",
                        "output": msg["response"]
                    }
                    f.write(json.dumps(entry) + "\n")
            
            else: # raw or default
                for msg in messages:
                    entry = {
                        "round": msg["round_num"],
                        "agent": msg["agent_id"],
                        "model": msg["agent_model"],
                        "prompt": msg["prompt"],
                        "response": msg["response"],
                        "is_moderator": bool(msg["is_moderator_direction"])
                    }
                    f.write(json.dumps(entry) + "\n")

        return output_file
    finally:
        conn.close()

def export_all_to_jsonl(output_dir: Path, format: str = "chatml") -> Path:
    """
    Combine all high-quality sessions into a single dataset.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM discussions")
        session_ids = [row["id"] for row in cursor.fetchall()]
        
        output_dir.mkdir(parents=True, exist_ok=True)
        dataset_file = output_dir / f"orch_full_master_{format}_dataset.jsonl"
        
        with open(dataset_file, "w", encoding="utf-8") as f_out:
            for sid in session_ids:
                temp_file = export_session_to_jsonl(sid, output_dir, format=format)
                if temp_file and temp_file.exists():
                    with open(temp_file, "r", encoding="utf-8") as f_in:
                        f_out.write(f_in.read())
                    # temp_file.unlink() # Optionally delete temporary files
        
        return dataset_file
    finally:
        conn.close()
