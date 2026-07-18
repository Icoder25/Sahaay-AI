from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = BACKEND_ROOT / "static" / "audio"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""
    exa_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel default
    claude_model: str = "claude-sonnet-4-5"
    enable_voice: bool = True
    database_url: str = f"sqlite:///{BACKEND_ROOT / 'sahaay.db'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
