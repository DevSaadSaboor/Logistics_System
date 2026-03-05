from .models import RefreshToken
class RefreshTokenRespsitory:
    async def create(self,db,user_id,token_hash,expires_at):
        token = RefreshToken(
            user_id = user_id,
            token_hash = token_hash,
            expires_at = expires_at
        )
        db.add(token)
        return token