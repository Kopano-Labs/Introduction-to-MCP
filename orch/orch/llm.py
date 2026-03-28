from litellm import completion
from .agent_manager import Agent
from .config import settings

def call_ai(agent: Agent, prompt: str, temperature: float = 0.7) -> str:
    """Single unified call via LiteLLM"""
    model_map = {
        "gemini": "gemini/gemini-1.5-pro",
        "grok": "xai/grok-4-1-fast",
        "xai": "xai/grok-4-1-fast",
        "copilot": "openai/gpt-4o",
        "openai": "openai/gpt-4o",
        "anthropic": "anthropic/claude-3-5-sonnet-20241022",
    }
    model = model_map.get(agent.provider.lower(), agent.model)
    
    # Check for AIML/Third-party providers with custom base URLs
    api_base = None
    if agent.provider.lower() == "aiml":
        model = f"openai/{agent.model}"
        api_base = settings.aiml_api_base

    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_key=agent.api_key,
        api_base=api_base,
        temperature=temperature,
        max_tokens=4096, # Increased for deep reasoning
    )
    return response.choices[0].message.content.strip()
