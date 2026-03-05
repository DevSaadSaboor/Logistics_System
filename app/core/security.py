from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime, timedelta,timezone
from app.core.config import settings
import secrets  
import hashlib
pwd_context = CryptContext(
    schemes= ["bcrypt"],
    deprecated  = "auto"
)

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password:str , hash_password:str):
    return pwd_context.verify(plain_password,hash_password)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_DATE = 60

def  create_access_token(data:dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY_DATE)
    to_encode.update({
    "exp": int(expire.timestamp())
    })
    encode_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encode_jwt

def create_refresh_token():
    return secrets.token_urlsafe(64)

def hash_refresh_token(token:str):
    return hashlib.sha256(token.encode()).hexdigest()

def decode_access_token(token:str):
    try:
        payload =  jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=ALGORITHM
        )
        return payload
    
    except JWTError:
        return None
