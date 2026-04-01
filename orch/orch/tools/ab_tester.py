import pandas as pd
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from ..database import get_db_connection

def ab_test_analysis() -> str:
    """
    Performs A/B testing analysis on agents/models based on value_score and override_score.
    """
    try:
        conn = get_db_connection()
        
        # Load the Data Lake audit logs
        query = "SELECT model, agent_id, value_score, override_score FROM audit_logs"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return "Data Lake is empty. Cannot perform A/B test analysis."

        # Group by Model to compare performance
        model_group = df.groupby('model').agg({
            'value_score': 'mean',
            'override_score': 'mean',
            'agent_id': 'count'
        }).rename(columns={'agent_id': 'interaction_count'}).round(2)

        # Sort by value_score (primary metric)
        model_group = model_group.sort_values(by='value_score', ascending=False)

        # Group by Agent ID to see individual performance
        agent_group = df.groupby('agent_id').agg({
            'value_score': 'mean',
            'override_score': 'mean',
            'model': 'first'
        }).round(2)

        report = "### A/B Test Analysis Report\n\n"
        
        report += "#### 🚀 Model Performance Comparison\n"
        report += model_group.to_markdown() + "\n\n"

        report += "#### 👤 Top Performing Agents\n"
        top_agents = agent_group.sort_values(by='value_score', ascending=False).head(5)
        report += top_agents.to_markdown() + "\n\n"

        # Winner Analysis
        if len(model_group) > 1:
            winner = model_group.index[0]
            runner_up = model_group.index[1]
            diff = model_group.iloc[0]['value_score'] - model_group.iloc[1]['value_score']
            report += f"**Conclusion:** The leading model is `{winner}`, outperforming `{runner_up}` by {diff:.2f} value score points on average."
        else:
            report += "Only one model detected. More diverse agent interactions are needed for a comparative analysis."

        return report

    except Exception as e:
        return f"Error during A/B test analysis: {str(e)}"
