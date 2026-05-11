import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.modules.tenants.repository import TenantRepository


class TenantService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TenantRepository(db)

    @staticmethod
    def _name_to_slug(normalized_name: str) -> str:
        slug = normalized_name.replace(" ", "-")
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug

    async def create_tenant(self, name: str):
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("Tenant name cannot be empty")
        slug = self._name_to_slug(normalized_name)
        if not slug:
            raise ValueError("Tenant name must contain at least one letter or number")

        existing = await self.repo.get_by_name(normalized_name)
        if existing:
            logger.warning("tenant.create.conflict name=%s slug=%s", normalized_name, slug)
            raise ValueError("Tenant with this name already exists")
        slug_taken = await self.repo.get_by_slug(slug)
        if slug_taken:
            logger.warning("tenant.create.slug_conflict slug=%s", slug)
            raise ValueError("Tenant with this slug already exists")

        tenant = await self.repo.create(normalized_name, slug)
        await self.db.commit()
        await self.db.refresh(tenant)

        return tenant
        
    
 

    async def list_tenants(self):
        return await self.repo.get_all()
    
    
    async def soft_delete(self, tenant_id: UUID):
        tenant = await self.repo.get_by_id(tenant_id)
        if not tenant:
            logger.warning("tenant.delete.not_found tenant_id=%s", tenant_id)
            raise ValueError("Tenant not found")
        tenant.deleted_at = datetime.now(timezone.utc)  
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant


    












    