from typing import Optional

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import authenticate_access_token_user
from app.modules.users.models import User, UserRole

from .repository import TenantRepository
from .service import TenantService


_optional_bearer = HTTPBearer(auto_error=False)


def _extract_bearer_token(request: Request) -> Optional[str]:
    """Manually extract Bearer token from Authorization header (never raises)."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer "):].strip() or None
    return None


def get_auth_service(db: AsyncSession = Depends(get_db)) -> TenantService:
    return TenantService(db)


async def _require_admin_bearer(
    db: AsyncSession,
    token: Optional[str],
    *,
    action: str,
) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                f"Bearer token required to {action}. "
                "During bootstrap, create the first tenant without auth, "
                "register an admin via POST /auth/register (X-Tenant-Slug), "
                "then use the login access token."
            ),
        )
    user = await authenticate_access_token_user(db, token)
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: only admin users can {action}",
        )
    return user


async def require_create_tenant_actor(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: Optional[HTTPAuthorizationCredentials] = Security(_optional_bearer),
) -> Optional[User]:
    """First tenant only: no bearer when there are zero active tenants; after that, admin JWT.
    
    The Security(_optional_bearer) parameter exists solely to register the HTTPBearer
    security scheme in OpenAPI so Swagger UI sends the Authorization header.
    The actual token is extracted manually from the request to avoid auto_error issues.
    """
    tenant_repo = TenantRepository(db)
    if await tenant_repo.count_active() == 0:
        return None
    token = _extract_bearer_token(request)
    return await _require_admin_bearer(db, token, action="create tenants")

