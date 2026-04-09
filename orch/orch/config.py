"""
Phase 2: Configuration & Environment Handling
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
import os
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import Optional

# Configuration paths
AGENTS_FILE = Path.home() / ".orch" / "agents.json"

class Settings(BaseSettings):
    """Pydantic Settings for secure configuration management."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    db_path: str = "db/datalake.db"

    # WhatsApp Integration (Phase 3)
    whatsapp_api_key: Optional[str] = None
    whatsapp_instance_url: Optional[str] = None
    whatsapp_instance_name: str = "main"
    whatsapp_recipient: Optional[str] = None # Default recipient JID

    # KasiLink bridge / Hack Day integration
    kasilink_frontend_url: Optional[str] = None
    kasilink_backend_url: Optional[str] = None
    clerk_secret_key: Optional[str] = None
    clerk_jwks_url: Optional[str] = None
    eskom_api_token: Optional[str] = None
    loadshedding_provider_url: Optional[str] = None
    orch_public_url: Optional[str] = None

    # Microsoft / Azure demo readiness
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_app_service_name: Optional[str] = None
    azure_container_app_name: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    azure_ai_search_endpoint: Optional[str] = None
    azure_ai_search_key: Optional[str] = None
    azure_ai_search_index_name: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_app_insights_connection_string: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "AZURE_APP_INSIGHTS_CONNECTION_STRING",
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
        ),
    )

    # Braintrust Integration (Phase 5)
    braintrust_api_key: Optional[str] = None
    braintrust_project_id: Optional[str] = None
    braintrust_default_project: Optional[str] = None
    braintrust_base_url: str = "https://api.braintrust.dev"
    braintrust_events_path: Optional[str] = None

    # Observation Braintrust Integration (Phase 6)
    observation_braintrust_api_key: Optional[str] = None
    observation_braintrust_project_id: Optional[str] = None
    observation_braintrust_base_url: Optional[str] = None
    observation_braintrust_events_path: Optional[str] = None

    # Team activity watcher
    dev_watch_owner: str = "DEV_3 (Background)"
    dev_watch_path: str = ".orch_data/dev_watch/dev3_activity.jsonl"
    dev_watch_comms_path: str = ".orch_data/dev_watch/dev3_communications.jsonl"
    dev_watch_session_rules_path: str = ".orch_data/session_logs/session_rules.md"

settings = Settings()
