"""
Phase 2: Simulation Engine (Round-Robin Logic)
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
from typing import List, Dict, Any
from litellm import completion
from rich.console import Console
from .datalake import start_discussion, log_interaction
from .context import format_history

console = Console()

def run_simulation(topic: str, agents: List[Any], moderator: Any, max_rounds: int) -> List[Dict[str, str]]:
    """
    Executes the round-robin simulation loop between configured agents, 
    guided by the Moderator AI, and logs to the Data Lake.
    """
    console.print(f"[bold green]Starting Simulation:[/] {topic}")
    discussion_id = start_discussion(topic)
    history = []
    
    for round_num in range(1, max_rounds + 1):
        console.print(f"\n[bold yellow]--- Round {round_num} ---[/]")
        
        # Moderator sets the direction
        prompt = moderator.moderate(topic, history)
        log_interaction(discussion_id, "moderator-model", "moderator", None, prompt, "reasoning")
        
        for agent in agents:
            context_messages = format_history(history, prompt)
            
            try:
                response = completion(
                    model=agent.model,
                    messages=context_messages,
                    api_key=getattr(agent, 'api_key', 'MOCK_KEY')
                )
                reply = response.choices[0].message.content.strip()
                
                # Save to shared history
                history.append({"role": "user", "name": agent.id, "content": reply})
                
                # Log execution to Data Lake
                log_interaction(discussion_id, agent.model, agent.id, reply, prompt, "execution")
                
                console.print(f"[bold cyan]{agent.id}:[/] {reply}\n")
                
            except Exception as e:
                console.print(f"[bold red]Error calling {agent.id}: {e}[/]")
                
    console.print("[bold green]Simulation Complete.[/]")
    return history