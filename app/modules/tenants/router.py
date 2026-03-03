from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.tenants.repository import TenantRepository
from .schema import TenantCreate,TenantResponse
from .service import TenantService
router = APIRouter(prefix="/tenants", tags=["Tenants"])

repo = TenantRepository()

service = TenantService()

@router.post("/", response_model= TenantResponse )
async def create_tenant( payload:TenantCreate, db:AsyncSession = Depends(get_db)):
    tenant = await service.create_tenant(db,payload.name)
    return tenant

@router.get("/", response_model= List[TenantResponse])
async def list_tenants(db:AsyncSession = Depends(get_db)):
    tenant = await service.list_tenants(db)
    return tenant

@router.delete("/{tenant_id}", response_model=TenantResponse)
async def delete_tenant(tenant_id:str, db:AsyncSession = Depends(get_db)):
    tenant = await service.soft_delete(db,tenant_id)
    return tenant
