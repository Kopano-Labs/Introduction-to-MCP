"""
Phase 2 → Phase 3: Simulation Engine (Round-Robin Logic)
Neural Link Patch: Async broadcast protocol wired to the API.
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
from typing import List, Dict, Any, Optional
from litellm import acompletion  # ← async version of completion
from rich.console import Console
from .datalake import start_discussion, log_interaction
from .context import format_history
import httpx  # ← async HTTP client for broadcasting

console = Console()

# --- NEURAL LINK CONFIG ---
# The URL of the running API server. Matches api.py's uvicorn host/port.
API_BROADCAST_URL = "http://localhost:8000/broadcast"


async def _broadcast(payload: Dict[str, Any]) -> None:
    """
    Fire-and-forget signal to the API's /broadcast endpoint.
    If the API is offline, we log the error and keep the simulation running.
    The GUI going dark should never crash the simulation.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(API_BROADCAST_URL, json=payload)
    except httpx.ConnectError:
        console.print("[dim yellow]⚠ Neural Link offline — GUI not connected. Simulation continues.[/]")
    except Exception as e:
        console.print(f"[dim red]⚠ Broadcast error: {e}[/]")


async def run_simulation(
    topic: str,
    agents: List[Any],
    moderator: Any,
    max_rounds: int,
    discussion_id: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Executes the async round-robin simulation loop between configured agents,
    guided by the Moderator AI, logging to the Data Lake and broadcasting
    every agent thought to the React GUI via the Neural Link.
    """
    console.print(f"[bold green]Starting Simulation:[/] {topic}")
    if discussion_id is None:
        discussion_id = start_discussion(topic)
    history = []

    # Broadcast simulation start so the GUI can initialise its view
    await _broadcast({
        "type": "simulation_start",
        "discussion_id": discussion_id,
        "topic": topic,
        "agents": [a.id for a in agents],
        "max_rounds": max_rounds,
    })

    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]--- Round {round_num} ---[/]")

        # Moderator sets the direction for this round
        if moderator:
            prompt = await moderator.amoderate(topic, history)
        else:
            prompt = history[-1]["content"] if history else topic
        
        log_interaction(discussion_id, "moderator-model", "moderator", None, prompt, "reasoning")

        # Broadcast the moderator's directive so the GUI shows it in real-time
        await _broadcast({
            "type": "moderator_directive",
            "discussion_id": discussion_id,
            "round": round_num,
            "content": prompt,
        })

        for agent in agents:
            # Broadcast that this agent is "thinking" — lets the GUI show a spinner
            await _broadcast({
                "type": "thinking", # Changed from agent_thinking to match App.tsx
                "discussion_id": discussion_id,
                "round": round_num,
                "agent": agent.id, # Changed from agent_id to match App.tsx
            })

            try:
                # In non-moderated mode, we use the last response as the prompt.
                # In moderated mode, the 'prompt' variable holds the moderator's directive.
                current_turn_prompt = prompt if moderator else (history[-1]["content"] if history else topic)

                response = await agent.agenerate_response(current_turn_prompt, history)
                reply = response.content.strip()

                # Save to shared history
                history.append({"role": "assistant", "name": agent.id, "content": reply})

                # Log to Data Lake
                log_interaction(discussion_id, agent.model, agent.id, reply, current_turn_prompt, "execution")

                console.print(f"[bold cyan]{agent.id}:[/] {reply}\n")

                # Broadcast the agent's response — this is the core Neural Link signal
                await _broadcast({
                    "type": "response", # Changed from agent_response to match App.tsx
                    "discussion_id": discussion_id,
                    "round": round_num,
                    "agent": agent.id, # Changed from agent_id to match App.tsx
                    "model": agent.model,
                    "content": reply,
                })

            except Exception as e:
                console.print(f"[bold red]Error calling {agent.id}: {e}[/]")

                # Broadcast errors too so the GUI can show an agent as failed
                await _broadcast({
                    "type": "agent_error",
                    "discussion_id": discussion_id,
                    "round": round_num,
                    "agent_id": agent.id,
                    "error": str(e),
                })

    console.print("[bold green]Simulation Complete.[/]")

    # Broadcast simulation end so the GUI can render a summary state
    await _broadcast({
        "type": "simulation_end",
        "discussion_id": discussion_id,
        "topic": topic,
        "total_rounds": max_rounds,
    })

    return history