from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.consent.repo import ConsentRepository
from app.modules.consent.model import Consent
from app.modules.audit.service import AuditService
from sqlalchemy import Select,desc


class ConsentService():
    def __init__(self, db:AsyncSession):
        self.db = db
        self.repo = ConsentRepository(db)

    
    async def grant_consent(self,user_id,tenant_id,consent_type,ip_addresses = None,user_agent = None):
        exisitng = await self.repo.get_active_consent( user_id = user_id,consent_type = consent_type)
        if exisitng:
            return exisitng
        

        consent = Consent(
            user_id = user_id,
            consent_type = consent_type,
            granted = True
        )

        consent = await self.repo.create_consent(consent)
        await self.repo.commit()

        await AuditService(self.db).log(
            action="consent_granted",
            resource_type="consent",
            resource_id= str(consent.id),
            user_id=str(user_id),
            tenant_id=str(tenant_id),
            ip_address=ip_addresses,
            user_agent=user_agent,
            metadata_json= {
                "consent_type": consent_type,
            },
        )
        return consent
    
    async def get_my_consent(self,user_id):
        return await self.repo.get_user_consents(user_id= user_id)


    async def revoke_my_consent(self,consent_id,user_id,tenant_id,ip_address=  None,user_agent = None):
        consent = await self.repo.revoke_consent(consent_id=consent_id)
        if not consent:
            return {"message": "Consent not found"}
        await self.repo.commit()

        await AuditService(self.db).log(
            action="consent.revoekd",
            resource_type="consent",
            resource_id=str(consent.id),
            user_id=str(user_id),
            tenant_id=str(tenant_id),
            ip_address=ip_address,
            user_agent = user_agent,
            metadata_json= {
                "consent_type": consent.consent_type,
            },
        )
        return {
            "message": "Consent revoked successfully"
        }
    

    
    async def verify_ai_consent(self,user_id):
        result = await self.db.execute(Select(Consent).where(Consent.user_id == user_id).where(Consent.consent_type == "AI_PROCESSING")
        .order_by(desc(Consent.granted_at)))

        consent = result.scalars().first()

        return (
            consent is not None
            and consent.granted is True
            and consent.revoked_at is None
        )
    
    

        