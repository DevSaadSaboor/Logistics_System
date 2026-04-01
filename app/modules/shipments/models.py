import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String,Enum,DateTime,func,ForeignKey,Float
from app.modules.tenants.models import Tenant
from datetime import datetime   
from sqlalchemy import Index
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from .enum import ShipmentStatus
from sqlalchemy.dialects.postgresql import UUID


class Shipments(Base):
    __tablename__ = "shipments"

    __table_args__ = (
        Index(
            "Shipment_tracking_number",
            "tracking_number",
            unique=True
        ),
    )
    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid= True),
        primary_key=True,
        default=uuid.uuid4
    )    
    tenant_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False
    )

    status : Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus),
        nullable=False
    )
    tracking_number : Mapped[str] = mapped_column(
        String(255),
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
        nullable=True
    )
    delivery_date : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    weight : Mapped[float] = mapped_column(
        Float,
        nullable= False
    )
    update_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default = func.now(),
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
        nullable=False
    )

