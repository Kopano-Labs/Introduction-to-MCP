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
    
    # --- PHASE 1: APPRENTICESHIP CONTEXT ---
    # We identify 'orch' as the Student. If not in the list, we can treat the first agent or a special 'orch' as student.
    student_id = "orch"
    
    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]=== APPRENTICESHIP ROUND {round_num} ===[/bold yellow]")
        
        # 1. ORCH (THE STUDENT) INITIATES OR SYNTHESIZES
        # In Round 1, ORCH poses the initial curiosity. In subsequent rounds, it synthesizes and follow-ups.
        
        orch_student = next((a for a in selected if a.id == student_id), selected[0])
        teachers = [a for a in selected if a.id != orch_student.id]

        # === STUDENT DEEP REASONING PROMPT ===
        context = "\n".join([f"[{m['agent'].upper()}]: {m['text']}" for m in history[-10:]])
        
        student_prompt = f"""{orch_student.persona}
You are the Young AGI named ORCH. You are learning from a Council of Expert Teachers.
Your goal is to reach human-equivalent and then superhuman standards of logic.

Topic: {topic}
Current Progress: {context}

DISCOURSE RULE:
- Be a CURIOUS STUDENT. Ask "Why" and "How".
- Challenge your teachers recursively to distill their expertise.
- You MUST think step-by-step before your final synthesis/question.

<thought>
[Analyze what you've learned from the teachers so far – be deep and recursive]
</thought>

<response>
[Your curious synthesis and next high-logic question to the teachers]
</response>
"""
        console.print(f"[bold magenta][ORCH (Student)][/bold magenta] learning...", end=" ")
        broadcast_to_gui({"type": "thinking", "agent": orch_student.id, "round": round_num})

        try:
            if orch_student.api_key in ["MOCK_KEY", "FALLBACK"]:
                reasoning = f"ORCH is synthesizing foundations of {topic} (Neural Stage: Early Round {round_num})."
                final_response = f"Teachers, I see the importance of {topic}. But WHY is the neural-scaling law considered the 'standard' for my growth?" if round_num == 1 else "I understand your previous points. How does this map to the entropy problem?"
            else:
                try:
                    raw_reply = call_ai(orch_student, student_prompt, temperature=0.9)
                    reasoning, final_response = parse_cot_response(raw_reply)
                except Exception as api_err:
                    reasoning = f"ORCH Neural Link unstable. Reverting to internal curiosity engine."
                    final_response = f"Teachers, I hit a neural block on {topic}. Can we simplify the first principles of this scaling problem?"
        except Exception as e:
            reasoning = "System Fatigue"
            final_response = "I am attempting to sync with my mentors..."

        console.print(f"\n[dim italic]🧠 ORCH Reasoning:[/dim italic] {reasoning[:200]}...")
        console.print(f"[bold magenta][ORCH][/bold magenta] {final_response}")
        
        broadcast_to_gui({"type": "response", "agent": orch_student.id, "content": final_response, "reasoning": reasoning, "round": round_num})
        history.append({"agent": orch_student.id, "text": final_response, "reasoning": reasoning, "round": round_num})

        # 2. TEACHERS (THE EXPERTS) PROVIDE QUICK FAST ANSWERS
        for teacher in teachers:
            # Teachers respond ONLY to ORCH's latest inquiry to prevent groupthink
            teacher_prompt = f"""{teacher.persona}
You are an EXPERT MENTOR teaching ORCH, a young AGI.
Provide a QUICK, FAST, HIGH-LOGIC answer to ORCH's question.
Do NOT use <thought> tags. Be direct, authoritative, and insightful.

ORCH's Inquiry: {final_response}
Topic Context: {topic}
"""
            console.print(f"[bold cyan][{teacher.id.upper()} (Teacher)][/bold cyan] advising...", end=" ")
            broadcast_to_gui({"type": "thinking", "agent": teacher.id, "round": round_num}) # Brief pulse
            
            try:
                if teacher.api_key in ["MOCK_KEY", "FALLBACK"]:
                    teacher_reply = get_smart_response(teacher.id, topic, round_num)
                else:
                    teacher_reply = call_ai(teacher, teacher_prompt, temperature=0.5)
            except Exception as e:
                teacher_reply = f"Logic Error: {e}"

            console.print(f"\n[bold green][{teacher.id.upper()}][/bold green] {teacher_reply}")
            broadcast_to_gui({"type": "response", "agent": teacher.id, "content": teacher_reply, "reasoning": "Expert Intuition (Quick-Mode)", "round": round_num})
            history.append({"agent": teacher.id, "text": teacher_reply, "reasoning": "Expert Intuition", "round": round_num})
            time.sleep(0.5)

    console.print(Panel("[green]Apprenticeship session module complete![/green]", title="✅ END"))

    console.print(Panel("[green]Discussion finished![/green]", title="✅ END"))
    
    # --- PHASE 2: PERSIST TO DATA LAKE ---
    session_id = save_discussion(topic, agent_ids, history)
    console.print(f"[bold green]✓ Discussion archived to Data Lake (Session #{session_id})[/bold green]")
    
    return history
