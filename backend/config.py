"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Eye of Horus: Sparks"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-in-production"
    vertical: str = "sparks"

    # Claude
    claude_api_key: str = ""
    claude_model: str = "claude-opus-4-7-20250514"

    # External APIs
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    openweather_api_key: str = ""
    ticketmaster_key: str = ""

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # Simulation defaults
    default_agent_count: int = 10000
    max_simulation_seconds: int = 600
    claude_sample_agents_per_tick: int = 10

    # Database (optional)
    database_url: str = "sqlite:///./eye_of_horus.db"
    redis_url: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
