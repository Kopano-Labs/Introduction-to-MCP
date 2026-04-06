"""
Test Suite for Data Lake SQLite Operations
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
import pytest
import sqlite3
from orch.datalake import get_connection, start_discussion, log_interaction

@pytest.fixture
def in_memory_db(monkeypatch):
    """Mock the DB connection to use an in-memory SQLite database for testing."""
    db_uri = "file:orch_datalake_tests?mode=memory&cache=shared"
    anchor = sqlite3.connect(db_uri, uri=True)
    anchor.row_factory = sqlite3.Row
    anchor.executescript("""
        CREATE TABLE discussions (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL);
        CREATE TABLE audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, discussion_id INTEGER, model TEXT, agent_id TEXT, message TEXT, prompt TEXT, log_type TEXT);
    """)

    def _connect():
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr("orch.datalake.get_connection", _connect)
    yield anchor
    anchor.close()

def test_insert_logs(in_memory_db):
    """Validates that Phase 2 Data Lake insertions work correctly."""
    disc_id = start_discussion("Test Topic")
    assert disc_id == 1
    
    log_interaction(disc_id, "test-model", "test-agent", "hello", "say hello", "execution")
    
    cursor = in_memory_db.cursor()
    cursor.execute("SELECT * FROM audit_logs WHERE discussion_id = ?", (disc_id,))
    row = cursor.fetchone()
    assert row["log_type"] == "execution"
    assert row["agent_id"] == "test-agent"
