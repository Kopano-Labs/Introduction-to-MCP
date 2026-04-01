"""
Phase 2: Context Handling
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
from typing import List, Dict

def format_history(history: List[Dict[str, str]], current_prompt: str) -> List[Dict[str, str]]:
    """
    Standardizes history injection so all models share the same state.
    Transforms the custom dictionary format into the standard LLM messages format.
    """
    formatted_messages = [
        {"role": "system", "content": "You are participating in a multi-agent think tank discussion."}
    ]
    
    for msg in history:
        formatted_messages.append({"role": msg["role"], "content": f"[{msg.get('name', 'Unknown')}]: {msg['content']}"})
        
    formatted_messages.append({"role": "user", "content": current_prompt})
    return formatted_messages