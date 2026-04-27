from fastapi import APIRouter, Depends, Header

from app.modules.users.schema import LoginRequest, RegisterRequest
from app.modules.users.service import UserService
from .dependencies import get_auth_service
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
    payload: LoginRequest,
    tenant_slug: str = Header(..., alias="X-Tenant-Slug"),
    service: UserService = Depends(get_auth_service),
):
    result = await service.login_user(
        tenant_slug=tenant_slug,
        email=payload.email,
        password=payload.password,
    )

    logger.info(
        "auth.login.success tenant_slug=%s email=%s",
        tenant_slug,
        payload.email,
    )

    return result   