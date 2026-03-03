from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# Base class for all models
class Base(DeclarativeBase):
    pass


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # shows SQL queries in terminal (good for learning)
)


# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session



# 1️⃣ engine

# The engine knows:

# Where the database is

# Which driver to use (asyncpg)

# It does NOT run queries itself.

# 2️⃣ AsyncSessionLocal

# This is a factory.

# Every request:

# Creates a session

# Talks to DB

# Closes automatically

# 3️⃣ get_db()

# This is what FastAPI will use:

# db: AsyncSession = Depends(get_db)

# And FastAPI will:

# Open session

# Inject it

# Close it automatically