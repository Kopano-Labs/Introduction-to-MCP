import json
from pathlib import Path
from rich.console import Console
from .config import settings

console = Console()

class Agent:
    def __init__(self, id: str, provider: str, model: str, api_key: str | None = None, persona: str = ""):
        self.id = id
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.persona = persona or f"You are {id.capitalize()}, a helpful and truthful AI."

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
