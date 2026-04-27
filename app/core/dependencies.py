from fastapi import Depends, HTTPException,Header,status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import UserRole


from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.logging import logger
from app.modules.users.respository import UserRepository
from app.modules.tenants.repository import TenantRepository

security = HTTPBearer()

async def get_current_user(credentials:HTTPAuthorizationCredentials = Depends(security),db :AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        logger.warning("auth.failed token_decode_failed")
        raise HTTPException(status_code=401, detail="Unauthorized: invalid access token")
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("auth.failed token_missing_subject")
        raise HTTPException(status_code=401, detail="Unauthorized: invalid access token")
    user = await repo.get_by_id(user_id)
    if not user:
        logger.warning("auth.failed user_not_found_for_token user_id=%s", user_id)
        raise HTTPException(status_code=401, detail="Unauthorized: invalid access token")
    return user

async def get_current_tenant( db: AsyncSession = Depends(get_db),tenant_slug:str = Header(...,alias="X-Tenant-Slug")):
    tenant_repo = TenantRepository(db)
    tenant = await tenant_repo.get_by_slug(tenant_slug)
    if tenant is None:
        logger.warning("tenant.resolve_failed slug=%s", tenant_slug)
        raise HTTPException(status_code=404, detail="Tenant not found for provided X-Tenant-Slug")
    return tenant

def require_roles(*allowed_roles):
    def checker(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            allowed = [role.value if hasattr(role, "value") else str(role) for role in allowed_roles]
            current = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
            logger.warning(
                "authz.forbidden role_mismatch user_id=%s current_role=%s allowed_roles=%s",
                current_user.id,
                current,
                ",".join(allowed),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: insufficient role permissions"
            )
        return current_user

    return checker

async def get_current_tenant_user(
    current_user=Depends(get_current_user),
    tenant=Depends(get_current_tenant),
):
    if current_user.tenant_id != tenant.id:
        logger.warning(
            "authz.forbidden tenant_mismatch user_id=%s user_tenant_id=%s request_tenant_id=%s",
            current_user.id,
            current_user.tenant_id,
            tenant.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: user does not belong to requested tenant"
        )
    return current_user

def require_tenant_roles(*allowed_roles: UserRole):
    def checker(current_user=Depends(get_current_tenant_user)):
        if current_user.role not in allowed_roles:
            allowed = [role.value if hasattr(role, "value") else str(role) for role in allowed_roles]
            current = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
            logger.warning(
                "authz.forbidden tenant_role_mismatch user_id=%s current_role=%s allowed_roles=%s",
                current_user.id,
                current,
                ",".join(allowed),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: insufficient role permissions"
            )
        return current_user
    return checker


