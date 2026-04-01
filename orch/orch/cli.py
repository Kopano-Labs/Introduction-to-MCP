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
from .database import get_db_connection, setup_database, log_message
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
    "write_file": ("filesystem", "write_file"),
    "list_directory": ("filesystem", "list_directory"),
    "delete_file": ("filesystem", "delete_file"),
    "execute_code": ("code_execution", "execute_code"),
}

# --- Serve Commands ---
@app.command()
def serve_info():
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
- list_directory(directory_path: str = "."): Lists the contents of a directory.
- delete_file(file_path: str): Deletes a file.
- search(query: str): Performs a web search for a given query.
- execute_code(code: str): Executes Python code and returns the result.
"""

def execute_tool_code(tool_code: str) -> str:
    """
    Executes a tool call string like 'read_file("file.txt")'.
    """
    try:
        import ast

        # Parse the tool code string into an AST
        tree = ast.parse(tool_code.strip())
        
        # Ensure it's a single function call
        if not isinstance(tree, ast.Module) or len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr) or not isinstance(tree.body[0].value, ast.Call):
            return f"Error: '{tool_code}' is not a valid single tool call."
            
        call_node = tree.body[0].value
        if not isinstance(call_node.func, ast.Name):
            return f"Error: Complex function calls are not supported."
            
        tool_name = call_node.func.id

        if tool_name not in TOOL_FUNCTIONS_MAP:
            return f"Error: Tool '{tool_name}' not found."

        # Extract arguments
        args = []
        for arg in call_node.args:
            if isinstance(arg, ast.Constant):
                args.append(arg.value)
            elif isinstance(arg, ast.Str): # For older Python versions
                args.append(arg.s)
            else:
                return f"Error: Only literal arguments are supported."
        
        # Extract keyword arguments
        kwargs = {}
        for kw in call_node.keywords:
            if isinstance(kw.value, ast.Constant):
                kwargs[kw.arg] = kw.value.value
            elif isinstance(kw.value, ast.Str):
                kwargs[kw.arg] = kw.value.s
            else:
                return f"Error: Only literal keyword arguments are supported."

        module_name, function_name = TOOL_FUNCTIONS_MAP[tool_name]
        
        module_path = f"orch.tools.{module_name}"
        tool_module = importlib.import_module(module_path)
        tool_function = getattr(tool_module, function_name)

        # Call the tool function
        result = tool_function(*args, **kwargs)
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


# --- Learn Commands ---
learn_app = typer.Typer(help="Tools for training and fine-tuning agents.")
app.add_typer(learn_app, name="learn")

@learn_app.command(name="generate-tuning-data")
def generate_tuning_data(
    output_format: str = typer.Option("alpaca", "--format", "-f", help="Export format: 'alpaca', 'jsonl', or 'chatml'."),
    output_file: Path = typer.Option("tuning_data.json", "--output", "-o", help="Output file path."),
    discussion_id: Optional[int] = typer.Option(None, "--discussion", "-d", help="Specific discussion ID to export. If not provided, exports all.")
):
    """
    Generates training/fine-tuning data from recorded discussions.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Querying from the audit_logs table for 'execution' type to get prompt/response
        query = "SELECT topic, prompt, message as response FROM audit_logs JOIN discussions ON audit_logs.discussion_id = discussions.id WHERE log_type = 'execution'"
        params = []
        if discussion_id:
            query += " AND discussion_id = ?"
            params.append(discussion_id)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            # Fallback to the old 'messages' table if audit_logs is empty
            query = "SELECT topic, prompt, response FROM messages JOIN discussions ON messages.discussion_id = discussions.id WHERE is_moderator_direction = 0"
            params = []
            if discussion_id:
                query += " AND discussion_id = ?"
                params.append(discussion_id)
            cursor.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            console.print("[bold yellow]No training data found in the Data Lake.[/bold yellow]")
            return

        tuning_data = []
        for row in rows:
            if output_format == "alpaca":
                tuning_data.append({
                    "instruction": row["prompt"] or f"Discuss the topic: {row['topic']}",
                    "input": "",
                    "output": row["response"]
                })
            elif output_format == "chatml":
                # Format as a conversation for ChatML
                tuning_data.append({
                    "messages": [
                        {"role": "system", "content": f"Topic: {row['topic']}"},
                        {"role": "user", "content": row["prompt"] or "Please provide your input."},
                        {"role": "assistant", "content": row["response"]}
                    ]
                })
            else: # JSONL
                tuning_data.append({
                    "prompt": row["prompt"] or f"Discuss the topic: {row['topic']}",
                    "completion": row["response"]
                })

        with open(output_file, "w", encoding="utf-8") as f:
            if output_format == "alpaca":
                json.dump(tuning_data, f, indent=4, ensure_ascii=False)
            else:
                for entry in tuning_data:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        console.print(f"[bold green]Successfully generated {len(tuning_data)} examples in {output_format} format to: [cyan]{output_file}[/cyan][/bold green]")
    finally:
        if conn:
            conn.close()


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
            discussion_id=discussion_id,
            parallel=parallel
        ))
    except Exception as e:
        console.print(f"[bold red]Simulation Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@serve_app.command(name="api")
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