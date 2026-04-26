import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.core.base import TimeStampMixIn    
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression



class Tenant(TimeStampMixIn,Base):
    users = relationship("User", back_populates="tenant")
    __tablename__ = "tenants"

    __table_args__ = (
    Index(
        "uq_tenant_name_active",
        "slug",
        unique=True,
        postgresql_where=expression.text("deleted_at IS NULL"),
    ),
)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name : Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )