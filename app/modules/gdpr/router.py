from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_tenant_user
from app.modules.users.models import UserRole
from app.modules.gdpr.services import GDPRService

router = APIRouter(prefix="/gdpr", tags=["GDPR"])

@router.delete("/users/{user_id}/data")
async def erase_user_data(user_id:UUID,current_user = Depends(get_current_tenant_user), db:AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can erase user data",
        )
    service = GDPRService(db)

    result = await service.erase_user_data(user_id = user_id, performed_by=current_user.id,)

    return result