import sqlite3
import pandas as pd
from pathlib import Path
from ..database import DB_PATH

def sql_query(query: str) -> str:
    """
    Executes a SQL query against the Data Lake SQLite database.
    Use this to retrieve information about past discussions, messages, and audit logs.
    
    Returns a formatted string containing the results or an error message.
    """
    if not DB_PATH.exists():
        return f"Error: Database not found at {DB_PATH}"

    try:
        conn = sqlite3.connect(DB_PATH)
        # Using pandas for nice formatting
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return "No results found for the given query."
            
        return df.to_markdown(index=False)
    except Exception as e:
        return f"Error executing SQL query: {e}"
