from fastapi import APIRouter, Depends, HTTPException
from typing import List
# from app.core.database import get_db
from .schema import TenantCreate,TenantResponse
from .service import TenantService
from .dependencies import get_auth_service
from app.core.dependencies import require_roles
from app.modules.users.models import UserRole
from app.core.logging import logger
router = APIRouter(prefix="/tenants", tags=["Tenants"])

# repo = TenantRepository()

# service = TenantService()

@router.post("/", response_model= TenantResponse )
async def create_tenant(
    payload:TenantCreate,
    current_user=Depends(require_roles(UserRole.ADMIN)),
    service: TenantService = Depends(get_auth_service)
):
    try:
        tenant = await service.create_tenant(payload.name)
        return tenant
    except ValueError as error:
        logger.warning(
            "tenant.create.failed user_id=%s name=%s reason=%s",
            getattr(current_user, "id", None),
            payload.name,
            str(error),
        )
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        logger.exception(
            "tenant.create.error user_id=%s name=%s",
            getattr(current_user, "id", None),
            payload.name,
        )
        raise

@router.get("/", response_model= List[TenantResponse])
async def list_tenants(
    current_user=Depends(require_roles(UserRole.ADMIN)),
    service: TenantService = Depends(get_auth_service)
):
    tenant = await service.list_tenants()
    return tenant

@router.delete("/{tenant_id}", response_model=TenantResponse)
async def delete_tenant(
    tenant_id:str,
    current_user=Depends(require_roles(UserRole.ADMIN)),
    service: TenantService = Depends(get_auth_service)
):
    try:
        tenant = await service.soft_delete(tenant_id)
        return tenant
    except ValueError as error:
        logger.warning(
            "tenant.delete.failed user_id=%s tenant_id=%s reason=%s",
            getattr(current_user, "id", None),
            tenant_id,
            str(error),
        )
        if str(error) == "Tenant not found":
            raise HTTPException(status_code=404, detail="Tenant not found")
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        logger.exception(
            "tenant.delete.error user_id=%s tenant_id=%s",
            getattr(current_user, "id", None),
            tenant_id,
        )
        raise
