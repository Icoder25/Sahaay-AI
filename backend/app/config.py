"""Typed runtime configuration. Optional integrations fail closed."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus, urlparse

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = BACKEND_ROOT / "static" / "audio"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = ""
    cors_origins: str = "http://localhost:3000"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_db_password: str = ""
    supabase_db_host: str = "aws-0-ap-northeast-1.pooler.supabase.com"
    supabase_db_port: int = 6543

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-5"
    exa_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    enable_voice: bool = False

    firebase_credentials_json: str = ""
    firebase_project_id: str = ""
    redis_url: str = ""
    celery_always_eager: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.supabase_db_password and self.supabase_url:
            project_ref = (urlparse(self.supabase_url).hostname or "").split(".", 1)[0]
            if project_ref:
                return (
                    f"postgresql+psycopg://postgres.{project_ref}:"
                    f"{quote_plus(self.supabase_db_password)}@{self.supabase_db_host}:"
                    f"{self.supabase_db_port}/postgres"
                )
        return f"sqlite:///{BACKEND_ROOT / 'sahaay.db'}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def uses_supabase_postgres(self) -> bool:
        return self.resolved_database_url.startswith("postgresql")

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
