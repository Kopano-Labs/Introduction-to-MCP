import json
from pathlib import Path
from rich.console import Console
from .config import settings

console = Console()

class Agent:
    def __init__(self, id: str, provider: str, model: str, api_key: str | None = None, persona: str = "", _api_key: str | None = None):
        self.id = id
        self.provider = provider
        self.model = model
        self.persona = persona or f"You are {id.capitalize()}, a helpful and truthful AI."
        
        # --- PHASE 3: AUTO-LOAD FROM .ENV FALLBACK ---
        # Handle both serialised and direct constructor names
        self._api_key = _api_key or api_key
        
    @property
    def api_key(self) -> str | None:
        # If we have a real-looking key in the object, use it
        placeholders = ["MOCK_KEY", "FALLBACK", "your_gemini_key", "your_anthropic_key", "your_openai_key"]
        if self._api_key and self._api_key not in placeholders:
            return self._api_key
            
        # Fallback to global settings (.env)
        key_map = {
            "gemini": settings.gemini_api_key,
            "grok": settings.grok_api_key,
            "xai": settings.grok_api_key,
            "copilot": settings.openai_api_key,
            "openai": settings.openai_api_key,
            "claude": settings.anthropic_api_key,
            "anthropic": settings.anthropic_api_key,
            "aiml": settings.aiml_api_key,
        }
        return key_map.get(self.id.lower()) or key_map.get(self.provider.lower())

def load_agents() -> dict[str, Agent]:
    if not settings.agents_file.exists():
        return {}
    with open(settings.agents_file) as f:
        data = json.load(f)
    return {k: Agent(**v) for k, v in data.items()}

def save_agent(agent: Agent):
    agents = load_agents()
    agents[agent.id] = agent
    settings.agents_file.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.agents_file, "w") as f:
        json.dump({k: vars(v) for k, v in agents.items()}, f, indent=2)
    console.print(f"[green]✓ Agent [bold]{agent.id}[/bold] configured[/green]")
