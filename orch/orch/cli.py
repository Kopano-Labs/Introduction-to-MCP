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
            
    # Prepend the tools prompt to each agent's persona
    tools_prompt = get_tools_prompt()
    for agent in selected_agents:
        agent.persona = tools_prompt + "\n---\n" + agent.persona
    if moderator_instance:
        moderator_instance.agent.persona = tools_prompt + "\n---\n" + moderator_instance.agent.persona

    try:
        # The canonical history of the discussion, including user prompts, agent responses, and moderator directions.
        # Each entry will be a dict like {"role": "user", "content": "...", "name": "..."}
        full_conversation_history: List[Dict[str, str]] = []
        
        # Start the conversation with the initial topic as a user message
        full_conversation_history.append({"role": "user", "content": topic, "name": "user"})

        for round_num in range(max_rounds):
            console.print(Panel(f"[bold yellow]--- Round {round_num + 1} ---[/bold yellow]", expand=False))

            for i, agent in enumerate(selected_agents):
                with Live(console=console, screen=False, refresh_per_second=4) as live:
                    live.update(Panel(f"[bold blue]Agent {agent.id} is thinking...[/bold blue]", expand=False))

                    try:
                        current_turn_prompt: str

                        # If a moderator is active, and it's not the very first turn of the very first round,
                        # the moderator provides the prompt.
                        if moderator_instance and (round_num > 0 or i > 0):
                            moderator_direction = moderator_instance.moderate(topic, full_conversation_history)

                            # Log moderator's action to the database
                            cursor.execute(
                                """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, response, is_moderator_direction)
                                   VALUES (?, ?, ?, ?, ?, 1)""",
                                (discussion_id, round_num + 1, moderator_instance.agent.id, moderator_instance.agent.model, moderator_direction)
                            )
                            conn.commit()
                            # Add moderator's direction to the full conversation history
                            full_conversation_history.append({"role": "system", "content": moderator_direction, "name": moderator_instance.agent.id})
                            current_turn_prompt = moderator_direction
                            console.print(f"[bold magenta]Moderator's direction for {agent.id}:[/bold magenta] {current_turn_prompt}")
                        else:
                            # For the very first agent's turn, the prompt is the initial topic.
                            # For subsequent agents without a moderator, the prompt is the previous agent's response.
                            # We take the content of the last message in the history as the prompt for the current turn.
                            current_turn_prompt = full_conversation_history[-1]["content"]


                        response_message = agent.generate_response(current_turn_prompt, full_conversation_history)
                        response_content = response_message.content
                        response_content = response_message.content.strip()

                        # Log agent's response to the database
                        cursor.execute(
                            """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction)
                               VALUES (?, ?, ?, ?, ?, ?, 0)""",
                            (discussion_id, round_num + 1, agent.id, agent.model, current_turn_prompt, response_content)
                        )
                        conn.commit()
                        # Check for tool calls
                        tool_code_match = re.search(r"<tool_code>([\s\S]*?)<\/tool_code>", response_content)

                        # Add agent's response to the full conversation history
                        full_conversation_history.append({"role": "assistant", "content": response_content, "name": agent.id})
                        if tool_code_match:
                            tool_code = tool_code_match.group(1).strip()
                            live.update(Panel(f"Agent {agent.id} wants to run a tool:\n[yellow]{tool_code}[/yellow]", border_style="yellow"))
                            time.sleep(1)

                        live.update(Panel(
                            Markdown(f"**{agent.id} ({agent.model}):**\n{response_content}"),
                            title=f"[bold green]Agent: {agent.id}[/bold green]",
                            border_style="green"
                        ))
                        time.sleep(1) # Simulate reading time # Simulate reading time
                            # Log the agent's thought process (the tool call)
                            cursor.execute(
                                """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction)
                                   VALUES (?, ?, ?, ?, ?, ?, 0)""",
                                (discussion_id, round_num + 1, agent.id, agent.model, current_turn_prompt, response_content)
                            )
                            conn.commit()
                            full_conversation_history.append({"role": "assistant", "content": response_content, "name": agent.id})

                            # Execute the tool
                            tool_result = execute_tool_code(tool_code)
                            live.update(Panel(f"Tool Result:\n{tool_result}", border_style="cyan"))
                            time.sleep(1)

                            # Log the tool result as a system message (using is_moderator_direction for now)
                            cursor.execute(
                                """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, response, is_moderator_direction)
                                   VALUES (?, ?, ?, ?, ?, 1)""",
                                (discussion_id, round_num + 1, "tool_executor", "system", tool_result)
                            )
                            conn.commit()
                            full_conversation_history.append({"role": "system", "content": tool_result, "name": "tool_executor"})
                        
                        else: # No tool call, proceed as normal
                            # Log agent's response to the database
                            cursor.execute(
                                """INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction)
                                   VALUES (?, ?, ?, ?, ?, ?, 0)""",
                                (discussion_id, round_num + 1, agent.id, agent.model, current_turn_prompt, response_content)
                            )
                            conn.commit()

                            # Add agent's response to the full conversation history
                            full_conversation_history.append({"role": "assistant", "content": response_content, "name": agent.id})

                            live.update(Panel(
                                Markdown(f"**{agent.id} ({agent.model}):**\n{response_content}"),
                                title=f"[bold green]Agent: {agent.id}[/bold green]",
                                border_style="green"
                            ))
                            time.sleep(1)
                            
                    except Exception as e:
                        live.update(Panel(f"[bold red]Error with agent {agent.id}:[/bold red] {e}", border_style="red"))
                        console.print(f"[bold red]Discussion halted due to error with agent {agent.id}.[/bold red]")
                        raise typer.Exit(code=1)

        console.print(Panel("[bold green]Discussion Ended.[/bold green]", expand=False))

    finally:
        if conn:
            conn.close()
            console.log("🗄️  Database connection closed.")