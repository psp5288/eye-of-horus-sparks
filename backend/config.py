"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Eye of Horus: Sparks"
    vertical: str = "sparks"
    debug: bool = False
    environment: str = "development"

    # Claude / Anthropic
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-opus-4-7"

    # Twitter / X
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None

    # Weather
    weather_api_key: Optional[str] = None

    # Ticketmaster
    ticketmaster_api_key: Optional[str] = None

    # Database
    database_url: str = "sqlite:///./eye_of_horus.db"
    redis_url: str = "redis://localhost:6379"

    # Hackathon
    hackathon_start: str = "2025-04-21"
    hackathon_end: str = "2025-04-26"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
