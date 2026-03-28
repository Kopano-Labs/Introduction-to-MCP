import litellm
from litellm import completion
from .agent_manager import Agent

def call_ai(agent: Agent, prompt: str, temperature: float = 0.7) -> str:
    """Single unified call via LiteLLM"""
    model_map = {
        "gemini": "gemini/gemini-1.5-pro",
        "grok": "xai/grok-2-1212",
        "copilot": "openai/gpt-4o",
        "openai": "openai/gpt-4o",
        "anthropic": "anthropic/claude-3-5-sonnet-20241022",
    }
    model = model_map.get(agent.provider.lower(), agent.model)

    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_key=agent.api_key,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
