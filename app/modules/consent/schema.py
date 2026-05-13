from pydantic import BaseModel

class ConsentCreate(BaseModel):
    consent_type:str
