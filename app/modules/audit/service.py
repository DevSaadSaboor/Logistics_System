from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.model import AuditLog


class AuditService:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def log(self,action:str,resources_type:str,resource_id:str | None = None,user_id:str | None = None,
            tenant_id:str | None = None,ip_address:str | None = None,user_agent:str | None = None,metadate_json:dict | None = None):
        
        audig_log = AuditLog (
            action = action,
            resources_type = resources_type,
            resource_id = resource_id,
            user_id = user_id,
            tenant_id = tenant_id,
            ip_address = ip_address,
            user_agent = user_agent,
            metadate_json = metadate_json
        )

        self.db.add(audig_log)
        await self.db.commit()
        await self.db.refresh(audig_log)
        return audig_log

