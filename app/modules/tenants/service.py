from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.utility import generate_slug
from app.modules.tenants.repository import TenantRepository
from datetime import datetime,timezone
from app.core.logging import logger


class TenantService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TenantRepository(db)
    
    
    async def create_tenant(self, name:str):
        normalized_name = name.strip().lower()
        slug = normalized_name.replace(" ", "-")
        existing =  await self.repo.get_by_name(normalized_name)
        if existing:
            logger.warning("tenant.create.conflict name=%s slug=%s", normalized_name, slug)
            raise ValueError("Tenant with this name already exists")
        tenant =  await self.repo.create(normalized_name, slug)
        await self.db.commit()
        await self.db.refresh(tenant)

        return tenant
        
    
 

    async def list_tenants(self):
        return await self.repo.get_all()
    
    
    async def soft_delete(self, tenant_id):
        tenant = await self.repo.get_by_id(tenant_id)
        if not tenant:
            logger.warning("tenant.delete.not_found tenant_id=%s", tenant_id)
            raise ValueError("Tenant not found")
        tenant.deleted_at = datetime.now(timezone.utc)  
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant


    












    