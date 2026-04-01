import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.markdown import Markdown
import time
from typing import List, Optional
from typing import List, Optional, Dict
import json
from pathlib import Path
import re
import importlib

from .agent_manager import load_agents, Agent, save_agents
from .moderator import Moderator
from .database import get_db_connection
from .database import get_db_connection, setup_database
from .config import AGENTS_FILE

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

@agents.command(name="remove")
def agents_remove(
    agent_id: str = typer.Argument(..., help="The unique ID of the agent to remove.")
):
    """
    Removes a configured AI agent.
    """
    agents = load_agents()
    if agent_id not in agents:
        console.print(f"[bold red]Error:[/bold red] Agent '{agent_id}' not found.")
        raise typer.Exit(code=1)

    del agents[agent_id]
    save_agents(agents)
    console.print(f"[bold green]Agent '{agent_id}' removed successfully.[/bold green]")
    

# --- Tool Management ---

TOOL_FUNCTIONS_MAP = {
    "search": ("search", "perform_search"),
    "read_file": ("filesystem", "read_file"),
    "write_file": ("write_file", "write_file"),
}

# --- Serve Commands ---
@app.command()
def serve():
    """
    Commands for the orch server.
    """
    console.print(Panel("[bold green]Orch Server Commands[/bold green]", expand=False))

def get_tools_prompt() -> str:
    """Generates the tool usage instructions for the agent's system prompt."""
    return """
You have access to the following tools. To use a tool, respond with ONLY the tool call inside <tool_code> XML tags.
Example: <tool_code>write_file("path/to/file.txt", "File content here.")</tool_code>

Available Tools:
- read_file(file_path: str): Reads the content of a specified file.
- write_file(file_path: str, content: str): Writes content to a specified file, creating directories if they don't exist.
- search(query: str): Performs a web search for a given query.
"""

def execute_tool_code(tool_code: str) -> str:
    """
    Commands for the orch server.
    Executes a tool call string like 'read_file("file.txt")'.
    This is a simple implementation for demonstration. A real implementation would use a more robust parser.
    """
    console.print(Panel("[bold green]Orch Server Commands[/bold green]", expand=False))
    try:
        tool_name_match = re.match(r"(\w+)\(", tool_code)
        if not tool_name_match:
            return f"Error: Could not parse tool name from '{tool_code}'."
        
        tool_name = tool_name_match.group(1)

        if tool_name not in TOOL_FUNCTIONS_MAP:
            return f"Error: Tool '{tool_name}' not found."

        # Extract arguments by finding all double-quoted strings
        args = re.findall(r'"((?:\\"|[^"])*)"', tool_code)

        module_name, function_name = TOOL_FUNCTIONS_MAP[tool_name]
        
        module_path = f"orch.tools.{module_name}"
        tool_module = importlib.import_module(module_path)
        tool_function = getattr(tool_module, function_name)

        result = tool_function(*args)
        return str(result)
    except Exception as e:
        return f"Error executing tool code '{tool_code}': {e}"


tools_app = typer.Typer(name="tools", help="Manage and run agent tools.")
app.add_typer(tools_app, name="tools")

@tools_app.command("run")
def run_tool(
    tool_name: str = typer.Argument(..., help=f"The name of the tool to run (e.g., {', '.join(TOOL_FUNCTIONS_MAP.keys())})."),
    tool_args: List[str] = typer.Argument(None, help="Arguments for the tool function."),
):
    """
    Dynamically loads and runs a specified tool function.
    
    Examples:
    - orch tools run search "The future of AI"
    - orch tools run read_file "my_document.txt"
    - orch tools run write_file "new_blog_post.md" "# My New Post"
    """
    tool_code = f'{tool_name}(' + ', '.join(f'"{arg}"' for arg in tool_args) + ')'
    console.print(f"Executing: [yellow]{tool_code}[/yellow]")
    result = execute_tool_code(tool_code)
    console.print(f"[green]Tool '{tool_name}' executed successfully:[/green]")
    console.print(result)


