from fastapi import APIRouter,Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

from app.core.dependencies import get_current_tenant_user
from app.modules.consent.schema import ConsentCreate
from app.modules.consent.service import ConsentService


router = APIRouter(prefix="/consent",tags=["consent"])

@router.post("/")
async def grant_consent(
    request:Request,
    payload:ConsentCreate,
    db:AsyncSession = Depends(get_db),
    current_user = Depends(get_current_tenant_user)
):
    
    service = ConsentService(db)

    consent  = await service.grant_consent(
        user_id = current_user.id,
        tenant_id= current_user.tenant_id,
        consent_type=payload.consent_type,
        ip_addresses= request.client.host,
        user_agent=request.headers.get("User-agent")
    )
    return consent


@router.get("/me")
async def my_consent(current_user = Depends(get_current_tenant_user),db:AsyncSession = Depends(get_db)):
    service = ConsentService(db)
    return await service.get_my_consent(user_id= current_user.id)


@router.delete("/{consent_id}")
async def revoke_consent(request: Request,consent_id,current_user=Depends(get_current_tenant_user),db: AsyncSession = Depends(get_db),):

    service = ConsentService(db)
    return await service.revoke_my_consent(
        consent_id=consent_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
    )