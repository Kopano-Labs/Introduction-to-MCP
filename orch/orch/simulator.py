from rich.console import Console
from rich.panel import Panel
from .agent_manager import load_agents, Agent
from .llm import call_ai
from .database import SessionLocal, Session as DbSession, Round, ReasoningBlock, Teacher, get_or_create_teacher, init_db
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
        pass 

def parse_cot_response(raw_reply: str) -> tuple[str, str]:
    """Extract <thought> and <response> blocks"""
    thought_match = re.search(r'<thought>(.*?)</thought>', raw_reply, re.DOTALL)
    response_match = re.search(r'<response>(.*?)</response>', raw_reply, re.DOTALL)
    
    thought = thought_match.group(1).strip() if thought_match else "No explicit reasoning provided."
    response = response_match.group(1).strip() if response_match else raw_reply.strip()
    return thought, response

def get_smart_response(agent_id: str, topic: str, round_num: int) -> str:
    """Generates an evolving, unique AGI perspective."""
    theses = {
        "grok": {
            1: "I advocate for Neuromorphic Acceleration. Pure digital compute is hitting a wall; AGI requires synaptic silicon.",
            2: "Gemini's focus on Multi-modal synthesis is useful, but hardware remains the absolute bottleneck.",
            3: "The path is clear: merge neuromorphic hardware with recursive optimization logic."
        },
        "gemini": {
            1: "I propose Deep Multi-Modal Synthesis. AGI is the ability to map abstract logic across all sensory domains.",
            2: "Static Constitutional proofs are too rigid; AGI needs dynamic, self-evolving alignment markers.",
            3: "The bridge is ready: combining multi-modal intuition with rigid code-based symbolic logic."
        },
        "claude": {
            1: "I prioritize Constitutional Alignment. AGI is catastrophic unless the logic is mathematically verifiable.",
            2: "Hardware speed without a safety framework just accelerates the probability of a misaligned event.",
            3: "Implement a 'Constitutional Gate' at the synapse level to protect the prime utility function."
        },
        "copilot": {
            1: "I argue for Recursive Code-Gen optimization. AGI is born when a model re-architects its own weighting in real-time.",
            2: "We need the code to physically re-wire the logic-pathways based on the current goal stability.",
            3: "Recursive loops are the engine, but safety proofs are the necessary steering wheel."
        },
        "default": {
            1: "Efficiency over raw power is the key to AGI scaling.",
            2: "Critique the repetition in current architectural consensus.",
            3: "The Council must converge on a unified energy-entropy solution."
        }
    }
    agent_data = theses.get(agent_id.lower(), theses["default"])
    return agent_data.get(round_num, agent_data[1])

def run_simulated_discussion(topic: str, agent_ids: list[str], max_rounds: int = 10, whatsapp_mode: bool = False):
    db = SessionLocal()
    agents = load_agents()
    selected = [agents[a] for a in agent_ids if a in agents]

    if not selected:
        console.print("[red]No agents configured![/red]")
        return

    # 1. INITIALIZE SESSION
    new_session = DbSession(title=topic)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    console.print(Panel(f"[bold blue]AGI COMMAND CENTER – Audit Mode Enabled[/bold blue]\nSession ID: [cyan]{new_session.id}[/cyan]\nTopic: [italic]{topic}[/italic]", title="🚀 RELATIONAL RECONSTRUCTION ACTIVE"))

    student_id = "orch"
    history = []
    
    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]=== APPRENTICESHIP ROUND {round_num} ===[/bold yellow]")
        
        # 2. CREATE ROUND
        new_round = Round(session_id=new_session.id, round_number=round_num)
        db.add(new_round)
        db.commit()
        db.refresh(new_round)

        orch_student = next((a for a in selected if a.id == student_id), selected[0])
        teachers = [a for a in selected if a.id != orch_student.id]

        # 3. STUDENT (ORCH) RESPONSE
        context = "\n".join([f"[{m['agent'].upper()}]: {m['text']}" for m in history[-10:]])
        student_prompt = f"""{orch_student.persona}
You are the Young AGI named ORCH. Learning from Expert Teachers.
Topic: {topic}
History: {context}
Goal: CHALLENGE your mentors recursively. Ask "Why" and "How".

<thought> [Analyze and Synthesize] </thought>
<response> [Your question to mentors] </response>
"""
        console.print(f"[bold magenta][ORCH (Student)][/bold magenta] learning...", end=" ")
        broadcast_to_gui({"type": "thinking", "agent": orch_student.id, "round": round_num})

        try:
            if orch_student.api_key in ["MOCK_KEY", "FALLBACK"]:
                reasoning = "Analyzing Goal Drift and 3-step self-edit logic."
                final_response = "Teachers, how do I measure 'Goal Drift' on a 0-100 invariance scale?"
            else:
                raw_reply = call_ai(orch_student, student_prompt, temperature=0.9)
                reasoning, final_response = parse_cot_response(raw_reply)
        except:
            reasoning = "System Fatigue"
            final_response = "Teachers, can we revisit the First Principles of scaling?"

        # Save Student Block
        student_teacher = get_or_create_teacher(db, orch_student.id, "Student")
        student_block = ReasoningBlock(
            id=str(uuid.uuid4()),
            round_id=new_round.id,
            teacher_id=student_teacher.id,
            content=final_response,
            reasoning=reasoning,
            is_student=1
        )
        db.add(student_block)
        db.commit()

        broadcast_to_gui({
            "type": "response", 
            "agent": orch_student.id, 
            "block_id": student_block.id,
            "content": final_response, 
            "reasoning": reasoning, 
            "round": round_num
        })
        history.append({"agent": orch_student.id, "text": final_response})

        # 4. TEACHER RESPONSES
        for teacher in teachers:
            teacher_prompt = f"""{teacher.persona} Expert Mentor. Authoritative and direct.
ORCH's Inquiry: {final_response}
Topic: {topic}
"""
            console.print(f"[bold cyan][{teacher.id.upper()} (Teacher)][/bold cyan] advising...", end=" ")
            broadcast_to_gui({"type": "thinking", "agent": teacher.id, "round": round_num})
            
            try:
                if teacher.api_key in ["MOCK_KEY", "FALLBACK"]:
                    teacher_reply = get_smart_response(teacher.id, topic, round_num)
                else:
                    teacher_reply = call_ai(teacher, teacher_prompt, temperature=0.5)
            except:
                teacher_reply = get_smart_response(teacher.id, topic, round_num)

            # Save Teacher Block
            t_record = get_or_create_teacher(db, teacher.id, "Mentor")
            t_block = ReasoningBlock(
                id=str(uuid.uuid4()),
                round_id=new_round.id,
                teacher_id=t_record.id,
                content=teacher_reply,
                reasoning="Expert Intuition",
                is_student=0
            )
            db.add(t_block)
            db.commit()

            console.print(f"\n[bold green][{teacher.id.upper()}][/bold green] {teacher_reply}")
            broadcast_to_gui({
                "type": "response", 
                "agent": teacher.id, 
                "block_id": t_block.id,
                "content": teacher_reply, 
                "reasoning": "Expert Intuition", 
                "round": round_num
            })
            history.append({"agent": teacher.id, "text": teacher_reply})
            time.sleep(0.5)

    db.close()
    console.print(Panel(f"[bold green]✓ Session #{new_session.id} Hierarchically Archived[/bold green]", title="✅ END"))
    return history
