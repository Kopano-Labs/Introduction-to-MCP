from litellm import completion
from .agent_manager import Agent
from .config import settings
from google import genai
from google.genai import types
import json

def call_ai(agent: Agent, prompt: str, temperature: float = 0.7) -> tuple[str, str]:
    """Unified entry point. Returns (reasoning, response)"""
    
    # SPECIAL CASE: Gemini 3.1 High-Thinking SDK
    if agent.provider.lower() == "gemini":
        try:
            return call_gemini_thinking(agent, prompt)
        except Exception as e:
            # Fallback to standard 3.1 if thinking preview fails
            print(f"High-Thinking Model failed: {str(e)}. Falling back to standard Gemini 3.1.")
            resp = call_ai_litellm(agent, prompt, temperature)
            return "Thinking fallback active.", resp
            
    # Standard LiteLLM logic (does not separate CoT unless prompted, so we use internal parse)
    resp = call_ai_litellm(agent, prompt, temperature)
    return "", resp

def call_ai_litellm(agent: Agent, prompt: str, temperature: float = 0.7) -> str:
    """Standard LiteLLM logic for Gemini 3 migration."""
    model_map = {
        "gemini": "gemini/gemini-3.1-pro-preview", 
        "grok": "xai/grok-4-1-fast",
        "xai": "xai/grok-4-1-fast",
        "copilot": "openai/gpt-4o",
        "openai": "openai/gpt-4o",
        "anthropic": "anthropic/claude-3-5-sonnet-20241022",
    }
    model = model_map.get(agent.provider.lower(), agent.model)
    
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
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def call_gemini_thinking(agent: Agent, prompt: str) -> tuple[str, str]:
    """Uses google-genai SDK to explicitly separate thoughts from answer."""
    client = genai.Client(api_key=agent.api_key)
    model_id = "gemini-3.1-pro-preview" 
    
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
            include_thoughts=True # ABSOLUTE REQUIREMENT FOR REASONING TRACE
        ),
        tools=[
            types.Tool(url_context=types.UrlContext()),
            types.Tool(code_execution=types.ToolCodeExecution),
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
    )
    
    thoughts = []
    answers = []
    
    # Streaming as per master blueprint
    for chunk in client.models.generate_content_stream(
        model=model_id,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
        config=config,
    ):
        if chunk.candidates and chunk.candidates[0].content.parts:
            for part in chunk.candidates[0].content.parts:
                if getattr(part, 'thought', False): # Catch reasoning blocks
                    thoughts.append(part.text)
                elif part.text: # Catch final answer
                    answers.append(part.text)
            
    return "".join(thoughts).strip(), "".join(answers).strip()

def call_structured_huddle(agent: Agent, prompt: str) -> dict:
    """Calls Grok with response_format for structured deliberation."""
    try:
        huddle_schema = {
            "type": "object",
            "properties": {
                "logical_steps": {"type": "array", "items": {"type": "string"}},
                "conflicts_detected": {"type": "array", "items": {"type": "string"}},
                "proposed_synthesis": {"type": "string"},
                "confidence_score": {"type": "integer", "minimum": 0, "maximum": 100}
            },
            "required": ["logical_steps", "conflicts_detected", "proposed_synthesis", "confidence_score"]
        }

        response = completion(
            model="xai/grok-2", 
            messages=[{"role": "user", "content": prompt}],
            api_key=agent.api_key,
            response_format={ "type": "json_object", "json_schema": huddle_schema }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "logical_steps": ["System Fatigue Trace"],
            "conflicts_detected": [f"Error: {str(e)}"],
            "proposed_synthesis": "I advocate for a foundational revisit of the Scaling Paradox.",
            "confidence_score": 0
        }
