from pydantic import BaseModel,field_validator,model_validator,Field
from datetime import datetime
import re


class ShipmentCreate(BaseModel):
    origin: str
    destination: str
    recipient_name: str
    recipient_phone : str
    weight : float
    delivery_address: str
    description: str
    pickup_date: datetime
   
class ShipmentResponse(BaseModel):
    origin: str
    destination: str
    recipient_name: str
    recipient_phone : str
    weight : float
    delivery_address: str
    description: str
    pickup_date: datetime
    delivery_date: datetime
    category:str
    confidence:float




# Add Custom Pydantic validators 
    @field_validator("weight")
    @classmethod
    def validate_weighr(cls , value):
        if value <= 0:
            raise ValueError("Weight must be postive")
        if value > 10000:
            raise ValueError("weight exceed maximum limit")
        return value


    @field_validator("recipient_phone")
    @classmethod
    def validate_phone(cls,value):
        if not value:
            raise ValueError("phone number can not be empty")
        
        if not value.isdigit():
            raise ValueError("Phone numbers  must contain digits")
        if len(value) < 8:
            raise ValueError("Phone number length must contains 8 digits")
        if len(value) > 20:
            raise ValueError("Phone number exceeds Maximum Limit")
        return value
   
    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if len(value.strip()) < 10:
            raise ValueError("Description can not be less than 10")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        if self.pickup_date >= self.delivery_date:
            raise ValueError("pickup_date must be before delivery_date")
        return self








    