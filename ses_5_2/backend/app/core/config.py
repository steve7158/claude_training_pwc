from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Carta Healthcare"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://carta:carta@postgres:5432/carta"
    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    encryption_key: str = "iAmA32ByteFernetKeyPlaceholder0="

    # Groq (free-tier) is the LLM extraction backend - see app/services/extraction_engine.py.
    # Env var is GROQ_API (not GROQ_API_KEY) to match how it's provided.
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API")
    groq_model: str = Field(default="openai/gpt-oss-120b", validation_alias="GROQ_MODEL")

    storage_root: str = "/data/documents"

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

    rate_limit_per_minute: int = 1000


settings = Settings()
