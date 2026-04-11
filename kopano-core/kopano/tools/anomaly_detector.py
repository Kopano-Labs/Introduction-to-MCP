import pandas as pd
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from ..database import get_db_connection

def detect_anomalies() -> str:
    """
    Analyzes the Data Lake (SQLite database) for anomalies in agent performance, 
    security alerts, and execution corrections.
    """
    try:
        conn = get_db_connection()
        
        # Load data from the Data Lake
        audit_df = pd.read_sql_query("SELECT * FROM audit_logs", conn)
        messages_df = pd.read_sql_query("SELECT * FROM messages", conn)
        
        conn.close()

        if audit_df.empty and messages_df.empty:
            return "Data Lake is empty. No anomalies found."

        anomalies = []

        # 1. Security Alerts Anomaly
        security_alerts = audit_df[audit_df['log_type'] == 'security_alert']
        if not security_alerts.empty:
            anomalies.append(f"Found {len(security_alerts)} security alerts in the logs.")

        # 2. Execution Corrections Anomaly
        corrections = audit_df[audit_df['log_type'] == 'execution_correction']
        if len(corrections) > (len(audit_df) * 0.1): # More than 10% corrections
            anomalies.append(f"High frequency of execution corrections ({len(corrections)} found). This may indicate agent model instability.")

        # 3. Value Score Anomalies (Low outliers)
        if 'value_score' in audit_df.columns:
            avg_score = audit_df['value_score'].mean()
            low_scores = audit_df[audit_df['value_score'] < (avg_score * 0.5)]
            if not low_scores.empty:
                anomalies.append(f"Found {len(low_scores)} entries with significantly low value scores (below 50% of the average {avg_score:.2f}).")

        # 4. Message Frequency Anomaly (Basic gap analysis)
        if not messages_df.empty and 'timestamp' in messages_df.columns:
            messages_df['timestamp'] = pd.to_datetime(messages_df['timestamp'])
            messages_df = messages_df.sort_values('timestamp')
            messages_df['gap'] = messages_df['timestamp'].diff().dt.total_seconds()
            
            # Find gaps > 60 seconds (adjust as needed)
            long_gaps = messages_df[messages_df['gap'] > 60]
            if not long_gaps.empty:
                anomalies.append(f"Found {len(long_gaps)} long gaps (over 60s) between agent responses, suggesting potential latency or processing delays.")

        if not anomalies:
            return "Anomaly Detection Scan Complete: No significant anomalies detected."
        
        summary = "### Anomaly Detection Report\n\n" + "\n".join([f"- {a}" for a in anomalies])
        return summary

    except Exception as e:
        return f"Error during anomaly detection: {str(e)}"
