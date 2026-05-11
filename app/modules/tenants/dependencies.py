from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import authenticate_access_token_user
from app.modules.users.models import User, UserRole

from .repository import TenantRepository
from .service import TenantService

_optional_bearer = HTTPBearer(auto_error=False)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> TenantService:
    return TenantService(db)


async def require_create_tenant_actor(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
) -> Optional[User]:
    """First active tenant may be created without a token (bootstrap). After that, admin JWT is required."""
    tenant_repo = TenantRepository(db)
    if await tenant_repo.count_active() == 0:
        return None
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Bearer token required. Create the first tenant without auth, "
                "then register an admin user and use their access token for more tenants."
            ),
        )
    user = await authenticate_access_token_user(db, credentials.credentials)
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: only admin users can create tenants",
        )
    return user


