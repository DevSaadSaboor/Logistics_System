from fastapi import APIRouter, Depends, Header,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.users.schema import LoginRequest, RegisterRequest
from app.modules.users.service import UserService
from .dependencies import get_auth_service
from app.modules.audit.service import AuditService
from app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    payload: RegisterRequest,
    tenant_slug: str = Header(..., alias="X-Tenant-Slug"),
    service: UserService = Depends(get_auth_service),
):
    await service.register_user(
        tenant_slug=tenant_slug,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )

    logger.info(
        "user.register.success tenant_slug=%s email=%s",
        tenant_slug,
        payload.email,
    )

    return {"message": "User registered successfully"}


@router.post("/login")
async def login(
    request:Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    tenant_slug: str = Header(..., alias="X-Tenant-Slug"),
    service: UserService = Depends(get_auth_service),
):
    result = await service.login_user(
        tenant_slug=tenant_slug,
        email=payload.email,
        password=payload.password,
    )

    await AuditService(db).log(

        action="user.login",

        resource_type="user",

        resource_id=str(result["user"]["id"]),

        user_id=result["user"]["id"],

        tenant_id=result["user"]["tenant_id"],

        ip_address=request.client.host,

        user_agent=request.headers.get("User-Agent"),

        metadata_json={
            "email": payload.email,
            "tenant_slug": tenant_slug,
        },
    )

    logger.info(
        "auth.login.success tenant_slug=%s email=%s",
        tenant_slug,
        payload.email,
    )

    return result   