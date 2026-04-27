from datetime import datetime, timezone, timedelta

from app.modules.tenants.repository import TenantRepository
from app.modules.auth.repository import RefreshTokenRespsitory
from .respository import UserRepository

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)

from app.core.logging import logger

from app.core.exceptions import (
    TenantNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)


class UserService:
    def __init__(self, db):
        self.db = db
        self.repo = UserRepository(db)
        self.tenant_repo = TenantRepository(db)
        self.refresh_repo = RefreshTokenRespsitory(db)

    async def register_user(self, tenant_slug, email, password, role):
        normalized_email = email.strip().lower()

        tenant = await self.tenant_repo.get_by_slug(tenant_slug)

        if not tenant:
            logger.warning(
                "user.register.tenant_not_found tenant_slug=%s",
                tenant_slug,
            )
            raise TenantNotFoundError()

        existing_user = await self.repo.get_by_email_and_tenant(
            tenant.id,
            normalized_email,
        )

        if existing_user:
            logger.warning(
                "user.register.conflict tenant_id=%s email=%s",
                tenant.id,
                normalized_email,
            )
            raise UserAlreadyExistsError()

        password_hash = hash_password(password)

        user = await self.repo.create(
            tenant.id,
            normalized_email,
            password_hash,
            role,
        )

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(
            "user.register.success tenant_id=%s email=%s",
            tenant.id,
            normalized_email,
        )

        return user

    async def login_user(self, tenant_slug, email, password):
        normalized_email = email.strip().lower()

        tenant = await self.tenant_repo.get_by_slug(tenant_slug)

        if not tenant:
            logger.warning(
                "auth.login.tenant_not_found tenant_slug=%s",
                tenant_slug,
            )
            raise InvalidCredentialsError()

        user = await self.repo.get_by_email_and_tenant(
            tenant.id,
            normalized_email,
        )

        if not user:
            logger.warning(
                "auth.login.user_not_found tenant_id=%s email=%s",
                tenant.id,
                normalized_email,
            )
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            logger.warning(
                "auth.login.invalid_password tenant_id=%s email=%s",
                tenant.id,
                normalized_email,
            )
            raise InvalidCredentialsError()

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "tenant_id": str(user.tenant_id),
                "role": user.role.value,
            }
        )

        refresh_token = create_refresh_token()
        token_hash = hash_refresh_token(refresh_token)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        await self.refresh_repo.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        user.last_login_at = datetime.now(timezone.utc)

        await self.db.commit()

        logger.info(
            "auth.login.success tenant_id=%s user_id=%s",
            tenant.id,
            user.id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "tenant_id": user.tenant_id,
            },
        }