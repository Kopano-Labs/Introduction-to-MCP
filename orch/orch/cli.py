import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.markdown import Markdown
import time
from typing import List, Optional

from .agent_manager import load_agents, Agent, save_agents
from .moderator import Moderator
from .database import get_db_connection

app = typer.Typer()
console = Console()

# --- Agent Management Commands ---
@app.command()
def agents():
    """
    Manage AI agents.
    """
    console.print(Panel("[bold green]Agent Management Commands[/bold green]", expand=False))

@agents.command(name="config")
def agents_config(
    agent_id: str = typer.Argument(..., help="Unique ID for the agent."),
    provider: str = typer.Option(..., "--provider", "-p", help="LLM provider (e.g., 'openai', 'google', 'anthropic')."),
    model: str = typer.Option(..., "--model", "-m", help="Specific model name (e.g., 'gpt-4o', 'gemini-1.5-flash-latest')."),
    api_key: str = typer.Option(..., "--api-key", "-k", help="API key for the LLM provider."),
    persona: str = typer.Option("You are a helpful AI assistant.", "--persona", "-s", help="The agent's persona or system prompt."),
):
    """
    Configures a new AI agent or updates an existing one.
    """
    agents = load_agents()
    new_agent = Agent(id=agent_id, provider=provider, model=model, api_key=api_key, persona=persona)
    agents[agent_id] = new_agent
    save_agents(agents)
    console.print(f"[bold green]Agent '{agent_id}' configured successfully.[/bold green]")

@agents.command(name="list")
def agents_list():
    """
    Lists all configured AI agents.
    """
    agents = load_agents()
    if not agents:
        console.print("No agents configured yet.")
        return

    console.print(Panel("[bold blue]Configured Agents[/bold blue]", expand=False))
    for agent_id, agent in agents.items():
        console.print(f"  [bold cyan]{agent_id}[/bold cyan]")
        console.print(f"    Provider: {agent.provider}")
        console.print(f"    Model: {agent.model}")
        console.print(f"    Persona: {agent.persona[:50]}...") # Truncate persona for display
        console.print("")

# --- Serve Commands ---
@app.command()
def serve():
    """
    Commands for the orch server.
    """
    console.print(Panel("[bold green]Orch Server Commands[/bold green]", expand=False))

@serve.command()
def launch(
    topic: str = typer.Option(..., "--topic", "-t", help="The discussion topic."),
    agent_ids: List[str] = typer.Option(..., "--agents", "-a", help="Comma-separated list of agent IDs to include in the discussion."),
    max_rounds: int = typer.Option(5, "--max-rounds", "-r", help="Maximum number of discussion rounds."),
    moderator_agent_id: Optional[str] = typer.Option(None, "--moderator", "-m", help="ID of the agent to use as the moderator for guiding the discussion."),
):
    """
    Launches a simulated multi-agent discussion.
    """
    console.print(Panel(f"[bold blue]Starting discussion on:[/bold blue] [bold yellow]{topic}[/bold yellow]", expand=False))

    # --- Database and Discussion Setup ---
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO discussions (topic) VALUES (?)", (topic,))
        discussion_id = cursor.lastrowid
        conn.commit()
        console.log(f"🗄️  Logging to discussion session [bold cyan]#{discussion_id}[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]Database Error:[/bold red] Could not start discussion session. {e}")
        if conn:
            conn.close()
        raise typer.Exit(code=1)

    agents = load_agents()
    selected_agents = []
    for agent_id in agent_ids:
        if agent_id in agents:
            selected_agents.append(agents[agent_id])
        else:
            console.print(f"[bold red]Error:[/bold red] Agent '{agent_id}' not found.")
            raise typer.Exit(code=1)

    if not selected_agents:
        console.print("[bold red]Error:[/bold red] No valid agents selected for the discussion.")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Agents participating:[/bold green] {', '.join([a.id for a in selected_agents])}")

    moderator_instance: Optional[Moderator] = None
    if moderator_agent_id:
        try:
            moderator_instance = Moderator(agent_id=moderator_agent_id)
            console.print(f"🤖 Moderator [bold cyan]{moderator_agent_id}[/] will guide the discussion.")
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(code=1)

    try:
        history = []
        current_prompt = topic # Initial prompt for the first agent

        for round_num in range(max_rounds):
            console.print(Panel(f"[bold yellow]--- Round {round_num + 1} ---[/bold yellow]", expand=False))

            for i, agent in enumerate(selected_agents):
                with Live(console=console, screen=False, refresh_per_second=4) as live:
                    live.update(Panel(f"[bold blue]Agent {agent.id} is thinking...[/bold blue]", expand=False))

                    try:
                        prompt_for_this_turn = current_prompt

                        # If a moderator is active, get a new prompt from the moderator
                        if moderator_instance and (round_num > 0 or i > 0):
                            moderator_direction = moderator_instance.moderate(topic, history)

                            # Log moderator's action to the database
                            cursor.execute(
                                """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, response, is_moderator_direction)
                                   VALUES (?, ?, ?, ?, ?, 1)""",
                                (discussion_id, round_num + 1, moderator_instance.agent.id, moderator_instance.agent.model, moderator_direction)
                            )
                            conn.commit()

                            prompt_for_this_turn = moderator_direction
                            console.print(f"[bold magenta]Moderator's direction for {agent.id}:[/bold magenta] {prompt_for_this_turn}")

                        response_message = agent.generate_response(prompt_for_this_turn, history)
                        response_content = response_message.content

                        # Log agent's response to the database
                        cursor.execute(
                            """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction)
                               VALUES (?, ?, ?, ?, ?, ?, 0)""",
                            (discussion_id, round_num + 1, agent.id, agent.model, prompt_for_this_turn, response_content)
                        )
                        conn.commit()

                        history.append({"role": "assistant", "content": response_content, "name": agent.id})

                        live.update(Panel(
                            Markdown(f"**{agent.id} ({agent.model}):**\n{response_content}"),
                            title=f"[bold green]Agent: {agent.id}[/bold green]",
                            border_style="green"
                        ))
                        time.sleep(1) # Simulate reading time

                        # If no moderator, the next agent's prompt is the current agent's response.
                        # If a moderator is active, the moderator will generate the next prompt.
                        if not moderator_instance:
                            current_prompt = response_content

                    except Exception as e:
                        live.update(Panel(f"[bold red]Error with agent {agent.id}:[/bold red] {e}", border_style="red"))
                        console.print(f"[bold red]Discussion halted due to error with agent {agent.id}.[/bold red]")
                        raise typer.Exit(code=1)

        console.print(Panel("[bold green]Discussion Ended.[/bold green]", expand=False))

    finally:
        if conn:
            conn.close()
            console.log("🗄️  Database connection closed.")