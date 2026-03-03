from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.sql import func


class TimeStampMixIn:
    create_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    update_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default= func.now(),
        onupdate=func.now(),
        nullable=False
    )

    deleted_at : Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )