from uuid import UUID
from sqlalchemy import delete, update,Select,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.audit.model import AuditLog
from app.modules.consent.model import Consent
from app.modules.users.models import User
from app.modules.shipments.models import Shipments
from app.modules.audit.model import AuditLog

class GDPRRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_data(self,user_id):
        result  = await self.db.execute(Select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_shipment(self,user_id):
        result = await self.db.execute(Select(Shipments).where(Shipments.created_by == user_id))
        return result.scalars().all()
    
    async def get_user_consents(self,user_id):
        result = await self.db.execute(Select(Consent).where(Consent.user_id == user_id))
        return result.scalars().all()
    
    async def get_user_audit_log(self,user_id):
        result = await self.db.execute(Select(AuditLog).where(AuditLog.user_id == user_id))
        return result.scalars().all()

    
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
        
    
