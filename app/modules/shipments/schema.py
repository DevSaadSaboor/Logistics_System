from pydantic import BaseModel


class ShipmentCreate(BaseModel):
    origin: str
    destination: str
    recipient_name: str
    recipient_phone : str
    weight : float
    delivery_address: str
    
    