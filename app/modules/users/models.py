import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String,Enum,DateTime,func,ForeignKey
from app.modules.tenants.models import Tenant
from datetime import datetime   
from sqlalchemy import Index
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
import enum



class UserRole(enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(Base):
    tenant = relationship("Tenant", back_populates="users")
    __tablename__ = "users"

    __table_args__ = (
        Index(
            "uq_users_tenant_email_active",
            "tenant_id",
            "email",
            unique=True,
            postgresql_where=expression.text("deleted_at IS NULL"),
        ),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id : Mapped[uuid.UUID] = mapped_column(
      UUID(as_uuid=True),
      ForeignKey("tenants.id"),
      nullable=False
      
    )
    email : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    hashed_password : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role : Mapped[UserRole] = mapped_column(
        Enum(UserRole, name = "user_role_enum"),nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default= func.now(),
        nullable=False
    )
    deleted_at : Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime, 
        server_default= func.now(),
        onupdate= func.now(),
        nullable=False
    )
    
    last_login_at : Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=True
    )

