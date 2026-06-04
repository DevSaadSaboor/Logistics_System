from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import authenticate_access_token_user
from app.modules.users.models import User, UserRole
from app.modules.users.respository import UserRepository

from .repository import TenantRepository
from .service import TenantService

_optional_bearer = HTTPBearer(auto_error=False)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> TenantService:
    return TenantService(db)


async def _tenant_bootstrap_open(db: AsyncSession) -> bool:
    """No tenants yet, or tenants exist but no users registered (pre-auth bootstrap)."""
    tenant_repo = TenantRepository(db)
    if await tenant_repo.count_active() == 0:
        return True
    user_repo = UserRepository(db)
    return await user_repo.count_active() == 0


async def _require_admin_bearer(
    db: AsyncSession,
    credentials: Optional[HTTPAuthorizationCredentials],
    *,
    action: str,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                f"Bearer token required to {action}. "
                "During bootstrap, create the first tenant without auth, "
                "register an admin via POST /auth/register (X-Tenant-Slug), "
                "then use the login access token."
            ),
        )
    user = await authenticate_access_token_user(db, credentials.credentials)
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: only admin users can {action}",
        )
    return user


async def require_create_tenant_actor(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
) -> Optional[User]:
    """Bootstrap: create tenant without a token until at least one user exists."""
    if await _tenant_bootstrap_open(db):
        return None
    return await _require_admin_bearer(
        db, credentials, action="create tenants"
    )


async def require_list_tenants_actor(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
) -> Optional[User]:
    """Bootstrap: list tenants without a token until at least one user exists (read slug for register)."""
    if await _tenant_bootstrap_open(db):
        return None
    return await _require_admin_bearer(
        db, credentials, action="list tenants"
    )


