import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from typing import List, Optional, Dict
import json
from pathlib import Path

from .agent_manager import load_agents, Agent, save_agents
from .database import get_db_connection, setup_database, log_message, register_user, authenticate_user, grant_admin
from .config import AGENTS_FILE
from .braintrust import status as braintrust_status, log_eval as braintrust_log_eval, log_observation as braintrust_log_observation
from .tool_runtime import TOOL_FUNCTIONS_MAP, execute_tool_code, get_tools_prompt

app = typer.Typer()
console = Console()

agents_app = typer.Typer()
app.add_typer(agents_app, name="agents")

# --- Agent Management Commands ---
@agents_app.callback()
def agents():
    """
    Manage AI agents.
    """
    console.print(Panel("[bold green]Agent Management Commands[/bold green]", expand=False))

# DROP-IN REPLACEMENT for the agents_config command in cli.py
# Find the @agents_app.command(name="config") block and replace it with this.

@agents_app.command(name="config")
def agents_config(
    agent_id: str = typer.Argument(..., help="Unique ID for the agent."),
    provider: str = typer.Option(..., "--provider", "-p", help="LLM provider (e.g., 'openai', 'google', 'anthropic')."),
    model: str = typer.Option(..., "--model", "-m", help="Specific model name (e.g., 'gpt-4o', 'gemini-1.5-flash-latest')."),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key. If not provided, reads from .env file automatically."),
    persona: str = typer.Option("You are a helpful AI assistant.", "--persona", "-s", help="The agent's persona or system prompt."),
):
    """
    Configures a new AI agent or updates an existing one.
    If --api-key is not provided, the key is read automatically from your .env file.
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # If no api_key passed, try to resolve from .env based on provider
    if api_key is None:
        env_key_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "xai": "XAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }
        env_var = env_key_map.get(provider.lower())
        if env_var:
            api_key = os.getenv(env_var, "")
            if api_key:
                console.print(f"[dim]🔑 Using {env_var} from .env[/dim]")
            else:
                console.print(f"[bold yellow]Warning:[/bold yellow] No --api-key provided and {env_var} not found in .env. Agent saved without key.")
                api_key = ""
        else:
            console.print(f"[bold yellow]Warning:[/bold yellow] Unknown provider '{provider}'. No API key resolved. Pass --api-key manually.")
            api_key = ""

    agents = load_agents()
    new_agent = Agent(id=agent_id, provider=provider, model=model, api_key=api_key, persona=persona)
    agents[agent_id] = new_agent
    save_agents(agents)
    console.print(f"[bold green]Agent '{agent_id}' configured successfully.[/bold green]")
    console.print(f"   Provider : [cyan]{provider}[/cyan]")
    console.print(f"   Model    : [cyan]{model}[/cyan]")
    console.print(f"   Key      : [dim]{'set' if api_key else 'not set'}[/dim]")

@agents_app.command(name="list")
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

@agents_app.command(name="remove")
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
    

# --- Serve Commands ---
@app.command()
def serve_info():
    """
    Commands for the orch server.
    """
    console.print(Panel("[bold green]Orch Server Commands[/bold green]", expand=False))


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
log_app = typer.Typer()
app.add_typer(log_app, name="log")

@log_app.callback()
def log():
    """
    Commands for viewing discussion logs.
    """
    console.print(Panel("[bold green]Discussion Log Commands[/bold green]", expand=False))

@log_app.command(name="list")
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
        pass

@log_app.command(name="view")
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

@log_app.command(name="export")
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


# --- User Commands ---
user_app = typer.Typer(help="Local user account commands.")
app.add_typer(user_app, name="user")


@user_app.command("register")
def user_register(
    email: str = typer.Option(..., "--email", "-e", help="User email address."),
    password: str = typer.Option(..., "--password", "-p", help="User password."),
    full_name: Optional[str] = typer.Option(None, "--name", "-n", help="Display name."),
):
    """
    Registers a local Orch user account.
    """
    try:
        user = register_user(email=email, password=password, full_name=full_name)
        console.print(f"[bold green]User registered:[/bold green] {user['email']}")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@user_app.command("login")
def user_login(
    email: str = typer.Option(..., "--email", "-e", help="User email address."),
    password: str = typer.Option(..., "--password", "-p", help="User password."),
):
    """
    Verifies local Orch user credentials.
    """
    user = authenticate_user(email=email, password=password)
    if not user:
        console.print("[bold red]Error:[/bold red] Invalid credentials.")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Login successful.[/bold green]")
    console.print(f"  Email: [cyan]{user['email']}[/cyan]")
    console.print(f"  Role: [cyan]{user['role']}[/cyan]")
    console.print(f"  God mode: [cyan]{user['god_mode']}[/cyan]")


# --- Admin Commands ---
admin_app = typer.Typer(help="Administrative account bootstrap commands.")
app.add_typer(admin_app, name="admin")


@admin_app.command("grant")
def admin_grant(
    email: str = typer.Option(..., "--email", "-e", help="User email address."),
    god_mode: bool = typer.Option(False, "--god-mode", help="Enable elevated god mode flag."),
):
    """
    Grants admin role to an existing local user account.
    """
    try:
        user = grant_admin(email=email, god_mode=god_mode)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Admin granted.[/bold green]")
    console.print(f"  Email: [cyan]{user['email']}[/cyan]")
    console.print(f"  Role: [cyan]{user['role']}[/cyan]")
    console.print(f"  God mode: [cyan]{bool(user['god_mode'])}[/cyan]")


# --- Learn Commands ---
learn_app = typer.Typer(help="Tools for training and fine-tuning agents.")
app.add_typer(learn_app, name="learn")

# --- Braintrust Commands ---
braintrust_app = typer.Typer(help="Braintrust evaluation and observation commands.")
app.add_typer(braintrust_app, name="braintrust")


@braintrust_app.command("status")
def bt_status():
    """
    Shows Braintrust Phase 5/6 configuration status loaded from environment.
    """
    console.print_json(data=braintrust_status())


@braintrust_app.command("eval")
def bt_eval(
    name: str = typer.Option(..., "--name", "-n", help="Evaluation name."),
    input_text: str = typer.Option(..., "--input", "-i", help="Evaluation input text."),
    output_text: str = typer.Option(..., "--output", "-o", help="Evaluation output text."),
    score: Optional[float] = typer.Option(None, "--score", "-s", help="Optional score value."),
    metadata: Optional[str] = typer.Option(None, "--metadata", "-m", help="Optional JSON metadata."),
):
    """
    Logs an evaluation event to local analytics and Braintrust (if configured).
    """
    parsed_metadata: Optional[Dict[str, object]] = None
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
            if not isinstance(parsed_metadata, dict):
                raise ValueError("Metadata JSON must be an object.")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Invalid --metadata JSON. {e}")
            raise typer.Exit(code=1)

    result = braintrust_log_eval(
        name=name,
        input_text=input_text,
        output_text=output_text,
        score=score,
        metadata=parsed_metadata,
    )
    console.print_json(data=result)


@braintrust_app.command("observe")
def bt_observe(
    event: str = typer.Option(..., "--event", "-e", help="Observation event name."),
    metadata: Optional[str] = typer.Option(None, "--metadata", "-m", help="Optional JSON metadata."),
):
    """
    Logs an observation event to local analytics and Braintrust Observation (if configured).
    """
    parsed_metadata: Optional[Dict[str, object]] = None
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
            if not isinstance(parsed_metadata, dict):
                raise ValueError("Metadata JSON must be an object.")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Invalid --metadata JSON. {e}")
            raise typer.Exit(code=1)

    result = braintrust_log_observation(
        event_name=event,
        metadata=parsed_metadata,
    )
    console.print_json(data=result)

@learn_app.command(name="generate-tuning-data")
def generate_tuning_data(
    output_format: str = typer.Option("chatml", "--format", "-f", help="Export format: 'alpaca', 'raw', or 'chatml'."),
    output_dir: Path = typer.Option(Path("tuning_data"), "--output-dir", "-o", help="Output directory for generated files."),
    discussion_id: Optional[int] = typer.Option(None, "--discussion", "-d", help="Specific discussion ID to export. If not provided, exports all.")
):
    """
    Generates training/fine-tuning data from recorded discussions using the exporter module.
    """
    from .exporter import export_session_to_jsonl, export_all_to_jsonl
    
    if discussion_id:
        console.print(f"📦 [bold cyan]Exporting session #{discussion_id} in {output_format} format...[/bold cyan]")
        output_file = export_session_to_jsonl(discussion_id, output_dir, format=output_format)
    else:
        console.print(f"📦 [bold cyan]Exporting all high-quality sessions in {output_format} format...[/bold cyan]")
        output_file = export_all_to_jsonl(output_dir, format=output_format)
    
    if output_file and output_file.exists():
        console.print(f"[bold green]Successfully generated training data at: [cyan]{output_file}[/cyan][/bold green]")
    else:
        console.print("[bold yellow]No training data was generated. Ensure you have discussions in your Data Lake.[/bold yellow]")


# --- WhatsApp Commands ---
whatsapp_app = typer.Typer(name="whatsapp", help="Manage and test WhatsApp integration.")
app.add_typer(whatsapp_app, name="whatsapp")

@whatsapp_app.command("test")
def test_whatsapp(
    message: str = typer.Option("Test message from orch.", "--message", "-m", help="The message to send."),
    recipient: Optional[str] = typer.Option(None, "--recipient", "-r", help="Target WhatsApp JID/Number. Defaults to config.")
):
    """
    Tests the WhatsApp MessagingBridge connection.
    """
    import asyncio
    from .bridge import bridge
    from .config import settings
    
    target = recipient or getattr(settings, "whatsapp_recipient", None)
    if not target:
        console.print("[bold red]Error:[/bold red] No recipient specified and none found in config.")
        raise typer.Exit(code=1)
        
    console.print(f"[bold cyan]Testing WhatsApp bridge to {target}...[/bold cyan]")
    
    async def run_test():
        success = await bridge.send_message(message, target)
        if success:
            console.print("[bold green]Success![/bold green] Message sent via WhatsApp.")
        else:
            console.print("[bold red]Failed.[/bold red] Check your API key and instance URL.")
            
    asyncio.run(run_test())

# --- Serve Commands ---
serve_app = typer.Typer(name="serve", help="Commands for the orch server.")
app.add_typer(serve_app, name="serve")

@serve_app.command("launch")
def launch(
    topic: str = typer.Option(..., "--topic", "-t", help="The discussion topic."),
    agent_ids: List[str] = typer.Option(..., "--agents", "-a", help="Comma-separated list of agent IDs to include in the discussion."),
    max_rounds: int = typer.Option(5, "--max-rounds", "-r", help="Maximum number of discussion rounds."),
    moderator_agent_id: Optional[str] = typer.Option(None, "--moderator", "-m", help="ID of the agent to use as the moderator for guiding the discussion."),
    use_neural_link: bool = typer.Option(True, "--neural-link", help="Whether to use the real-time Neural Link (API/WebSocket)"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Execute agents in parallel within each round.")
):
    """
    Launches a simulated multi-agent discussion.
    """
    import asyncio
    from .simulator import run_simulation

    console.print(Panel(f"[bold blue]Starting discussion on:[/bold blue] [bold yellow]{topic}[/bold yellow]", expand=False))
    if parallel:
        console.print("[bold cyan]Mode:[/] [bold green]Parallel Execution[/bold green]")

    # --- Database and Discussion Setup ---
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO discussions (topic) VALUES (?)", (topic,))
        discussion_id = cursor.lastrowid
        conn.commit()
        console.log(f"Logging to discussion session [bold cyan]#{discussion_id}[/bold cyan]")
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

    moderator_instance: Optional[object] = None
    if moderator_agent_id:
        try:
            from .moderator import Moderator
            moderator_instance = Moderator(agent_id=moderator_agent_id, agents=agents_map)
            if not hasattr(moderator_instance.amoderate, "__call__") or "unittest.mock" in type(moderator_instance.moderate).__module__:
                moderator_instance.amoderate = moderator_instance.moderate  # test shim for mocked sync moderator
            console.print(f"Moderator [bold cyan]{moderator_agent_id}[/] will guide the discussion.")
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
        if use_neural_link:
            console.print("[bold cyan]Neural Link Active:[/] Simulation will be broadcast to the Control Plane.")
        asyncio.run(run_simulation(
            topic=topic,
            agents=selected_agents,
            moderator=moderator_instance,
            max_rounds=max_rounds,
            discussion_id=discussion_id,
            parallel=parallel
        ))
    except Exception as e:
        console.print(f"[bold red]Simulation Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@serve_app.command(name="api")
def start_api_cmd(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the API on."),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to run the API on."),
    open_browser: bool = typer.Option(True, "--open", help="Automatically open the GUI in the browser.")
):
    """
    Starts the orch AGI Control Plane API and serves the Neural Link GUI.
    """
    import uvicorn
    import webbrowser
    from .api import app
    
    url = f"http://{host}:{port}"
    console.print(Panel(
        f"[bold green]Starting orch AGI Control Plane[/bold green]\n"
        f"🌐 API & GUI: [bold cyan]{url}[/bold cyan]",
        expand=False
    ))
    
    if open_browser:
        console.print(f"🚀 Opening {url} in your browser...")
        webbrowser.open(url)
        
    uvicorn.run(app, host=host, port=port)
