from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)

from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
)

from app.core.config import settings


# -----------------------------------
# Base class for all SQLAlchemy models
# -----------------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------------
# Convert sync PostgreSQL URL
# to asyncpg URL for async SQLAlchemy
# -----------------------------------
def _async_sqlalchemy_url(raw: str) -> str:
    u = raw.strip()
    if u.startswith("postgres://"):
        u = "postgresql://" + u[len("postgres://") :]
    if u.startswith("postgresql+asyncpg://"):
        return u
    if u.startswith("postgresql://"):
        return "postgresql+asyncpg://" + u[len("postgresql://") :]
    return u


DATABASE_URL = None

if settings.DATABASE_URL:
    DATABASE_URL = _async_sqlalchemy_url(settings.DATABASE_URL)

# -----------------------------------
# Engine + Session Factory
# -----------------------------------
engine = None
AsyncSessionLocal = None

if DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # logs SQL queries
    )

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# -----------------------------------
# FastAPI DB Dependency
# -----------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:

    if AsyncSessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------------
# Explanation
# -----------------------------------

# 1️⃣ engine
#
# The engine knows:
#
# - where the database is
# - which driver to use
# - how to connect
#
# It does NOT execute business logic.


# 2️⃣ AsyncSessionLocal
#
# This is a session factory.
#
# Every request:
#
# - creates a DB session
# - performs queries
# - closes automatically


# 3️⃣ get_db()
#
# FastAPI dependency injection:
#
# db: AsyncSession = Depends(get_db)
#
# FastAPI automatically:
#
# - opens session
# - injects it
# - closes it