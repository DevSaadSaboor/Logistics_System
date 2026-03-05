from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.users.respository import UserRepository

security = HTTPBearer()
repo = UserRepository()

async def get_current_user(credentials:HTTPAuthorizationCredentials = Depends(security),db :AsyncSession = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await repo.get_by_id(db,user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user



