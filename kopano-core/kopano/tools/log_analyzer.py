import os
import re
from collections import Counter
from pathlib import Path

def analyze_logs(file_path: str) -> str:
    """
    Analyzes a log file and returns a structured summary, including log counts by level 
    and identifying potential errors.
    
    Args:
        file_path: The path to the log file to analyze.
        
    Returns:
        A Markdown-formatted summary of the log analysis.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: Log file not found at {file_path}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        if total_lines == 0:
            return "The log file is empty."
        
        # Regex to find log levels (e.g., INFO, ERROR, WARNING, DEBUG)
        level_pattern = re.compile(r"\b(INFO|ERROR|WARNING|DEBUG|CRITICAL|FATAL)\b", re.IGNORECASE)
        levels = []
        errors_found = []
        
        for line in lines:
            match = level_pattern.search(line)
            if match:
                level = match.group(0).upper()
                levels.append(level)
                if level in ("ERROR", "CRITICAL", "FATAL"):
                    errors_found.append(line.strip())
        
        level_counts = Counter(levels)
        
        summary = f"### Log Summary for `{path.name}`\n\n"
        summary += f"- **Total Lines:** {total_lines}\n"
        summary += f"- **Identified Log Levels:**\n"
        for level, count in level_counts.items():
            summary += f"  - {level}: {count}\n"
            
        if errors_found:
            summary += "\n#### Identified Errors/Critical Issues:\n"
            for i, error in enumerate(errors_found[:10]): # Limit to first 10 for the summary
                summary += f"{i+1}. `{error}`\n"
            if len(errors_found) > 10:
                summary += f"... and {len(errors_found) - 10} more.\n"
                
        return summary
    except Exception as e:
        return f"Error analyzing log file: {e}"
