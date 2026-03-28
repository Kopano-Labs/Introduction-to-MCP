import typer
from rich.console import Console
from rich.table import Table
from .agent_manager import Agent, save_agent, load_agents
from .simulator import run_simulated_discussion
from .config import settings

app = typer.Typer(rich_markup_mode="rich", help="orch – Multi-AI Collaboration Platform (MCP)")
console = Console()

# ====================== SERVE ======================
serve_app = typer.Typer()
app.add_typer(serve_app, name="serve", help="Simulation Control")

@serve_app.command("launch")
def serve_launch(
    topic: str = typer.Option(..., "--topic", "-t", help="Discussion topic"),
    agents: str = typer.Option(..., "--agents", "-a", help="Comma-separated agent IDs e.g. gemini,grok"),
    max_rounds: int = typer.Option(10, "--max-rounds", "-r"),
    group_simulated: bool = typer.Option(True, "--group-simulated", help="Run in terminal only (Phase 1)"),
):
    """Start a new simulation (Phase 1 = terminal only)"""
    agent_list = [a.strip() for a in agents.split(",")]
    if group_simulated:
        run_simulated_discussion(topic, agent_list, max_rounds)
    else:
        console.print("[yellow]Real WhatsApp mode coming in Phase 3[/yellow]")

# ====================== CHAT ======================
chat_app = typer.Typer()
app.add_typer(chat_app, name="chat", help="Interactive Control")

@chat_app.command("status")
def chat_status():
    console.print("[blue]No active session (simulation only in Phase 1)[/blue]")

@chat_app.command("log")
def chat_log():
    console.print("[dim]Full log will be in SQLite from Phase 2[/dim]")

# ====================== AGENTS ======================
agents_app = typer.Typer()
app.add_typer(agents_app, name="agents", help="Management")

@agents_app.command("list")
def agents_list():
    agents = load_agents()
    if not agents:
        console.print("[yellow]No agents configured yet.[/yellow]")
        return
    table = Table(title="Configured Agents")
    table.add_column("ID", style="cyan")
    table.add_column("Provider", style="magenta")
    table.add_column("Model")
    for a in agents.values():
        table.add_row(a.id, a.provider, a.model)
    console.print(table)

@agents_app.command("config")
def agents_config(
    id: str = typer.Argument(..., help="Agent ID e.g. gemini"),
    provider: str = typer.Option("gemini", "--provider", "-p"),
    model: str = typer.Option(None, "--model", "-m"),
    api_key: str = typer.Option(..., "--api-key", "-k", prompt=True, hide_input=True),
    persona: str = typer.Option("", "--persona"),
):
    """Configure a new AI (stores key securely in .env + agents.json)"""
    agent = Agent(id=id, provider=provider, model=model or id, api_key=api_key, persona=persona)
    save_agent(agent)

@agents_app.command("inspect")
def agents_inspect(id: str):
    agents = load_agents()
    if id not in agents:
        console.print(f"[red]Agent {id} not found[/red]")
        return
    a = agents[id]
    console.print(a.__dict__)

# ====================== LEARN ======================
learn_app = typer.Typer()
app.add_typer(learn_app, name="learn", help="Knowledge Base")

@learn_app.command("datasets")
def learn_datasets_list():
    console.print("[dim]Datasets coming in Phase 2 (SQLite)[/dim]")

@app.command()
def version():
    console.print("orch v0.1.0 – Phase 1 Foundation ✅")

if __name__ == "__main__":
    app()
