from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Intervue API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    # Default is Postgres. If Postgres is unavailable or sqlite is requested, fallback logic handles it.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/intervue_db"
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./intervue.db"

    # LLM Settings
    # provider options: "auto", "gemini", "groq", "ollama", "mock"
    LLM_PROVIDER: str = "auto"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
