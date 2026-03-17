from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from .schema import TenantCreate,TenantResponse
from .service import TenantService
from .dependencies import get_auth_service
router = APIRouter(prefix="/tenants", tags=["Tenants"])

# repo = TenantRepository()

# service = TenantService()

@router.post("/", response_model= TenantResponse )
async def create_tenant( payload:TenantCreate, service: TenantService = Depends(get_auth_service)):
    tenant = await service.create_tenant(payload.name)
    return tenant

@router.get("/", response_model= List[TenantResponse])
async def list_tenants(service: TenantService = Depends(get_auth_service)):
    tenant = await service.list_tenants()
    return tenant

@router.delete("/{tenant_id}", response_model=TenantResponse)
async def delete_tenant(tenant_id:str, service: TenantService = Depends(get_auth_service)):
    tenant = await service.soft_delete(tenant_id)
    return tenant
