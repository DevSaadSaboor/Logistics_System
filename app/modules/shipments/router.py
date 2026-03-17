from .schema import ShipmentCreate
from .service import ShipmentsService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_tenant, get_current_user
from .dependencies import get_auth_service
router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.post("/")

async def create_shipment(
    payload : ShipmentCreate,
    tenant = Depends(get_current_tenant),
    user = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):

    service = ShipmentsService(db)

    shipment = await service.create_shipment(
        tenant_id=tenant.id,
        origin=payload.origin,
        destination=payload.destination,
        weight=payload.weight,
        recipient_name=payload.recipient_name,
        recipient_phone=payload.recipient_phone,
        delivery_address=payload.delivery_address,
        user_id=user.id
    )
    return shipment



