from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API keys (automatically loaded)
    gemini_api_key: str | None = None
    grok_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # WhatsApp / Evolution API
    whatsapp_api_key: str | None = None
    whatsapp_instance_url: str | None = None
    whatsapp_instance_name: str = "main"
    whatsapp_recipient: str | None = None # The phone number or Group JID to talk to
    
    # --- PHASE 5: AIML API (Universal Aggregator) ---
    aiml_api_key: str | None = None
    aiml_api_base: str = "https://ai.aimlapi.com"
    
    # Storage
    # Using a local directory within the project for easier auditing during development
    data_dir: Path = Path("./.orch_data")
    agents_file: Path = Path("./.orch_data/agents.json")

settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
