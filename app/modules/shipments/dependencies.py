from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .service import ShipmentsService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> ShipmentsService:
    return ShipmentsService(db)

