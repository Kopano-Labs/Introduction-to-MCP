from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
from pathlib import Path
from rich.console import Console

console = Console()

from .memory import memory_manager
from .config import AGENTS_FILE

class Agent(BaseModel):
    id: str
    provider: str
    model: str
    api_key: str
    persona: str = "You are a helpful AI assistant."

    async def agenerate_response(self, current_turn_prompt: str, full_history: List[Dict[str, str]], topic: Optional[str] = None) -> Any:
        """
        Generates an async response from the agent using LiteLLM.
        """
        # Retrieve relevant memories
        memories = memory_manager.retrieve(self.id, topic=topic)
        memory_context = ""
        if memories:
            memory_context = "\n[Relevant Memories]:\n" + "\n".join([f"- {m['content']}" for m in memories])
        
        system_prompt = self.persona + memory_context
        messages = [{"role": "system", "content": system_prompt}]
        for msg in full_history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": current_turn_prompt})

        try:
            from litellm import acompletion

            response = await acompletion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                stream=False,
            )
            # Store this interaction in memory for future recall
            memory_manager.store(self.id, response.choices[0].message.content, topic=topic)
            return response.choices[0].message
        except Exception as e:
            console.log(f"[bold red]Agent {self.id} failed to generate a response:[/] {e}")
            raise

    def generate_response(self, current_turn_prompt: str, full_history: List[Dict[str, str]]) -> Any:
        """
        Generates a response from the agent using LiteLLM.
        The full_history includes all previous messages, including system prompts and user inputs.
        The current_turn_prompt is the specific prompt for this agent's turn.
        """
        # Start with the agent's persona as a system message
        messages = [{"role": "system", "content": self.persona}]
        
        # Add the full conversation history, ensuring only 'role' and 'content' are passed to LiteLLM
        for msg in full_history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        # Add the specific prompt for this turn as a user message
        messages.append({"role": "user", "content": current_turn_prompt})

        try:
            from litellm import completion

            response = completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                stream=False, # For now, keep it non-streaming for simplicity in CLI
            )
            # LiteLLM response.choices[0].message is a dict-like object
            return response.choices[0].message
        except Exception as e:
            console.log(f"[bold red]Agent {self.id} failed to generate a response:[/] {e}")
            raise

def load_agents() -> Dict[str, Agent]:
    """
    Loads configured agents from the JSON file.
    """
    if not AGENTS_FILE.exists():
        return {}
    try:
        with open(AGENTS_FILE, "r") as f:
            agents_data = json.load(f)
        return {id: Agent(**data) for id, data in agents_data.items()}
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/bold red] Could not decode agents.json. File might be corrupt.")
        return {}

def save_agents(agents: Dict[str, Agent]):
    """
    Saves configured agents to the JSON file.
    """
    AGENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENTS_FILE, "w") as f:
        json.dump({id: agent.dict() for id, agent in agents.items()}, f, indent=4)
