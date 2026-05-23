from sqlalchemy import Select,Update,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.consent.model import Consent
from app.modules.users.models import User
from app.modules.shipments.models import Shipments
from app.modules.audit.model import AuditLog

class ConsentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_consent(self, consent:Consent):
        self.db.add(consent)
        await self.db.flush()
        await self.db.refresh(consent)
        return consent
    
    async def get_user_consents(self,user_id):
        result = await self.db.execute(Select(Consent).where(Consent.user_id == user_id))
        return result.scalars().all()
    
    async def get_active_consent(self,user_id,consent_type):
        result = await self.db.execute(Select(Consent).where(Consent.user_id == user_id).where(Consent.consent_type  == consent_type)
                .where(Consent.granted == True))
        
        return result.scalar_one_or_none()

    async def commit(self):
        await self.db.commit()

    async def revoke_consent(self,consent_id,):
        result = await self.db.execute(Select(Consent).where(Consent.id == consent_id))
        consent = result.scalar_one_or_none()
        if not consent:
            return None
        await self.db.execute(Update(Consent).where(Consent.id == consent_id).values(granted=False,revoked_at=func.now(),))
        await self.db.flush()
        await self.db.refresh(consent)
        return consent
    

    async def has_active_consent(self,user_id,consent_type):
        result  = await self.db.execute(Select(Consent).where(Consent.user_id == user_id).where(Consent.consent_type == consent_type)
                .where(Consent.granted == True).where(Consent.revoked_at.is_(None)))
        
        consent =  result.scalar_one_or_none()
        return consent is not None
    

    async def get_user_data(self,user_id):
        result  = await self.db.execute(Select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_shipment(self,user_id):
        result = await self.db.execute(Select(Shipments).where(Shipments.created_by == user_id))
        return result.scalars().all()
    

    async def get_user_audit_log(self,user_id):
        result = await self.db.execute(Select(AuditLog).where(AuditLog.user_id == user_id))
        return result.scalars().all()


    

