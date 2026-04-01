"""
Phase 2: Configuration & Environment Handling
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Pydantic Settings for secure configuration management."""
    google_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    db_path: str = "db/datalake.db"

    class Config:
        env_file = ".env"

settings = Settings()