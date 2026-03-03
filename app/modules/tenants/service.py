from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.utility import generate_slug
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.models import Tenant
from datetime import datetime,timezone


class TenantService:

    def __init__(self):
        self.repo = TenantRepository()
    
    
    async def create_tenant(self,db:AsyncSession,name:str):
        normalized_name = name.strip().lower()
        slug = normalized_name.replace(" ", "-")
        existing =  await self.repo.get_by_name(db,slug)
        if existing:
            raise ValueError("Tenant with this name already exists") 
        tenant =  await self.repo.create(db,normalized_name,slug)
        await db.commit()
        await db.refresh(tenant)

        return tenant
        
    
 

    async def list_tenants(self, db: AsyncSession):
        return await self.repo.get_all(db)
    
    
    async def soft_delete(self,db:AsyncSession,tenant_id):
        tenant = await self.repo.get_by_id(db,tenant_id)
        if not tenant:
            raise ValueError("Tenant not found")
        tenant.deleted_at = datetime.now(timezone.utc)  
        await db.commit()
        await db.refresh(tenant)
        return tenant


    












    