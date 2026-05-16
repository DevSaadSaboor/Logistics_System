from sqlalchemy import Select,Update,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.consent.model import Consent

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
        self.db.commit()

    async def revoke_consent(self,consent_id,):
        result = await self.db.execute(Select(Consent).where(Consent.id == consent_id))
        consent = result.scalar_one_or_none()
        if not consent:
            return None
        await self.db.execute(Update(Consent).where(Consent.id == consent_id).values(granted=False,revoked_at=func.now(),))
        await self.db.flush()
        return consent