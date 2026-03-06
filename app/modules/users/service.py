from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime,timezone,timedelta
from app.modules.tenants.models import Tenant
from app.modules.tenants.repository import TenantRepository
from app.modules.auth.repository import RefreshTokenRespsitory
from .respository import UserRepository
from app.core.security import hash_password,verify_password,create_access_token,create_refresh_token,hash_refresh_token


class UserService():
    def __init__(self,db):
        self.db = db
        self.repo = UserRepository(db)
        self.tenant_repo = TenantRepository(db)
        self.refresh_repo = RefreshTokenRespsitory(db)

    async def register_user(self,tenant_slug,email,password,role):
        normalize_email = email.strip().lower()
        resolve_tenant = await self.tenant_repo.get_by_slug(tenant_slug)
        if not resolve_tenant:
            raise ValueError("Slug not found")
        check_active_user = await self.repo.get_by_email_and_tenant(resolve_tenant.id,normalize_email)
        if check_active_user:
            raise ValueError("user already exist")
        password_hash = hash_password(password)

        user = await self.repo.create(resolve_tenant.id,normalize_email,password_hash,role)

        await self.db.commit()
        await self.db.refresh(user)
        return user
    
  
    async def login_user(self,tenant_slug,email,password):
        email = email.strip().lower()
        resolve_tenant = await self.tenant_repo.get_by_slug(tenant_slug)
        if not resolve_tenant:
            raise ValueError("Invalid credentials")
        
        user = await self.repo.get_by_email_and_tenant(resolve_tenant.id,email)
        if not user:
            raise ValueError("Invalid credentials")
        
        password_verification = verify_password(password, user.hashed_password)
        if not password_verification:
            raise ValueError("Invalid credentials")
        
        token = create_access_token({
            "sub": str(user.id),
            "tenant_id" : str(user.tenant_id),
            "role" : user.role.value
        })

        refresh_token = create_refresh_token()

        token_hash = hash_refresh_token(refresh_token)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        await self.refresh_repo.create(
            user_id=user.id,
            token_hash=  token_hash,
            expires_at= expires_at
        )


        # `users.last_login_at` is TIMESTAMP WITHOUT TIME ZONE, so store naive UTC.
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()
        return {
            "access_token" : token,
            "refresh_toek" : refresh_token,
            "token_type" : "bearer",
            "user" :{
                "id": user.id,
                "email" : user.email,
                "role" : user.role.value,
                "tenant_id" : user.tenant_id
            }
        }
        


    