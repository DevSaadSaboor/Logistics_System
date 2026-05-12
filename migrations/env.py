import os

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

from app.core.database import Base

from app.modules.audit.model import AuditLog
from app.modules.tenants.models import Tenant
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.shipments.models import (
    ShipmentStatus,
    Shipment_Staus_log,
)

# -----------------------------------
# Alembic Config
# -----------------------------------
config = context.config

# -----------------------------------
# Read DB URL from environment
# -----------------------------------
db_url = (
    os.getenv("SYNC_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or ""
).strip()
print("SYNC_DATABASE_URL =", os.getenv("SYNC_DATABASE_URL"))
print("DATABASE_URL =", os.getenv("DATABASE_URL"))
if not db_url:
    raise RuntimeError(
        "Database URL is not configured. "
        "Set SYNC_DATABASE_URL or DATABASE_URL."
    )

# -----------------------------------
# Convert async driver -> sync driver
# Alembic must use psycopg2
# -----------------------------------
def _alembic_sync_url(url: str) -> str:
    u = url.strip()
    if u.startswith("postgres://"):
        u = "postgresql://" + u[len("postgres://") :]
    if u.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg2://" + u[len("postgresql+asyncpg://") :]
    if u.startswith("postgresql://"):
        return "postgresql+psycopg2://" + u[len("postgresql://") :]
    return u


sync_db_url = _alembic_sync_url(db_url)


print("ALEMBIC USING:", sync_db_url)

# Override alembic.ini URL
config.set_main_option(
    "sqlalchemy.url",
    sync_db_url
)

# -----------------------------------
# Logging
# -----------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------------
# Metadata
# -----------------------------------
target_metadata = Base.metadata


# -----------------------------------
# Offline migrations
# -----------------------------------
def run_migrations_offline() -> None:

    context.configure(
        url=sync_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# -----------------------------------
# Online migrations
# -----------------------------------
def run_migrations_online() -> None:

    connectable = create_engine(
        sync_db_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# -----------------------------------
# Entrypoint
# -----------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()