"""
Phase 2: Data Lake Interface
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "db" / "datalake.db"

def get_connection() -> sqlite3.Connection:
    """Establishes and returns a connection to the SQLite Data Lake."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db(schema_path: str):
    """Initializes the database using the provided schema.sql file."""
    conn = get_connection()
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def start_discussion(topic: str) -> int:
    """Creates a new discussion record and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO discussions (topic) VALUES (?)", (topic,))
    discussion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return discussion_id

def log_interaction(
    discussion_id: int, 
    model: str, 
    agent_id: str, 
    message: Optional[str], 
    prompt: Optional[str], 
    log_type: str
):
    """Inserts a structured log into the audit_logs table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (discussion_id, model, agent_id, message, prompt, log_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (discussion_id, model, agent_id, message, prompt, log_type))
    conn.commit()
    conn.close()