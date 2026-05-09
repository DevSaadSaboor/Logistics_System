from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Text,DateTime
from datetime import datetime

from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    session_id: Mapped[str] = mapped_column(
        String,
        index=True
    )

    role: Mapped[str] = mapped_column(String)

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )