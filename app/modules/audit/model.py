from sqlalchemy import String,Integer,DateTime,ForeignKey,JSON
from sqlalchemy.orm import Mapped,MappedColumn
from datetime import datetime,timezone
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id : Mapped[int] = MappedColumn(
        Integer,
        primary_key = True,
        index = True
    )

    user_id : Mapped[int | None]  = MappedColumn(
        ForeignKey("users.id"),
        nullable = True,
    )
    tenant_id : Mapped[int | None] = MappedColumn(
        ForeignKey("tenants.id"),
        nullable = True
    )
    action: Mapped[str] = MappedColumn (
        String,
        nullable = False
    )
    resource_type :Mapped[str] = MappedColumn (
        String,
        nullable = False
    )
    resource_id : Mapped[str] = MappedColumn (
        String,
        nullable = False
    )
    ip_address : Mapped[str] = MappedColumn (
        String,
        nullable = False
    )
    user_agent : Mapped[str]  = MappedColumn (
        String,
        nullable = False
    )
    metadata_json : Mapped[dict | None] = MappedColumn (
        JSON,
        nullable = True
    )
    created_at: Mapped[datetime] = MappedColumn (
        DateTime(timezone=True),
        default = datetime.now(timezone.utc)
    )