from fastapi import APIRouter, Depends,Header,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.users.schema import LoginRequest,LoginResponse,UserResponse,RegisterRequest
from app.modules.users.service import UserService
from .dependencies import get_auth_service
router = APIRouter(prefix="/auth", tags=["auth"])


# service = UserService()


@router.post("/register")

async def register(
    payload:RegisterRequest,
    tenant_slug : str = Header(..., alias="X-Tenant-Slug"),
    service:UserService =Depends(get_auth_service) 
):
    try:
        user = await service.register_user(
            tenant_slug=tenant_slug,
            email= payload.email,   
            password = payload.password,
            role = payload.role,
        )
        return {"message": "User register successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=400 , detail=str(e))

@router.post("/login")

async def login(
    payload : LoginRequest,
    tenant_slug : str = Header(..., alias="X-Tenant-Slug"),
    service:UserService =Depends(get_auth_service) 
):
    try:
        user = await service.login_user(
            tenant_slug=tenant_slug,
            email = payload.email,
            password = payload.password
        )
        return user
    except ValueError:
        raise HTTPException(status_code=400 , detail="Invalid Credentials")
        
