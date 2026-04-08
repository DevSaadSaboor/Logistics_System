import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Enum, DateTime, func, ForeignKey, Float, Boolean, Index
from datetime import datetime
from .enum import ShipmentStatus


class Shipments(Base):
    __tablename__ = "shipments"

    __table_args__ = (
        Index("ix_shipments_tenant_status", "tenant_id", "status"),
        Index("ix_shipment_tenant_created_at", "tenant_id", "created_at")
    )
    
    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid= True),
        primary_key=True,
        default=uuid.uuid4
    )    
    tenant_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        index = True,
        nullable=False
    )

    status : Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus),
        nullable=False
    )
    tracking_number : Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    
    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default= func.now(),
        nullable= False
    )
    origin : Mapped[str] = mapped_column(
        String(255),
        nullable= False
    )
    destination : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description : Mapped[str] = mapped_column(
        String(255), 
        nullable=False)
    
    recipient_name  :Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    recipient_phone : Mapped[str] = mapped_column(
        String(50),
        nullable= False
    )
    delivery_address : Mapped[str] = mapped_column (
        String(255),
        nullable= False
    )
    pickup_date : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    delivery_date : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    weight : Mapped[float] = mapped_column(
        Float,
        nullable= False
    )
    updated_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable = False,
        default="other"
    )
    confidence : Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )
    ai_processed : Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    ai_processed_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    assign_driver_id :  Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.id"),
        nullable=True
    )

class Shipment_Staus_log(Base):
    __tablename__ = "shipments_status_log"

    id  : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key=True,
        nullable= False,
        default=uuid.uuid4
    )
    shipment_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid= True),
        ForeignKey("shipments.id"),
        nullable=False
    )
    status : Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus),
        nullable= False
    )
    timestamp : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default= func.now(),
        onupdate=func.now(),
        nullable=False
    )
    location : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    updated_by_user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.id"),
        nullable=True 
    )

