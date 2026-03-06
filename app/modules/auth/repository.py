from .models import RefreshToken
from sqlalchemy import select,update
from datetime import timezone,datetime
from sqlalchemy.ext.asyncio import AsyncSession


class RefreshTokenRespsitory:
     def __init__(self,db):
        self.db = db

     async def create(self,user_id,token_hash,expires_at):
        token = RefreshToken(
            user_id = user_id,
            token_hash = token_hash,
            expires_at = expires_at
        )
        self.db.add(token)
        return token
    
     async def get_refresh_token_by_hash(self,token_hash):
        query = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
     async def revoke_refresh_token(self,token_id):
        query = update(RefreshToken).where(RefreshToken.id == token_id).values(revoked_at = datetime.now(timezone.utc))
        await self.db.execute(query)
        await self.db.commit()

