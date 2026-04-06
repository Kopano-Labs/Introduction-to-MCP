import gc
import os
import unittest
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from orch.orch.tools.database_tool import sql_query

class TestDatabaseTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_orch_datastore.db"
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("INSERT INTO discussions (topic) VALUES ('Test Topic')")
            conn.commit()

    def tearDown(self):
        gc.collect()
        for _ in range(10):
            try:
                self.temp_dir.cleanup()
                break
            except PermissionError:
                time.sleep(0.05)
        else:
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)

    def test_sql_query_success(self):
        from orch.orch.tools import database_tool
        original_path = database_tool.DB_PATH
        database_tool.DB_PATH = self.test_db_path
        try:
            result = sql_query("SELECT topic FROM discussions")
            self.assertIn("Test Topic", result)
        finally:
            database_tool.DB_PATH = original_path

    def test_sql_query_invalid_sql(self):
        from orch.orch.tools import database_tool
        original_path = database_tool.DB_PATH
        database_tool.DB_PATH = self.test_db_path
        try:
            result = sql_query("SELECT * FROM non_existent_table")
            self.assertIn("Error", result)
        finally:
            database_tool.DB_PATH = original_path

    def test_sql_query_empty_result(self):
        from orch.orch.tools import database_tool
        original_path = database_tool.DB_PATH
        database_tool.DB_PATH = self.test_db_path
        try:
            result = sql_query("SELECT * FROM discussions WHERE id = 999")
            self.assertIn("No results found", result)
        finally:
            database_tool.DB_PATH = original_path

if __name__ == "__main__":
    unittest.main()
