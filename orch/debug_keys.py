import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

def test_provider(name, model, key_name):
    key = os.environ.get(key_name)
    if not key or "your_" in key:
        print(f"❌ {name}: No key in .env or placeholder found.")
        return
    
    try:
        print(f"📡 Testing {name} ({model})...", end=" ", flush=True)
        response = completion(
            model=model,
            messages=[{"role": "user", "content": "hello"}],
            api_key=key,
            max_tokens=10
        )
        print(f"✅ SUCCESS: {response.choices[0].message.content.strip()[:20]}...")
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}")

print("--- 🛰️ COUNCIL FLASH AUDIT v4: Full Roster ---")
test_provider("xAI / Grok", "xai/grok-2", "XAI_API_KEY")
test_provider("Anthropic / Claude", "anthropic/claude-3-haiku-20240307", "ANTHROPIC_API_KEY")
test_provider("OpenAI / GPT", "openai/gpt-4o-mini", "OPENAI_API_KEY")
test_provider("Copilot / GPT-4", "openai/gpt-4", "OPENAI_API_KEY")
test_provider("Gemini / Flash", "gemini/gemini-1.5-flash-latest", "GEMINI_API_KEY")
