from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # -----------------------------------
    # Database
    # -----------------------------------
    DATABASE_URL: str | None = None
    SYNC_DATABASE_URL: str | None = None

    # -----------------------------------
    # Security
    # -----------------------------------
    SECRET_KEY: str

    # -----------------------------------
    # OpenAI
    # -----------------------------------
    OPENAI_API_KEY: str

    # -----------------------------------
    # JWT
    # -----------------------------------
    REFRESH_TOKEN_EXPIRE_DELTA: timedelta = timedelta(days=7)

    class Config:
        env_file = ".env"


settings = Settings()