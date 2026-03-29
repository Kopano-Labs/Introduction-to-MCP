import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

key = os.environ.get("GEMINI_API_KEY")

if not key:
    print("No GEMINI_API_KEY found in .env!")
else:
    try:
        client = genai.Client(api_key=key)
        print(f"--- 🛰️ AUTHORIZED GEMINI MODELS FOR KEY: {key[:10]}... ---")
        for model in client.models.list():
            print(f"✓ {model.name}")
    except Exception as e:
        print(f"Failed to list models: {str(e)}")