# --- Log Commands ---
@app.command()
def log():
    """
    Commands for viewing discussion logs.
    """
    console.print(Panel("[bold green]Discussion Log Commands[/bold green]", expand=False))

@log.command(name="list")
def log_list():
    """
    Lists all recorded discussion sessions.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, topic, start_time FROM discussions ORDER BY start_time DESC")
        discussions = cursor.fetchall()

        if not discussions:
            console.print("No discussion sessions found.")
            return

        table = Table(title="Recorded Discussions")
        table.add_column("ID", style="cyan")
        table.add_column("Topic", style="magenta")
        table.add_column("Start Time", style="green")

        for d in discussions:
            table.add_row(str(d["id"]), d["topic"], d["start_time"])
        
        console.print(table)
    finally:
        if conn:
            conn.close()

@log.command(name="view")
def log_view(
    discussion_id: int = typer.Argument(..., help="The ID of the discussion session to view.")
):
    """
    Views the messages and events within a specific discussion session.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Get discussion topic
        cursor.execute("SELECT topic, start_time FROM discussions WHERE id = ?", (discussion_id,))
        discussion = cursor.fetchone()
        if not discussion:
            console.print(f"[bold red]Error:[/bold red] Discussion session with ID '{discussion_id}' not found.")
            return

        console.print(Panel(
            f"[bold blue]Viewing Discussion:[/bold blue] [bold yellow]{discussion['topic']}[/bold yellow]\n"
            f"Started: [italic]{discussion['start_time']}[/italic]",
            expand=False,
            title=f"Session #{discussion_id}"
        ))

        # Get all messages for the discussion
        cursor.execute(
            """SELECT round_num, agent_id, agent_model, prompt, response, is_moderator_direction, timestamp
               FROM messages WHERE discussion_id = ? ORDER BY round_num ASC, timestamp ASC""",
            (discussion_id,)
        )
        messages = cursor.fetchall()

        if not messages:
            console.print("No messages recorded for this discussion session.")
            return

        current_round = 0
        for msg in messages:
            if msg["round_num"] > current_round:
                current_round = msg["round_num"]
                console.print(Panel(f"[bold yellow]--- Round {current_round} ---[/bold yellow]", expand=False))

            if msg["is_moderator_direction"]:
                console.print(
                    Panel(
                        f"[bold magenta]Moderator ({msg['agent_id']}):[/bold magenta]\n"
                        f"{msg['response']}", # Moderator direction is stored in 'response' field
                        title=f"[bold green]Moderator Direction[/bold green]",
                        border_style="magenta"
                    )
                )
            else:
                console.print(
                    Panel(
                        Markdown(f"**{msg['agent_id']} ({msg['agent_model']}):**\n"
                                 f"Prompt: {msg['prompt'] or 'N/A'}\n"
                                 f"{msg['response']}"),
                        title=f"[bold green]Agent: {msg['agent_id']}[/bold green]",
                        border_style="green"
                    )
                )
            console.print("\n") # Add a little spacing between messages

    finally:
        if conn:
            conn.close()

