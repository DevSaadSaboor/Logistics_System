from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_tenant, require_tenant_roles
from app.core.logging import logger
from app.modules.users.models import UserRole
from app.modules.shipments.ai_service import ShipmentAiService
from .schema import (
    ShipmentCreate,
    ShipmentResponse,
    UpdateShipmentStatus,
    SimilarShipmentResponse,
)
from .service import ShipmentsService

router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.patch("/{shipment_id}/status")
async def update_shipment(
    shipment_id: UUID,
    payload: UpdateShipmentStatus,
    tenant=Depends(get_current_tenant),
    user=Depends(
        require_tenant_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ShipmentsService(db)

    shipment = await service.update_status(
        shipment_id=shipment_id,
        tenant_id=tenant.id,
        new_status=payload.status,
        user_id=user.id,
    )

    logger.info(
        "shipment.status.updated shipment_id=%s tenant_id=%s user_id=%s new_status=%s",
        shipment.id,
        tenant.id,
        user.id,
        payload.status,
    )

    return shipment


@router.post("/", response_model=ShipmentResponse)
async def create_shipment(
    payload: ShipmentCreate,
    background_tasks: BackgroundTasks,
    tenant=Depends(get_current_tenant),
    user=Depends(
        require_tenant_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
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
        description=payload.description,
        user_id=user.id,
    )

    ai_service = ShipmentAiService(db)

    background_tasks.add_task(
        ai_service.categorizer_and_update_shipment,
        shipment.id,
        tenant.id,
        payload.description,
    )

    logger.info(
        "shipment.created shipment_id=%s tenant_id=%s user_id=%s",
        shipment.id,
        tenant.id,
        user.id,
    )

    return shipment


@router.post("/{shipment_id}/categorize")
async def categorize_shipment(
    shipment_id: UUID,
    background_tasks: BackgroundTasks,
    tenant=Depends(get_current_tenant),
    user=Depends(
        require_tenant_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ShipmentsService(db)

    shipment = await service.get_tenant_shipment_or_raise(
        shipment_id=shipment_id,
        tenant_id=tenant.id,
    )

    ai_service = ShipmentAiService(db)

    background_tasks.add_task(
        ai_service.categorizer_and_update_shipment,
        shipment.id,
        tenant.id,
        shipment.description,
    )

    logger.info(
        "shipment.categorization.started shipment_id=%s tenant_id=%s user_id=%s",
        shipment.id,
        tenant.id,
        user.id,
    )

    return {"message": "categorization started"}


@router.get("/{shipment_id}/category")
async def get_category_result(
    shipment_id: UUID,
    tenant=Depends(get_current_tenant),
    user=Depends(
        require_tenant_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ShipmentsService(db)

    shipment = await service.get_tenant_shipment_or_raise(
        shipment_id=shipment_id,
        tenant_id=tenant.id,
    )

    return {
        "shipment_id": shipment.id,
        "category": shipment.category,
        "confidence": shipment.confidence,
        "ai_processed": shipment.ai_processed,
        "ai_processed_at": shipment.ai_processed_at,
    }


@router.get(
    "/{shipment_id}/similar",
    response_model=list[SimilarShipmentResponse],
)
async def similar_shipments(
    shipment_id: UUID,
    min_similarity: float = 0.7,
    limit: int = 5,
    offset: int = 0,
    tenant=Depends(get_current_tenant),
    user=Depends(
        require_tenant_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ShipmentsService(db)

    result = await service.get_similar_shipment(
        shipment_id=shipment_id,
        tenant_id=tenant.id,
        min_similarity=min_similarity,
        limit=limit,
        offset=offset,
    )

    return result


@router.get("/track/{tracking_number}")
async def track_shipment(
    tracking_number: str,
    db: AsyncSession = Depends(get_db),
):
    service = ShipmentsService(db)

    return await service.get_by_tracking_number(tracking_number)