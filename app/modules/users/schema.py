from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Annotated
from app.modules.users.models import UserRole

PasswordStr = Annotated[str, Field(min_length=8, max_length=72)]


class UserloginRequest(BaseModel):
    id:UUID
    email:str
    tenant_id:UUID
    role:str

class LoginResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str = "bearer"
    user:UserloginRequest

class LoginRequest(BaseModel):
    email: EmailStr
    password: PasswordStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: PasswordStr
    role: UserRole

class UserResponse(BaseModel):
    id:str
    email:str
    role:UserRole
    tenant_id : str

class LoginResponse(BaseModel):
    id:str
    email:str
    user: UserResponse