import typer
from rich.console import Console
from rich.table import Table
from .agent_manager import Agent, save_agent, load_agents
from .simulator import run_simulated_discussion
from .database import SessionLocal, Session, Message
from .exporter import export_session_to_jsonl, export_all_to_jsonl
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
    whatsapp: bool = typer.Option(False, "--whatsapp", "-w", help="Mirror discussion to WhatsApp (Phase 3)"),
):
    """Start a new simulation with optional WhatsApp broadcasting."""
    agent_list = [a.strip() for a in agents.split(",")]
    run_simulated_discussion(topic, agent_list, max_rounds, whatsapp_mode=whatsapp)

# ====================== CHAT ======================
chat_app = typer.Typer()
app.add_typer(chat_app, name="chat", help="Interactive Control")

@chat_app.command("status")
def chat_status():
    console.print("[blue]No active session (simulation only in Phase 1)[/blue]")

@chat_app.command("sessions")
def chat_sessions_list():
    """List all archived discussion sessions in the Data Lake."""
    db = SessionLocal()
    try:
        sessions = db.query(Session).order_by(Session.created_at.desc()).all()
        if not sessions:
            console.print("[yellow]No sessions found in the Data Lake.[/yellow]")
            return
            
        table = Table(title="Discussion History")
        table.add_column("ID", style="cyan")
        table.add_column("Topic", style="white")
        table.add_column("Created At", style="magenta")
        table.add_column("Agents", style="green")
        
        for s in sessions:
            table.add_row(str(s.id), s.topic, s.created_at.strftime("%Y-%m-%d %H:%M"), s.agents)
            
        console.print(table)
    finally:
        db.close()

@chat_app.command("log")
def chat_log(session_id: int = typer.Option(None, "--session", "-s")):
    """View the actual discussion history from the Data Lake."""
    db = SessionLocal()
    try:
        session = None
        if session_id:
            session = db.query(Session).filter(Session.id == session_id).first()
        else:
            session = db.query(Session).order_by(Session.created_at.desc()).first()
            
        if not session:
            console.print("[red]No archived sessions found![/red]")
            return
            
        console.print(f"📄 [bold blue]LOG: Session #{session.id}[/bold blue] | Topic: {session.topic}")
        for msg in session.messages:
            console.print(f"[bold cyan][{msg.agent_id.upper()}][/bold cyan] (Round {msg.round_num}): {msg.content}")
    finally:
        db.close()

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
    """List and export training datasets from the Data Lake."""
    console.print("[blue]Exporting Full Knowledge Base to JSONL...[/blue]")
    output_path = settings.data_dir / "datasets"
    output_path.mkdir(parents=True, exist_ok=True)
    
    dataset_file = export_all_to_jsonl(output_path)
    console.print(f"[bold green]✓ Done! Master dataset saved at: {dataset_file}[/bold green]")

@learn_app.command("export")
def learn_export(session_id: int):
    """Export a specific session for fine-tuning."""
    output_path = settings.data_dir / "datasets"
    output_path.mkdir(parents=True, exist_ok=True)
    
    file = export_session_to_jsonl(session_id, output_path)
    if file:
        console.print(f"[green]✓ Session #{session_id} exported to: {file}[/green]")
    else:
         console.print(f"[red]Error: Session #{session_id} not found.[/red]")

@learn_app.command("insights")
def learn_insights(session_id: int):
    """Analyze a session and extract distilled logical truths."""
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            console.print(f"[red]Session #{session_id} not found.[/red]")
            return
            
        console.print(f"🧠 [bold blue]INSIGHTS: Session #{session_id}[/bold blue] | Analyzing...")
        
        # We use a special model call to 'distill' the logic
        moderator_agent = next((a for a in load_agents().values() if a.id == "moderator"), list(load_agents().values())[0])
        full_text = "\n".join([f"[{m.agent_id}]: {m.content}" for m in session.messages])
        
        insight_prompt = f"Distill the following multi-agent discussion into 3-5 core logical 'Truths' or 'Conclusions' for a Knowledge Base:\n\n{full_text}"
        
        insights = call_ai(moderator_agent, insight_prompt)
        console.print(Panel(insights, title="💡 Distilled Knowledge"))
    finally:
        db.close()

@app.command("board")
def board():
    """Start the AGI Command Center GUI Backend (API + WebSocket)."""
    from .api import start_api
    start_api()

@app.command()
def version():
    console.print("orch v0.5.0 – AGI Command Center Ready 🛰️")

if __name__ == "__main__":
    app()
