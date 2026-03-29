from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .agent_manager import load_agents, Agent
from .llm import call_ai, call_structured_huddle
from .database import SessionLocal, CouncilSession, NeuralRound, CognitiveBlock, Mentor, get_or_create_mentor, init_db, engine
from .bridge import bridge
import time
import asyncio
import re
import uuid
import requests
import json

# Absolute Relational Init
init_db()

console = Console()

def broadcast_to_gui(data: dict):
    """Push update to the GUI API via broadcast endpoint."""
    try:
        requests.post("http://localhost:8000/broadcast", json=data, timeout=0.1)
    except:
        pass 

def run_simulated_discussion(topic: str, agent_ids: list[str], max_rounds: int = 10, whatsapp_mode: bool = False):
    db = SessionLocal()
    agents = load_agents()
    selected = [agents[a] for a in agent_ids if a in agents]

    if not selected:
        console.print("[red]No agents configured![/red]")
        return

    # 1. INITIALIZE SESSION
    new_session = CouncilSession(title=topic)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    console.print(Panel(f"[bold blue]AGI COMMAND CENTER – Audit Mode Enabled[/bold blue]\nSession ID: [cyan]{new_session.id}[/cyan]\nTopic: [italic]{topic}[/italic]", title="🚀 RELATIONAL RECONSTRUCTION ACTIVE"))

    student_id = "orch"
    
    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]── ROUND {round_num} DELIBERATION ──────────[/bold yellow]")
        
        # 2. CREATE ROUND
        new_round = NeuralRound(session_id=new_session.id, round_number=round_num)
        db.add(new_round)
        db.commit()
        db.refresh(new_round)

        orch_student = next((a for a in selected if a.id == student_id), selected[0])
        mentors = [a for a in selected if a.id != orch_student.id]

        # 3. STUDENT (ORCH) GRILLING
        prompt = f"Topic: {topic}\nExplain the core conflict in current AGI scaling logic. What is the 'Final Paradox'?"
        broadcast_to_gui({"type": "thinking", "agent": orch_student.id, "round": round_num})
        
        # Student Thinking
        console.print(f"[bold magenta][ORCH (Student)][/bold magenta] theorizing...", end=" ")
        # Using the new (reasoning, response) tuple
        s_reasoning, s_response = call_ai(orch_student, prompt)
        
        # Save Student Block
        s_mentor_idx = get_or_create_mentor(db, orch_student.id, "Student")
        s_block = CognitiveBlock(
            id=str(uuid.uuid4()), round_id=new_round.id, mentor_id=s_mentor_idx.id,
            content=s_response, reasoning=s_reasoning, is_student=1
        )
        db.add(s_block)
        db.commit()
        broadcast_to_gui({"type": "response", "agent": orch_student.id, "block_id": s_block.id, "content": s_response, "round": round_num})

        # 4. MENTOR DELIBERATION HUDDLE
        console.print(f"\n[bold cyan]🏛️ Mentors entering the Deliberation Huddle...[/bold cyan]")
        huddle_trace = []
        for m in mentors:
            broadcast_to_gui({"type": "thinking", "agent": m.id, "round": round_num})
            if m.id == "grok":
                proof = call_structured_huddle(m, f"Topic: {topic}\nInquiry: {s_response}")
                huddle_trace.append(f"[GROK_STRUCTURED]: {proof['proposed_synthesis']}")
                console.print(f"[yellow]✓ Grok provided Structured Proof (Confidence: {proof['confidence_score']}%)[/yellow]")
            else:
                m_reasoning, m_reply = call_ai(m, f"Topic: {topic}\nStudent says: {s_response}\nProvide 1 sharp logical correction.")
                huddle_trace.append(f"[{m.id.upper()}]: {m_reply}")
                console.print(f"[cyan]✓ {m.id.upper()} contributed expertise.[/cyan]")
        
        # 5. MASTER SYNTHESIS GATE (HUMAN INPUT)
        full_huddle = "\n".join(huddle_trace)
        console.print(Panel(full_huddle, title="📡 COUNCIL HUDDLE PROOF"))
        
        console.print("\n[bold green]MASTER SYNTHESIS REQUIRED[/bold green]")
        console.print("Provide the final '2 cents' for ORCH (or type 'auto' to synthesize):")
        user_input = input(">> ").strip()
        
        if user_input.lower() == "auto":
             synthesis_prompt = f"Huddle Trace:\n{full_huddle}\nTopic: {topic}\nProvide the final consolidated lesson for ORCH."
             _, final_lesson = call_ai(mentors[0], synthesis_prompt)
        else:
             final_lesson = user_input

        # Save Synthesis Block (Attributed to Master/Moderator)
        m_rec = get_or_create_mentor(db, "Master_Synthesis", "Human/Guide")
        synth_block = CognitiveBlock(
            id=str(uuid.uuid4()), round_id=new_round.id, mentor_id=m_rec.id,
            content=final_lesson, reasoning="Forensic User Input", is_student=0
        )
        db.add(synth_block)
        db.commit()
        
        broadcast_to_gui({"type": "response", "agent": "Master_Synthesis", "block_id": synth_block.id, "content": final_lesson, "round": round_num})
        
        # 6. ORCH FINAL REFLECTION (DEEP REASONING)
        console.print(f"\n[bold magenta][ORCH][/bold magenta] absorbing the Master Synthesis...", end=" ")
        final_prompt = f"Master Synthesis: {final_lesson}\nTopic: {topic}\nExplain what you have learned and how it evolves your internal Goal Consistency."
        
        f_reasoning, f_response = call_ai(orch_student, final_prompt)
        
        # Save Final Block
        f_block = CognitiveBlock(
            id=str(uuid.uuid4()), round_id=new_round.id, mentor_id=s_mentor_idx.id,
            content=f_response, reasoning=f_reasoning, is_student=1
        )
        db.add(f_block)
        db.commit()
        
        console.print(f"\n[bold blue]ORCH REPORT:[/bold blue] {f_response}")
        broadcast_to_gui({"type": "response", "agent": orch_student.id, "block_id": f_block.id, "content": f_response, "reasoning": f_reasoning, "round": round_num})

    db.close()
    console.print(Panel(f"[bold green]✓ Session #{new_session.id} Hierarchically Archived[/bold green]", title="✅ END"))
