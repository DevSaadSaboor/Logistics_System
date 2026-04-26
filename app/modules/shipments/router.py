from .schema import ShipmentCreate, ShipmentResponse,UpdateShipmentStatus,SimilarShipmentResponse
from .service import ShipmentsService
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.shipments.ai_service import ShipmentAiService
from app.core.dependencies import get_current_tenant, get_current_user
from .repository import ShipmentRespository
from uuid import UUID

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.patch("/{shipment_id}/status")

async def update_shipment(
    shipment_id: UUID,
    payload: UpdateShipmentStatus,
    tenant =Depends(get_current_tenant),
    user = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    service = ShipmentsService(db)
    shipment = await service.update_status(
        shipment_id=shipment_id,
        tenant_id=tenant.id,
        new_status=payload.status,
        user_id=user.id
    )
    return shipment


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
        description= payload.description,
        user_id=user.id
    )
    ai_service = ShipmentAiService(db)
    background_tasks.add_task(
        ai_service.categorizer_and_update_shipment,
        shipment.id,
        tenant.id,
        payload.description
    )
    return shipment


@router.post("/{shipment_id}/categorize")
async def categorize_shipment(
    shipment_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant = Depends(get_current_tenant)
):

    repo = ShipmentRespository(db)
    shipment = await repo.get_by_id(shipment_id)
    if not shipment or shipment.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Shipment not found")

    ai_service = ShipmentAiService(db)
    background_tasks.add_task(
        ai_service.categorizer_and_update_shipment,
        shipment_id,
        tenant.id,
        shipment.description
    )
    return {"message": "categorization started"}

@router.get("/{shipment_id}/category")
async def get_category_result(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant = Depends(get_current_tenant)
):
    repo = ShipmentRespository(db) 
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

@router.get("/{shipment_id}/similar", response_model=list[SimilarShipmentResponse])
async def similar_shipments(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(get_current_tenant),
    min_similarity = 0.7,
    limit = 5,
    offset = 0
):
    service = ShipmentsService(db)

    result = await service.get_similar_shipment(
        shipment_id,
        tenant.id,
        min_similarity,
        limit,
        offset
    )

    return result

@router.get("/track/{tracking_number}") 
async def track_shipment(
    tracking_number: str,
    db: AsyncSession = Depends(get_db)
):
    service = ShipmentsService(db)
    return await service.get_by_tracking_number(tracking_number)


    
   






