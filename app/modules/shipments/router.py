from .schema import ShipmentCreate, ShipmentResponse
from .service import ShipmentsService
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.shipments.ai_service import ShipmentAiService
from app.core.dependencies import get_current_tenant, get_current_user
from .repository import ShipmentRespository

router = APIRouter(prefix="/shipments", tags=["Shipments"])



@router.post("/", response_model=ShipmentResponse)
async def create_shipment(
    payload : ShipmentCreate,
    background_tasks:BackgroundTasks,
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
        pickup_date=payload.pickup_date,
        delivery_date= payload.delivery_date,
        description= payload.description,
        user_id=user.id
    )
    background_tasks.add_task(
        service.run_ai_categorization,
        shipment.id,
        payload.description
    )
    return shipment

@router.post("/{shipment_id}/categorize")
async def categorize_shipment(
    shipment_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant = Depends(get_current_tenant)
):
    # Fetch shipment first to get the description needed for AI categorization
    repo = ShipmentRespository(db)
    shipment = await repo.get_by_id(shipment_id)
    if not shipment or shipment.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Shipment not found")

    ai_service = ShipmentAiService(db)
    background_tasks.add_task(
        ai_service.categorizer_and_update_shipment,
        shipment_id,
        tenant.id,
        shipment.description  # Fixed: description was missing
    )
    return {"message": "categorization started"}

@router.get("/{shipment_id}/category")
async def get_category_result(
    shipment_id: int,
    db: AsyncSession = Depends(get_db),
    tenant = Depends(get_current_tenant)
):
    repo = ShipmentRespository(db)  # Fixed: was missing db argument
    shipment = await repo.get_by_id(shipment_id)
    if not shipment or shipment.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return {
        "shipment_id": shipment.id,
        "category": shipment.category,
        "confidence": shipment.confidence,
        "ai_processed": shipment.ai_processed,
        "ai_processed_at": shipment.ai_processed_at
    }


@router.get("/track/{tracking_number}")  # Fixed: was /shipments/track/... causing double prefix
async def track_shipment(
    tracking_number: str,
    db: AsyncSession = Depends(get_db)
):
    service = ShipmentsService(db)
    return await service.get_by_tracking_number(tracking_number)


    
   






