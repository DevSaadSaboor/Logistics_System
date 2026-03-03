from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta,timezone
from app.core.config import settings

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

def create_access_token(data:dict):
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