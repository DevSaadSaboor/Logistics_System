import os 
from dotenv import load_dotenv
from datetime import timedelta


# Ensure local `.env` values override any existing OS env vars.
load_dotenv(override=True)

class Settings:
     DATABASE_URL: str = os.getenv("DATABASE_URL")
     SECRET_KEY :str = os.getenv("SECRET_KEY")
     REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=7)
settings = Settings()