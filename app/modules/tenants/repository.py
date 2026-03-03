from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.tenants.models import Tenant

class TenantRepository:
    async def create(self,db:AsyncSession, name:str,slug:str):
        tenant = Tenant(
            name = name,
            slug=slug
        )
        db.add(tenant)
        return tenant
    

    async def get_all(self,db:AsyncSession):
        result = await db.execute(select(Tenant).where(Tenant.deleted_at.is_(None)))
        return result.scalars().all()

    async def get_by_slug(self,db:AsyncSession,slug:str):
        result = await db.execute(select(Tenant).where(Tenant.slug == slug).where(Tenant.deleted_at.is_(None)))
        return result.scalars().first()
        
    async def get_by_name(self, db:AsyncSession,name:str):
        result = await db.execute(select(Tenant).where(Tenant.name == name).where(Tenant.deleted_at.is_(None)))
        return result.scalars().first()
    
    async def get_by_id(self,db:AsyncSession,tenant_id):
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id).where(Tenant.deleted_at.is_(None)))
        return result.scalars().first()
    