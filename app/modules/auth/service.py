from app.modules.auth.repository import RefreshTokenRespsitory
from app.modules.users.respository import UserRepository
from app.core.security import hash_refresh_token,create_refresh_token,create_access_token
from app.core.config import Settings
from datetime import timezone,datetime

class AuthService:
    def __init__(self,db):
        
        self.auth_repo = RefreshTokenRespsitory(db)
        self.user_repo = UserRepository(db)

    async def refresh_access_token(self, refresh_token :str,tenant_id):
       token_hash = hash_refresh_token(refresh_token)
       refresh_token_record = await self.auth_repo.get_refresh_token_by_hash(token_hash)
       if refresh_token_record is None:
          raise Exception("Invalid Refesh Token")
       if refresh_token_record.revoked_at is not None:
          raise Exception("Refresh token revoked")
       if refresh_token_record.expires_at < datetime.now(timezone.utc):
          raise Exception("Invalid Refresh Token")
       user = await self.user_repo.get_by_id(refresh_token_record.user_id)
       if user is None:
          raise Exception("User not found")
       if user.tenant_id != tenant_id:
          raise Exception("User not found")
       
       access_token = create_access_token({
          "sub" : str(user.id),
          "tenant_id" : str(user.tenant_id),
          "role"  : user.role.value
       })
       new_refresh_token = create_refresh_token()

       await self.auth_repo.revoke_refresh_token(
            refresh_token_record.id
       )
       new_token_hash = hash_refresh_token(new_refresh_token)
       await self.auth_repo.create(
          user_id= user.id,
          token_hash=new_token_hash,
          expires_at= datetime.now(timezone.utc) + Settings.REFRESH_TOKEN_EXPIRE_DELTA
       )

       return {
          "access_token" : access_token,
          "refresh_token" : new_refresh_token,
          "token_type" : "bearer"
       }



