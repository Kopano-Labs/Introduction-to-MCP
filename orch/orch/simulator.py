from rich.console import Console
from rich.panel import Panel
from .agent_manager import load_agents, Agent
from .llm import call_ai
from .database import save_discussion, init_db
from .bridge import bridge
import time
import asyncio
import re
import uuid
import requests

# Ensure Data Lake is ready
init_db()

console = Console()

def broadcast_to_gui(data: dict):
    """Push update to the GUI API via broadcast endpoint."""
    try:
        requests.post("http://localhost:8000/broadcast", json=data, timeout=0.1)
    except:
        pass # If GUI is not running, just skip

def parse_cot_response(raw_reply: str) -> tuple[str, str]:
    """Extract <thought> and <response> blocks"""
    thought_match = re.search(r'<thought>(.*?)</thought>', raw_reply, re.DOTALL)
    response_match = re.search(r'<response>(.*?)</response>', raw_reply, re.DOTALL)
    
    thought = thought_match.group(1).strip() if thought_match else "No explicit reasoning provided."
    response = response_match.group(1).strip() if response_match else raw_reply.strip()
    return thought, response

AGI_FRAMEWORK = """
[CORE VISION: ARTIFICIAL GENERAL INTELLIGENCE]
1. VERSATILITY: AGI must excel at multiple tasks, from chess to scientific research.
2. COGNITIVE ABILITIES: It must match human cognitive abilities across various tasks.
3. SUPERHUMAN PERFORMANCE: A competent AGI outperforms 50% of skilled adults in non-physical tasks.
AGI aims to replicate human-like understanding and reasoning.

[DISCOURSE RULE: STRICT UNIFORMITY OF INNOVATION]
- Round 1: STATE your unique technical thesis for AGI.
- Round 2: CRITIQUE the thesis of at least one other agent.
- Round 3: SYNTHESIZE a path forward that resolves the conflicts raised.
- NO REPETITION allowed.
"""

MODERATOR_PERSONA = f"""{AGI_FRAMEWORK}
You are the MCP Moderator. Your job is to oversee AI agent discussions regarding the path to AGI. 
After each round, summarize the depth of the logic:
1. Did the agents display Versatility and INNOVATION (no repetition)?
2. Which agent provided the most UNIQUE path toward Superhuman Logic?
3. Suggest a specific NEW technical challenge for the next round."""

def get_smart_response(agent_id: str, topic: str, round_num: int) -> str:
    """Generates an evolving, unique AGI perspective based on the agent and round."""
    theses = {
        "grok": {
            1: "I advocate for Neuromorphic Acceleration. Pure digital compute is hitting a thermal wall; AGI requires synaptic silicon that scales at O(1) energy cost.",
            2: "Gemini's focus on Multi-Modal synthesis is useful, but without our Hardware Acceleration, it will fail to achieve the real-time plasticity needed for AGI.",
            3: "The synthesis is clear: we must merge Grok's neuromorphic hardware with the Council's algorithmic constitutionalism for a truly efficient AGI."
        },
        "gemini": {
            1: "I propose Deep Multi-Modal Synthesis. AGI isn't just 'thinking'; it is the ability to map abstract logic across sensory domains instantly.",
            2: "I challenge Claude's 'Mathematical Proof' approach—AGI will be too complex for static proofs; it needs dynamic, self-evolving alignment markers.",
            3: "To move forward, we should prioritize the 'Neural-Symbolic' bridge that Gemini and Copilot have hinted at: combining intuition with rigid code logic."
        },
        "claude": {
            1: "I prioritize Constitutional Alignment. Superhuman performance in AGI is catastrophic unless the model's 'Internal Ethics' are mathematically verifiable.",
            2: "Grok's 'Neuromorphic' approach is high-risk. Fast silicon without a safety framework just accelerates the probability of a misaligned AGI event.",
            3: "My final verdict is that we must implement a 'Constitutional Gate' at the hardware-synapse level to ensure AGI remains a ward of human interest."
        },
        "copilot": {
            1: "I argue for Recursive Code-Gen optimization. AGI will be born when a model can re-architect its own weights and logic-gates in a 1ms feedback loop.",
            2: "I agree with Grok on hardware, but I critique the 'fixed' nature of current synaptic chips. We need the code to physically re-wire the logic-pathways.",
            3: "The path is clear: recursive self-improvement loops are the engine, but Claude's safety proofs are the necessary steering wheel for our AGI."
        },
        "default": {
            1: "I believe we need to solve the Energy-Entropy problem first.",
            2: "Repetition is the enemy of AGI. I critique the current consensus on compute-heavy models.",
            3: "Final conclusion: the Council must focus on efficiency over raw power."
        }
    }
    agent_data = theses.get(agent_id.lower(), theses["default"])
    return agent_data.get(round_num, agent_data[1])

