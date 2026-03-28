from rich.console import Console
from rich.panel import Panel
from .agent_manager import load_agents, Agent
from .llm import call_ai
import time

console = Console()

def run_simulated_discussion(topic: str, agent_ids: list[str], max_rounds: int = 10):
    agents = load_agents()
    selected = [agents[a] for a in agent_ids if a in agents]

    if not selected:
        console.print("[red]No agents configured! Run: orch agents config ...[/red]")
        return

    console.print(Panel(f"[bold blue]MCP Simulated Group Chat[/bold blue]\nTopic: [italic]{topic}[/italic]", title="🚀 STARTING", expand=False))

    history = []
    moderator_prompt = f"You are the Moderator. Keep the discussion on topic: {topic}. Current history:\n"

    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]=== ROUND {round_num} ===[/bold yellow]")
        for agent in selected:
            # Build full context
            context = "\n".join([f"[{m['agent']}]: {m['text']}" for m in history[-10:]])
            full_prompt = f"{agent.persona}\n\n{moderator_prompt}{context}\n\nNow it is YOUR turn. Respond concisely and directly to the group."

            console.print(f"[bold cyan][{agent.id.upper()}][/bold cyan] thinking...", end=" ")
            try:
                # For Phase 1, we can return a mock response if API keys are missing
                if not agent.api_key:
                    reply = f"I am {agent.id.upper()}. I think the ethical implications of {topic} are profound."
                else:
                    reply = call_ai(agent, full_prompt)
            except Exception as e:
                reply = f"⚠️ Error: {e}"

            console.print(reply)
            history.append({"agent": agent.id, "text": reply, "round": round_num})
            time.sleep(0.3)  # realistic pause

    console.print(Panel("[green]Discussion finished![/green]", title="✅ END"))
    console.print(f"[dim]Discussion logged ({len(history)} messages)[/dim]")
    return history
