import sqlite3
from pathlib import Path

db_path = Path("c:/Users/rkhol/OneDrive/Documents/Anthropic/Introduction to MCP/orch/.orch_data/orch.db")

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "block_id" not in columns:
        print("Adding block_id...")
        cursor.execute("ALTER TABLE messages ADD COLUMN block_id TEXT UNIQUE")
    if "value_score" not in columns:
        print("Adding value_score...")
        cursor.execute("ALTER TABLE messages ADD COLUMN value_score INTEGER DEFAULT 0")
    if "improvement_hint" not in columns:
        print("Adding improvement_hint...")
        cursor.execute("ALTER TABLE messages ADD COLUMN improvement_hint TEXT")
        
    conn.commit()
    conn.close()
    print("Migration complete!")
else:
    print("No DB found, skipping migration.")
