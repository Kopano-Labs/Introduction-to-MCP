"""
Phase 2: Data Lake & Strategy Engine
This module handles the structured logging of all discussions to a local SQLite database.
It provides the schema and functions for creating, connecting to, and writing to the database.

Connect with the Architect:
- LinkedIn: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
- GitHub: https://github.com/RobynAwesome/
"""
import sqlite3
import hashlib
import secrets
from pathlib import Path
from typing import Optional
from rich.console import Console

from .config import settings

console = Console()

# Define the path for the SQLite database
DB_PATH = Path(settings.db_path)

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
        round_num INTEGER,
        model TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        message TEXT,
        prompt TEXT,
        log_type TEXT CHECK(log_type IN ('reasoning', 'execution', 'tool_call', 'tool_result', 'system', 'security_alert', 'execution_correction')) NOT NULL,
        value_score INTEGER DEFAULT 0,
        override_score INTEGER,
        improvement_hint TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(discussion_id) REFERENCES discussions(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cowork_rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mission TEXT NOT NULL,
        lead TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cowork_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        owner TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        priority TEXT NOT NULL DEFAULT 'high',
        lane TEXT NOT NULL DEFAULT 'build',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES cowork_rooms (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orch_code_lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_key TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        track TEXT NOT NULL,
        source TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        confidence INTEGER NOT NULL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cowork_artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        artifact_type TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES cowork_rooms (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mcp_console_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        surface TEXT NOT NULL DEFAULT 'orch_labs',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mcp_console_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        topic TEXT,
        content TEXT NOT NULL,
        latency_ms INTEGER NOT NULL DEFAULT 0,
        model_used TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES mcp_console_sessions (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS creator_analytics_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        room_id INTEGER,
        task_id INTEGER,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES cowork_rooms (id),
        FOREIGN KEY (task_id) REFERENCES cowork_tasks (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        god_mode INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    console.log("Database schema initialized successfully.")


def setup_database():
    """Wrapper for init_db for external calls."""
    init_db()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def register_user(email: str, password: str, full_name: Optional[str] = None) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    normalized_email = email.strip().lower()

    cursor.execute("SELECT id FROM users WHERE email = ?", (normalized_email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("A user with this email already exists.")

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    cursor.execute(
        """
        INSERT INTO users (email, full_name, password_hash, password_salt)
        VALUES (?, ?, ?, ?)
        """,
        (normalized_email, full_name, password_hash, salt),
    )
    conn.commit()
    cursor.execute(
        "SELECT id, email, full_name, role, god_mode, is_active, created_at FROM users WHERE email = ?",
        (normalized_email,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def authenticate_user(email: str, password: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    normalized_email = email.strip().lower()
    cursor.execute(
        """
        SELECT id, email, full_name, password_hash, password_salt, role, god_mode, is_active, created_at
        FROM users
        WHERE email = ?
        """,
        (normalized_email,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    if not row["is_active"]:
        return None

    expected = _hash_password(password, row["password_salt"])
    if expected != row["password_hash"]:
        return None

    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "god_mode": bool(row["god_mode"]),
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


def grant_admin(email: str, god_mode: bool = False) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    normalized_email = email.strip().lower()
    cursor.execute(
        """
        UPDATE users
        SET role = 'admin',
            god_mode = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE email = ?
        """,
        (1 if god_mode else 0, normalized_email),
    )
    if cursor.rowcount == 0:
        conn.close()
        raise ValueError("User not found.")
    conn.commit()
    cursor.execute(
        "SELECT id, email, full_name, role, god_mode, is_active, created_at FROM users WHERE email = ?",
        (normalized_email,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def record_creator_event(
    event_type: str,
    room_id: int | None = None,
    task_id: int | None = None,
    metadata: str | None = None,
) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO creator_analytics_events (event_type, room_id, task_id, metadata)
        VALUES (?, ?, ?, ?)
        """,
        (event_type, room_id, task_id, metadata),
    )
    conn.commit()
    conn.close()

def log_interaction(
    discussion_id: int, 
    model: str, 
    agent_id: str, 
    message: Optional[str], 
    prompt: Optional[str], 
    log_type: str,
    round_num: Optional[int] = None,
    value_score: int = 0
):
    """
    Inserts a structured log into the audit_logs table.
    log_type: 'reasoning', 'execution', 'tool_call', 'tool_result', 'system', 'security_alert', 'execution_correction'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (discussion_id, round_num, model, agent_id, message, prompt, log_type, value_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (discussion_id, round_num, model, agent_id, message, prompt, log_type, value_score))
    conn.commit()
    conn.close()

def update_log_override(log_id: int, override_score: int, improvement_hint: Optional[str] = None):
    """Updates the override score and hint for a specific log entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE audit_logs 
        SET override_score = ?, improvement_hint = ?
        WHERE id = ?
    """, (override_score, improvement_hint, log_id))
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
