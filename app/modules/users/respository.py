from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User


class UserRepository:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create(self,tenant_id,email,hashed_password,role):
        user = User(tenant_id = tenant_id,email = email,hashed_password=hashed_password,role=role)
        self.db.add(user)
        return user


    async def get_by_id(self,user_id):
        result = await self.db.execute(select(User).where(User.id == user_id).where(User.deleted_at.is_(None)))
        return result.scalars().first()


    async def get_by_email_and_tenant(self,tenant_id,email):
        result = await self.db.execute(select(User).where(User.tenant_id == tenant_id).where(User.email == email).where(User.deleted_at.is_(None)))
        return result.scalars().first()