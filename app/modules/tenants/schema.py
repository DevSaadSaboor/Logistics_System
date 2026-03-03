from pydantic import BaseModel
import uuid

class TenantCreate(BaseModel):
    name:str


class TenantResponse(BaseModel):
    id:uuid.UUID
    name:str

class Config:
    from_attributes = True