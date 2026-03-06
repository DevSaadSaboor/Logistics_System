from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .service import UserService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)