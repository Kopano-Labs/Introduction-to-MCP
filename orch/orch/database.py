"""
Phase 2: Data Lake & Strategy Engine
This module handles the structured logging of all discussions to a local SQLite database.
It provides the schema and functions for creating, connecting to, and writing to the database.

Connect with the Architect:
- LinkedIn: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
- GitHub: https://github.com/RobynAwesome/
"""
import sqlite3
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()

# Define the path for the SQLite database
DB_PATH = Path.home() / ".orch" / "orch_datastore.db"

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database and creates the necessary tables if they don't exist.
    This function defines the core schema for the Data Lake.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for discussion sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table for individual messages within a discussion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discussion_id INTEGER NOT NULL,
        round_num INTEGER NOT NULL,
        agent_id TEXT NOT NULL,
        agent_model TEXT NOT NULL,
        prompt TEXT,
        response TEXT NOT NULL,
        is_moderator_direction INTEGER NOT NULL DEFAULT 0, -- Boolean (0 or 1)
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (discussion_id) REFERENCES discussions (id)
    );
    """)

    # Table for audit logs (Separating reasoning from execution)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discussion_id INTEGER,
        model TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        message TEXT,
        prompt TEXT,
        log_type TEXT CHECK(log_type IN ('reasoning', 'execution', 'tool_call', 'tool_result', 'system')) NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(discussion_id) REFERENCES discussions(id)
    );
    """)

    conn.commit()
    conn.close()
    console.log("🗄️  Database schema initialized successfully.")


def setup_database():
    """Wrapper for init_db for external calls."""
    init_db()

def log_interaction(
    discussion_id: int, 
    model: str, 
    agent_id: str, 
    message: Optional[str], 
    prompt: Optional[str], 
    log_type: str
):
    """
    Inserts a structured log into the audit_logs table.
    log_type: 'reasoning', 'execution', 'tool_call', 'tool_result', 'system'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (discussion_id, model, agent_id, message, prompt, log_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (discussion_id, model, agent_id, message, prompt, log_type))
    conn.commit()
    conn.close()

def log_message(
    discussion_id: int,
    round_num: int,
    agent_id: str,
    agent_model: str,
    prompt: Optional[str],
    response: str,
    is_moderator_direction: int = 0
):
    """
    Inserts a message into the messages table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction))
    conn.commit()
    conn.close()

# Initialize the database on module load to ensure tables are ready.
# In a larger application, this might be called from a specific startup script.
try:
    init_db()
except Exception as e:
    console.print(f"[bold red]Error initializing database:[/] {e}")