"""
Phase 2: Moderator AI Logic
This module contains the Moderator AI responsible for managing discussion flow
and summarizing rounds in the MCP orchestration.
"""
from typing import List, Dict
from litellm import completion, acompletion
from rich.console import Console

from .agent_manager import Agent, load_agents

console = Console()

MODERATOR_PROMPT = """
You are the Moderator of a council of AI agents. Your role is to ensure the discussion remains productive, on-topic, and insightful.
You will be given the discussion topic and the recent conversation history.
Your tasks are:
1. Briefly summarize the key points, agreements, and disagreements from the last round of conversation.
2. Identify any tangents, repetitive loops, or missed opportunities.
3. Provide a clear, concise, and neutral prompt for the NEXT agent to address. This prompt should steer the conversation in a more productive direction, challenge the agents, or introduce a new angle to the topic.

Your output must be ONLY the new prompt for the next agent. Do not include your summary or analysis in the final output. Be direct and focused.
"""

class Moderator:
    """
    The Moderator AI manages the flow of conversation between agents.
    """
    def __init__(self, agent_id: str):
        """
        Initializes the Moderator.

        Args:
            agent_id: The ID of the agent to be used as the moderator (e.g., 'claude-3-haiku-20240307' or 'gpt-4o').
                      This agent must be configured via `orch agents config`.
        """
        agents = load_agents()
        if agent_id not in agents:
            raise ValueError(f"Moderator agent '{agent_id}' not found. Please configure it using 'orch agents config'.")
        self.agent: Agent = agents[agent_id]
        console.log(f"🤖 Moderator initialized using agent: [bold cyan]{self.agent.id}[/] ({self.agent.model})")

    async def amoderate(self, topic: str, history: List[Dict[str, str]]) -> str:
        """
        Analyzes the conversation history and generates a new prompt to guide the discussion asynchronously.
        """
        formatted_history_for_moderator = "\n".join([
            f"[{msg.get('name', msg.get('role'))}]: {msg['content']}"
            for msg in history
        ])

        user_prompt_for_moderator = f"Discussion Topic: {topic}\n\nConversation History:\n{formatted_history_for_moderator}"

        messages = [
            {"role": "system", "content": MODERATOR_PROMPT},
            {"role": "user", "content": user_prompt_for_moderator}
        ]

        try:
            console.log(f"Moderator [bold cyan]{self.agent.id}[/] is thinking...")
            response = await acompletion(
                model=self.agent.model,
                messages=messages,
                api_key=self.agent.api_key,
            )
            new_direction = response.choices[0].message.content.strip()
            console.log(f"Moderator generated new direction: \"{new_direction[:70]}...\"")
            return new_direction
        except Exception as e:
            console.log(f"🚨 [bold red]Moderator failed to generate a response:[/] {e}")
            return f"Please continue the discussion on {topic}."

    def moderate(self, topic: str, history: List[Dict[str, str]]) -> str:
        """
        Analyzes the conversation history and generates a new prompt to guide the discussion.
        Args:
            topic: The main topic of the discussion.
            history: A list of message dictionaries representing the entire conversation.
        Returns:
            A new prompt string for the next agent.
        """
        # Format the full history for the moderator's context.
        # We need to be careful here. The moderator's prompt already defines its role.
        # The 'history' should be presented as the 'Conversation History' for the moderator to analyze.
        formatted_history_for_moderator = "\n".join([
            f"[{msg.get('name', msg.get('role'))}]: {msg['content']}"
            for msg in history
        ])

        user_prompt_for_moderator = f"Discussion Topic: {topic}\n\nConversation History:\n{formatted_history_for_moderator}"

        messages = [
            {"role": "system", "content": MODERATOR_PROMPT},
            {"role": "user", "content": user_prompt_for_moderator}
        ]

        try:
            console.log(f"Moderator [bold cyan]{self.agent.id}[/] is thinking...")
            response = completion(
                model=self.agent.model, # Assumes agent.model is the full litellm model string
                messages=messages,
                api_key=self.agent.api_key,
            )
            new_direction = response.choices[0].message.content.strip()
            console.log(f"Moderator generated new direction: \"{new_direction[:70]}...\"")
            return new_direction
        except Exception as e:
            console.log(f"🚨 [bold red]Moderator failed to generate a response:[/] {e}")
            # Fallback to a simple prompt if the moderator fails
            return f"Please continue the discussion on {topic}."