@log.command(name="export")
def log_export(
    discussion_id: int = typer.Argument(..., help="The ID of the discussion session to export."),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path. Defaults to orch_discussion_<id>.json")
):
    """
    Exports a specific discussion session log to a JSON file.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Get discussion topic and start_time
        cursor.execute("SELECT topic, start_time FROM discussions WHERE id = ?", (discussion_id,))
        discussion_row = cursor.fetchone()
        if not discussion_row:
            console.print(f"[bold red]Error:[/bold red] Discussion session with ID '{discussion_id}' not found.")
            return

        discussion_data = {
            "id": discussion_id,
            "topic": discussion_row["topic"],
            "start_time": discussion_row["start_time"],
            "messages": []
        }

        # Get all messages for the discussion
        cursor.execute(
            """SELECT round_num, agent_id, agent_model, prompt, response, is_moderator_direction, timestamp
               FROM messages WHERE discussion_id = ? ORDER BY round_num ASC, timestamp ASC""",
            (discussion_id,)
        )
        message_rows = cursor.fetchall()

        if not message_rows:
            console.print(f"No messages recorded for discussion session '{discussion_id}'. Exporting discussion metadata only.")
        
        for msg_row in message_rows:
            message_entry = {
                "round_num": msg_row["round_num"],
                "agent_id": msg_row["agent_id"],
                "agent_model": msg_row["agent_model"],
                "timestamp": msg_row["timestamp"],
            }
            if msg_row["is_moderator_direction"]:
                message_entry["type"] = "moderator_direction"
                message_entry["direction"] = msg_row["response"] # Moderator direction is in 'response'
            else:
                message_entry["type"] = "agent_response"
                message_entry["prompt"] = msg_row["prompt"]
                message_entry["response"] = msg_row["response"]
            
            discussion_data["messages"].append(message_entry)

        # Determine output file path
        if output_file is None:
            file_name = Path.cwd() / f"orch_discussion_{discussion_id}.json"
        else:
            file_name = output_file

        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(discussion_data, f, indent=4, ensure_ascii=False)
            console.print(f"[bold green]Discussion #{discussion_id} exported successfully to:[/bold green] [cyan]{file_name}[/cyan]")
        except IOError as e:
            console.print(f"[bold red]Error:[/bold red] Could not write to file '{file_name}'. {e}")
            raise typer.Exit(code=1)

    finally:
        if conn:
            conn.close()


# --- Serve Commands ---
@app.command()
def serve():
    """
    Commands for the orch server.
    """
    console.print(Panel("[bold green]Orch Server Commands[/bold green]", expand=False))
    console.print(Panel("[bold green]Orch Server Commands[/bold green]", expand=False)) # This is a placeholder

@serve.command()
def launch(
    topic: str = typer.Option(..., "--topic", "-t", help="The discussion topic."),
    agent_ids: List[str] = typer.Option(..., "--agents", "-a", help="Comma-separated list of agent IDs to include in the discussion."),
    max_rounds: int = typer.Option(5, "--max-rounds", "-r", help="Maximum number of discussion rounds."),
    moderator_agent_id: Optional[str] = typer.Option(None, "--moderator", "-m", help="ID of the agent to use as the moderator for guiding the discussion."),
    use_neural_link: bool = typer.Option(True, "--neural-link", help="Whether to use the real-time Neural Link (API/WebSocket)"),
):
    """
    Launches a simulated multi-agent discussion.
    """
    import asyncio
    from .simulator import run_simulation

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
    finally:
        if conn:
            conn.close()

    agents_map = load_agents()
    selected_agents = []
    for agent_id in agent_ids:
        if agent_id in agents_map:
            selected_agents.append(agents_map[agent_id])
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
            
    # Prepend the tools prompt to each agent's persona
    tools_prompt = get_tools_prompt()
    for agent in selected_agents:
        agent.persona = tools_prompt + "\n---\n" + agent.persona
    if moderator_instance:
        moderator_instance.agent.persona = tools_prompt + "\n---\n" + moderator_instance.agent.persona

    # Run the simulation asynchronously
    try:
        asyncio.run(run_simulation(
            topic=topic,
            agents=selected_agents,
            moderator=moderator_instance,
            max_rounds=max_rounds,
            discussion_id=discussion_id
        ))
    except Exception as e:
        console.print(f"[bold red]Simulation Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@serve.command(name="api")
def start_api_cmd(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the API on."),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to run the API on.")
):
    """
    Starts the orch AGI Control Plane API.
    """
    import uvicorn
    from .api import app
    console.print(Panel(f"[bold green]Starting orch AGI Control Plane API on {host}:{port}...[/bold green]", expand=False))
    uvicorn.run(app, host=host, port=port)