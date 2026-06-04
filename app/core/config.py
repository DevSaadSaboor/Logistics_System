from datetime import timedelta

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # -----------------------------------
    # Database
    # -----------------------------------
    DATABASE_URL: str | None = None
    SYNC_DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", "SYNC_DATABASE_URL", mode="before")
    @classmethod
    def strip_empty_db_urls(cls, v: object) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v  # type: ignore[return-value]

    # -----------------------------------
    # Security
    # -----------------------------------
    SECRET_KEY: str

    # -----------------------------------
    # OpenAI (optional — AI routes degrade gracefully without it)
    # -----------------------------------
    OPENAI_API_KEY: str | None = None

    # -----------------------------------
    # App
    # -----------------------------------
    APP_ENV: str = "development"
    DEBUG: bool = False

    # -----------------------------------
    # JWT
    # -----------------------------------
    REFRESH_TOKEN_EXPIRE_DELTA: timedelta = timedelta(days=7)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.strip().lower() == "production"

    class Config:
        env_file = ".env"


settings = Settings()