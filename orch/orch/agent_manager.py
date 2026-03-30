from typing import Dict, List, Any
from pydantic import BaseModel
import json
from pathlib import Path
from litellm import completion
from rich.console import Console

console = Console()

# Define the path for agent configuration
AGENT_CONFIG_PATH = Path.home() / ".orch" / "agents.json"

class Agent(BaseModel):
    id: str
    provider: str
    model: str
    api_key: str
    persona: str = "You are a helpful AI assistant."

    def generate_response(self, prompt: str, history: List[Dict[str, str]]) -> Any:
        """
        Generates a response from the agent using LiteLLM.
        """
        messages = [{"role": "system", "content": self.persona}]
        for msg in history:
            # Ensure 'role' and 'content' are present, and handle 'name' for display
            role = msg.get("role", "user") # Default to user if role is missing
            content = msg.get("content", "")
            # For LiteLLM, 'name' is usually not part of the standard message dict unless it's a tool call.
            # We'll just pass role and content.
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        try:
            response = completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                stream=False, # For now, keep it non-streaming for simplicity in CLI
            )
            # LiteLLM response.choices[0].message is a dict-like object
            return response.choices[0].message
        except Exception as e:
            console.log(f"🚨 [bold red]Agent {self.id} failed to generate a response:[/] {e}")
            raise

def load_agents() -> Dict[str, Agent]:
    """
    Loads configured agents from the JSON file.
    """
    if not AGENT_CONFIG_PATH.exists():
        return {}
    try:
        with open(AGENT_CONFIG_PATH, "r") as f:
            agents_data = json.load(f)
        return {id: Agent(**data) for id, data in agents_data.items()}
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/bold red] Could not decode agents.json. File might be corrupt.")
        return {}

def save_agents(agents: Dict[str, Agent]):
    """
    Saves configured agents to the JSON file.
    """
    AGENT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENT_CONFIG_PATH, "w") as f:
        json.dump({id: agent.dict() for id, agent in agents.items()}, f, indent=4)