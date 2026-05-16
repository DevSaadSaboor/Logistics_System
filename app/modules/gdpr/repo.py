from uuid import UUID
from sqlalchemy import delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.audit.model import AuditLog


class GDPRRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    
    async def delete_refresh_tokens(self,user_id:UUID):
        await self.db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))

    
    async def anonymize_audit_log(self,user_id:UUID):
        await self.db.execute(update(AuditLog).where(AuditLog.user_id == user_id).values(user_id = None, metadata_json = {"gdpr_erased":True,},))

    async def anonymize_user(self,user_id:UUID):
        await self.db.execute(update(User).where(User.id == user_id).values(
            email=f"deleted_user_{user_id}@erased.local",
            hashed_password="GDPR_ERASED",
            deleted_at=func.now(),
        ))
    
    async def commit(self):
        await self.db.commit()
        
    
