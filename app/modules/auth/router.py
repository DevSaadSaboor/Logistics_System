from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from .schema import RefreshTokenRequest
from .service import AuthService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_tenant
from app.modules.users.service import UserService
from .dependencies import get_auth_service
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me")
async def get_me(current_user = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    UserService(db)
    return {
        "id": current_user.id,
        "email" : current_user.email,
        "role" : current_user.role.value
    }
    
@router.post("/refresh", response_model=None)
async def refresh_token(
    payload: RefreshTokenRequest,
    tenant = Depends(get_current_tenant),
    service: AuthService = Depends(get_auth_service)
):


    tokens = await service.refresh_access_token(
        refresh_token=payload.refresh_token,
        tenant_id=tenant.id
    )

    return tokens