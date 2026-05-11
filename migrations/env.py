import os

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

from app.core.database import Base

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
# Read database URL from Render env
# -----------------------------------
db_url = os.environ["SYNC_DATABASE_URL"]

print("ALEMBIC USING:", db_url)

# Override alembic.ini URL
config.set_main_option(
    "sqlalchemy.url",
    db_url
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
        url=db_url,
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
        db_url,
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