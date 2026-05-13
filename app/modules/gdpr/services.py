from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.gdpr.repo import GDPRRepository
from app.modules.audit.service import AuditService

class GDPRService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.repo = GDPRRepository(db)

    
    async def erase_user_data(self,user_id:UUID,performed_by:UUID | None = None):
        await self.repo.delete_refresh_tokens(user_id = user_id,)
        await self.repo.anonymize_audit_log(user_id = user_id,)
        await self.repo.anonymize_user(user_id=user_id)
        await self.repo.commit()
        await AuditService(self.db).log(

            action="gdpr.erasure_completed",

            resource_type="user",

            resource_id=str(user_id),

            user_id=str(performed_by)
            if performed_by
            else None,

            metadata_json={
                "erased_user_id": str(user_id),
            },
        )

        return {
            "message": "User data erased successfully"
        }