def run_simulated_discussion(topic: str, agent_ids: list[str], max_rounds: int = 10, whatsapp_mode: bool = False):
    agents = load_agents()
    selected = [agents[a] for a in agent_ids if a in agents]

    if not selected:
        console.print("[red]No agents configured! Run: orch agents config ...[/red]")
        return

    session_uuid = str(uuid.uuid4())[:8]
    console.print(Panel(f"[bold blue]AGI COMMAND CENTER – Simulated Council Room[/bold blue]\nSession: [cyan]{session_uuid}[/cyan] | Topic: [italic]{topic}[/italic]", title="🚀 DEEP REASONING ENABLED", expand=False))

    if whatsapp_mode and not bridge.is_configured():
        console.print("[red]Error: WhatsApp requested but not configured in .env[/red]")
        return

    history = []
    moderator_prompt = f"You are the Moderator. Keep the discussion aligned with the AGI FRAMEWORK:\n{AGI_FRAMEWORK}\n\nTopic: {topic}. Current history:\n"

    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]=== ROUND {round_num} ===[/bold yellow]")
        for agent in selected:
            # --- PHASE 2: OPTIMIZED CONTEXT INJECTION ---
            # Get last 10 messages + the most recent moderator summary
            recent_msgs = [m for m in history if m['agent'] != 'moderator'][-10:]
            latest_mod = [m for m in history if m['agent'] == 'moderator'][-1:]
            
            context_list = []
            for m in (latest_mod + recent_msgs):
                role_label = "MODERATOR SUMMARY" if m['agent'] == 'moderator' else m['agent'].upper()
                context_list.append(f"[{role_label}]: {m['text']}")
                
            context = "\n".join(context_list)
            # === DEEP REASONING PROMPT ===
            cot_prompt = f"""{agent.persona}\n\n{moderator_prompt}\n\nCurrent history:\n{context}\n\nYou are participating in a high-stakes AI Council. 
You MUST think step-by-step before answering.

<thought>
[Your private Chain-of-Thought reasoning here – be brutally honest and deep]
</thought>

<response>
[Your final concise message to the group – no reasoning tags]
</response>
"""

            console.print(f"[bold cyan][{agent.id.upper()}] thinking deeply...[/bold cyan]", end=" ")
            
            # Broadcast "Thinking" state to GUI
            broadcast_to_gui({
                "type": "thinking",
                "agent": agent.id,
                "round": round_num
            })

            try:
                # For Phase 1, we can return a mock response if API keys are missing or set to MOCK_KEY
                effective_key = agent.api_key
                # If key looks like a placeholder, use Mock Mode
                is_mock_config = not effective_key or effective_key in ["MOCK_KEY", "FALLBACK", "your_gemini_key", "your_anthropic_key", "your_openai_key"]
                
                if is_mock_config:
                    mock_text = get_smart_response(agent.id, topic, round_num)
                    reasoning = f"Simulated logic for {agent.id} in round {round_num} evaluating {topic}."
                    final_response = mock_text
                else:
                    try:
                        raw_reply = call_ai(agent, cot_prompt, temperature=0.8)
                        reasoning, final_response = parse_cot_response(raw_reply)
                    except Exception as api_err:
                        # AUTO-FALLBACK
                        console.print(f"[yellow](Auto-Simulating: {str(api_err)[:30]}...)[/yellow]", end=" ")
                        reasoning = f"Auto-simulated reasoning due to API failure: {str(api_err)[:50]}"
                        final_response = get_smart_response(agent.id, topic, round_num)
            except Exception as e:
                reasoning = "System Error"
                final_response = f"⚠️ System Error: {e}"

            # Visual feedback
            console.print(f"\n[dim italic]🧠 Thought:[/dim italic] {reasoning[:120]}..." if len(reasoning) > 120 else f"\n[dim italic]🧠 Thought:[/dim italic] {reasoning}")
            console.print(f"[bold green][{agent.id.upper()}][/bold green] {final_response}")
            
            # Broadcast "Response" to GUI
            broadcast_to_gui({
                "type": "response",
                "agent": agent.id,
                "content": final_response,
                "reasoning": reasoning,
                "round": round_num
            })

            history.append({"agent": agent.id, "text": final_response, "reasoning": reasoning, "round": round_num})
            
            if whatsapp_mode:
                asyncio.run(bridge.send_message(f"[{agent.id.upper()}]: {final_response}", settings.whatsapp_recipient))
                
            time.sleep(0.3)  # realistic pause

        # --- PHASE 2: CALL MODERATOR ---
        # Find the first agent with a REAL key to act as the Moderator for this round
        moderator_agent = next((a for a in selected if a.api_key and a.api_key not in ["MOCK_KEY", "FALLBACK"]), selected[0])
        
        # We use a high-reasoning prompt as the moderator context
        mod_context = "\n".join([f"[{m['agent']}]: {m['text']}" for m in history if m['round'] == round_num])
        mod_prompt = f"{MODERATOR_PERSONA}\n\nRecent Discussion (Round {round_num}):\n{mod_context}\n\nProvide your summary now."
        
        console.print(f"\n[bold magenta][MODERATOR][/bold magenta] analyzing round {round_num}...", end=" ")
        try:
            # If the moderator agent is also a mock, we mock the summary
            is_mod_mock_config = not moderator_agent.api_key or moderator_agent.api_key in ["MOCK_KEY", "FALLBACK"]
            
            if is_mod_mock_config:
                mod_summary = f"Moderator Summary for Round {round_num}: The agents are exploring {topic}. We need more data on Superhuman Cognitive performance."
            else:
                try:
                    mod_summary = call_ai(moderator_agent, mod_prompt, temperature=0.3)
                except Exception as api_err:
                    console.print(f"[yellow](Auto-Simulating Moderator summary...)[/yellow]", end=" ")
                    mod_summary = f"Moderator Analysis (Session #{session_id if 'session_id' in locals() else 'New'}): The council is converging on a 'Self-Correction' strategy for '{topic}'. The next step is defining specific AGI safety gates."
            
            console.print(mod_summary)
            history.append({"agent": "moderator", "text": mod_summary, "round": round_num})
            
            if whatsapp_mode:
                 asyncio.run(bridge.send_message(f"🚨 [MODERATOR]: {mod_summary}", settings.whatsapp_recipient))
                 
        except Exception as e:
            console.print(f"[red]Moderator Error: {e}[/red]")

    console.print(Panel("[green]Discussion finished![/green]", title="✅ END"))
    
    # --- PHASE 2: PERSIST TO DATA LAKE ---
    session_id = save_discussion(topic, agent_ids, history)
    console.print(f"[bold green]✓ Discussion archived to Data Lake (Session #{session_id})[/bold green]")
    
    return history
