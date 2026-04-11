import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from rich.console import Console
from .config import settings

console = Console()

class MemoryManager:
    """
    Handles long-term memory for agents using a simple persistent store.
    Phase 4: Moving towards Vector DB (Chroma/FAISS).
    Current version: SQLite-based associative memory.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.db_path
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                topic TEXT,
                content TEXT NOT NULL,
                metadata TEXT, -- JSON string for extra info
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Index for faster retrieval
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_topic ON long_term_memory (agent_id, topic)")
        conn.commit()
        conn.close()

    def store(self, agent_id: str, content: str, topic: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Stores a memory for a specific agent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        meta_json = json.dumps(metadata) if metadata else None
        cursor.execute("""
            INSERT INTO long_term_memory (agent_id, topic, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (agent_id, topic, content, meta_json))
        conn.commit()
        conn.close()
        console.log(f"🧠 Memory stored for agent [bold cyan]{agent_id}[/bold cyan]")

    def retrieve(self, agent_id: str, topic: Optional[str] = None, limit: int = 5, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieves relevant memories for an agent with optional metadata filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT content, topic, metadata, timestamp FROM long_term_memory WHERE agent_id = ?"
        params = [agent_id]
        
        if topic:
            query += " AND (topic LIKE ? OR content LIKE ?)"
            params.extend([f"%{topic}%", f"%{topic}%"])
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = [dict(row) for row in rows]

        # Apply metadata filter in Python for now (SQLite JSON support varies)
        if metadata_filter:
            filtered_results = []
            for res in results:
                if res['metadata']:
                    meta = json.loads(res['metadata'])
                    if all(meta.get(k) == v for k, v in metadata_filter.items()):
                        filtered_results.append(res)
            results = filtered_results

        # Sort by timestamp and limit
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        return results[:limit]

# Singleton instance
memory_manager = MemoryManager()
