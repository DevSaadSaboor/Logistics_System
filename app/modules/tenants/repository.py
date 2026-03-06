from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.tenants.models import Tenant

class TenantRepository:
     def __init__(self,db:AsyncSession):
        self.db = db


     async def create(self, name:str,slug:str):
        tenant = Tenant(
            name = name,
            slug=slug
        )
        self.db.add(tenant)
        return tenant
    

     async def get_all(self,):
        result = await self.db.execute(select(Tenant).where(Tenant.deleted_at.is_(None)))
        return result.scalars().all()

     async def get_by_slug(self,slug:str):
          query = select(Tenant).where(Tenant.slug == slug)
          result = await self.db.execute(query)
          return result.scalar_one_or_none()
    
     async def get_by_name(self,name:str):
        result = await self.db.execute(select(Tenant).where(Tenant.name == name).where(Tenant.deleted_at.is_(None)))
        return result.scalars().first()
    
     async def get_by_id(self,tenant_id):
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id).where(Tenant.deleted_at.is_(None)))
        return result.scalars().first()
    