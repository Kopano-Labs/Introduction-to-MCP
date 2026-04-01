import unittest
import sqlite3
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from orch.orch.tools.database_tool import sql_query

class TestDatabaseTool(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.test_db_path = "test_orch_datastore.db"
        self.conn = sqlite3.connect(self.test_db_path)
        self.cursor = self.conn.cursor()
        
        # Create schema for testing
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.cursor.execute("INSERT INTO discussions (topic) VALUES ('Test Topic')")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_sql_query_success(self):
        from orch.orch.tools import database_tool
        from pathlib import Path
        original_path = database_tool.DB_PATH
        database_tool.DB_PATH = Path(self.test_db_path)
        try:
            result = sql_query("SELECT topic FROM discussions")
            self.assertIn("Test Topic", result)
        finally:
            database_tool.DB_PATH = original_path

    def test_sql_query_invalid_sql(self):
        # This will fail because sql_query is not yet implemented
        result = sql_query("SELECT * FROM non_existent_table")
        self.assertIn("Error", result)

    def test_sql_query_empty_result(self):
        # This will fail because sql_query is not yet implemented
        result = sql_query("SELECT * FROM discussions WHERE id = 999")
        self.assertIn("No results found", result)

if __name__ == "__main__":
    unittest.main()
