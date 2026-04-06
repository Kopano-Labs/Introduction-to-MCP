"""
Phase 2 → Phase 3: Simulation Engine (Round-Robin Logic)
Neural Link Patch: Async broadcast protocol wired to the API.
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
from typing import List, Dict, Any, Optional
from litellm import acompletion  # ← async version of completion
from rich.console import Console
from .database import get_db_connection, log_interaction, log_message
from .moderator import Moderator, SecurityAuditor
import httpx  # ← async HTTP client for broadcasting
import asyncio
import inspect
from unittest.mock import AsyncMock
from .tool_runtime import execute_tool_code

console = Console()

# --- NEURAL LINK CONFIG ---
# The URL of the running API server. Matches api.py's uvicorn host/port.
API_BROADCAST_URL = "http://localhost:8000/broadcast"


def _is_async_callable(candidate: Any) -> bool:
    return inspect.iscoroutinefunction(candidate) or isinstance(candidate, AsyncMock)


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
        console.print("[dim yellow]Neural Link offline - GUI not connected. Simulation continues.[/]")
    except Exception as e:
        console.print(f"[dim red]Broadcast error: {e}[/]")


from .bridge import bridge
from .config import settings
import re

async def _handle_tool_calls(reply: str, agent_id: str, discussion_id: int, round_num: int) -> str:
    """
    Detects and executes tool calls within an agent's response.
    Returns the tool result(s) to be appended to the conversation history.
    """
    tool_code_match = re.search(r"<tool_code>([\s\S]*?)<\/tool_code>", reply)
    if tool_code_match:
        tool_code = tool_code_match.group(1).strip()
        console.print(f"[bold yellow]Agent {agent_id} is calling a tool:[/] {tool_code}")
        
        # Broadcast that a tool is being executed
        await _broadcast({
            "type": "tool_execution",
            "discussion_id": discussion_id,
            "round": round_num,
            "agent": agent_id,
            "tool_code": tool_code
        })
        
        tool_result = execute_tool_code(tool_code)
        console.print(f"[bold cyan]Tool Result:[/] {tool_result}")
        
        # Broadcast the moderator's result
        await _broadcast({
            "type": "tool_result",
            "discussion_id": discussion_id,
            "round": round_num,
            "agent": agent_id,
            "result": tool_result
        })
        
        # Log tool result to Data Lake
        log_interaction(discussion_id, "system", "tool_executor", tool_result, tool_code, "tool_result", round_num=round_num)
        
        return f"\n[Tool Result]: {tool_result}"
    return ""


async def run_quick_match(gig_request: dict, providers: list[dict]) -> dict:
    from .tools.gig_matcher import match_gig
    return match_gig(
        gig_request.get("description", ""),
        gig_request.get("location", ""),
        gig_request.get("category", ""),
        gig_request.get("skills", []),
        providers,
    )


async def _process_agent_turn(agent, prompt, round_num, discussion_id, topic, history, moderator):
    """
    Processes a single agent's turn asynchronously.
    """
    # Broadcast that this agent is "thinking"
    await _broadcast({
        "type": "thinking",
        "discussion_id": discussion_id,
        "round": round_num,
        "agent": agent.id,
    })

    try:
        current_turn_prompt = prompt if moderator else (history[-1]["content"] if history else topic)
        agent_async = getattr(agent, "agenerate_response", None)
        agent_sync = getattr(agent, "generate_response", None)
        history_snapshot = [dict(item) for item in history]
        if agent_async and _is_async_callable(agent_async):
            response = await agent_async(current_turn_prompt, history_snapshot, topic=topic)
        elif agent_sync and "unittest.mock" in type(agent_sync).__module__:
            response = agent_sync(current_turn_prompt, history_snapshot)
        elif agent_sync:
            response = agent_sync(current_turn_prompt, history_snapshot)
        else:
            raise AttributeError(f"Agent {agent.id} has no response method")
        reply = response.content.strip()

        # Log to Data Lake
        log_interaction(discussion_id, agent.model, agent.id, reply, current_turn_prompt, "execution", round_num=round_num)
        log_message(discussion_id, round_num, agent.id, agent.model, current_turn_prompt, reply)

        console.print(f"[bold cyan]{agent.id}:[/] {reply}\n")

        # Broadcast the agent's response
        await _broadcast({
            "type": "response",
            "discussion_id": discussion_id,
            "round": round_num,
            "agent": agent.id,
            "model": agent.model,
            "content": reply,
        })

        # WhatsApp Gateway Integration
        if bridge.is_configured() and getattr(settings, "whatsapp_recipient", None):
            await bridge.send_message(
                f"*{agent.id} ({agent.model})*:\n{reply}",
                settings.whatsapp_recipient
            )

        # Tool Execution Logic
        tool_result_str = await _handle_tool_calls(reply, agent.id, discussion_id, round_num)
        
        # Self-Correction Loop (#92)
        if "Tool Error" in tool_result_str:
            console.print(f"[bold yellow]Agent {agent.id} encountered an error. Attempting self-correction...[/]")
            correction_prompt = f"The tool execution failed with the following error: {tool_result_str}\n\nPlease analyze the error and try a corrected tool_code or approach."
            # Recursive call with a depth limit (1 attempt for now)
            corrected_response = await agent.agenerate_response(correction_prompt, full_history=history + [{"role": "assistant", "name": agent.id, "content": reply, "tool_result": tool_result_str}], topic=topic)
            reply = corrected_response.content.strip()
            # Log corrected turn
            log_interaction(discussion_id, agent.model, agent.id, reply, correction_prompt, "execution_correction", round_num=round_num)
            console.print(f"[bold green]{agent.id} (Corrected):[/] {reply}\n")
            # Re-handle potential tool calls in the corrected response
            tool_result_str += "\n[Correction]: " + await _handle_tool_calls(reply, agent.id, discussion_id, round_num)

        return {"role": "assistant", "name": agent.id, "content": reply, "tool_result": tool_result_str}

    except Exception as e:
        console.print(f"[bold red]Error calling {agent.id}: {e}[/]")
        await _broadcast({
            "type": "agent_error",
            "discussion_id": discussion_id,
            "round": round_num,
            "agent_id": agent.id,
            "error": str(e),
        })
        return None

async def run_simulation(
    topic: str,
    agents: List[Any],
    moderator: Any,
    max_rounds: int,
    discussion_id: Optional[int] = None,
    parallel: bool = False
) -> List[Dict[str, str]]:
    """
    Executes the async simulation loop between configured agents,
    with optional parallel execution of agents within each round.
    """
    console.print(f"[bold green]Starting Simulation:[/] {topic}")
    if discussion_id is None:
        from .database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO discussions (topic) VALUES (?)", (topic,))
        discussion_id = cursor.lastrowid
        conn.commit()
        conn.close()
    history = [{"role": "user", "name": "user", "content": topic}]

    # Broadcast simulation start
    await _broadcast({
        "type": "simulation_start",
        "discussion_id": discussion_id,
        "topic": topic,
        "agents": [a.id for a in agents],
        "max_rounds": max_rounds,
    })

    # Initialize Security Auditor if a moderator is available to provide an agent
    auditor = None
    if moderator:
        try:
            auditor = SecurityAuditor(moderator.agent.id)
        except Exception:
            auditor = None

    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]--- Round {round_num} ---[/]")

        # Run Security Audit
        if auditor:
            audit_res = await auditor.audit(history)
            if "RISK" in audit_res:
                console.print(f"[bold red]Security Alert:[/] {audit_res}")
                await _broadcast({
                    "type": "security_alert",
                    "discussion_id": discussion_id,
                    "round": round_num,
                    "risk": audit_res
                })
                # Log risk
                log_interaction(discussion_id, auditor.agent.model, auditor.agent.id, audit_res, "Audit Loop", "security_alert", round_num=round_num)

        if moderator and round_num > 1:
            moderate_async = getattr(moderator, "amoderate", None)
            moderate_sync = getattr(moderator, "moderate", None)
            if moderate_async and _is_async_callable(moderate_async):
                prompt = await moderate_async(topic, [dict(item) for item in history])
            elif moderate_sync:
                prompt = moderate_sync(topic, [dict(item) for item in history])
            else:
                prompt = topic
            log_interaction(discussion_id, moderator.agent.model, moderator.agent.id, None, prompt, "reasoning", round_num=round_num)
            log_message(discussion_id, round_num, moderator.agent.id, moderator.agent.model, topic, prompt, is_moderator_direction=1)
            history.append({"role": "system", "name": moderator.agent.id, "content": prompt})
        else:
            prompt = topic
            log_interaction(discussion_id, "system", "system", None, prompt, "system", round_num=round_num)

        await _broadcast({
            "type": "moderator_directive",
            "discussion_id": discussion_id,
            "round": round_num,
            "content": prompt,
        })

        if parallel:
            # Parallel execution using asyncio.gather
            tasks = [_process_agent_turn(agent, prompt, round_num, discussion_id, topic, history, moderator) for agent in agents]
            results = await asyncio.gather(*tasks)
            for res in results:
                if res:
                    history.append({"role": res["role"], "name": res["name"], "content": res["content"]})
                    if res.get("tool_result"):
                        history.append({"role": "system", "name": "tool_executor", "content": res["tool_result"]})
        else:
            # Sequential execution
            for agent in agents:
                res = await _process_agent_turn(agent, prompt, round_num, discussion_id, topic, history, moderator)
                if res:
                    history.append({"role": res["role"], "name": res["name"], "content": res["content"]})
                    if res.get("tool_result"):
                        history.append({"role": "system", "name": "tool_executor", "content": res["tool_result"]})

    console.print("[bold green]Simulation Complete.[/]")
    console.print("Discussion Ended")
    await _broadcast({
        "type": "simulation_end",
        "discussion_id": discussion_id,
        "topic": topic,
        "total_rounds": max_rounds,
    })

    return [item for item in history if not (item.get("role") == "user" and item.get("name") == "user")]
