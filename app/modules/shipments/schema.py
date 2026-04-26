from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime, timedelta
import uuid
from .enum import ShipmentStatus


class ShipmentCreate(BaseModel):
    origin: str
    destination: str
    recipient_name: str
    recipient_phone : str
    weight : float
    delivery_address: str
    delivery_date: datetime | None = None
    description: str
    pickup_date: datetime
    @field_validator("weight")
    @classmethod
    def validate_weight(cls, value):
        if value <= 0:
            raise ValueError("Weight must be positive")
        if value > 10000:
            raise ValueError("Weight exceeds maximum limit")
        return value

    @field_validator("recipient_phone")
    @classmethod
    def validate_phone(cls, value):
        if not value:
            raise ValueError("Phone number can not be empty")
        if not value.isdigit():
            raise ValueError("Phone numbers must contain digits only")
        if len(value) < 8:
            raise ValueError("Phone number length must contain at least 8 digits")
        if len(value) > 20:
            raise ValueError("Phone number exceeds maximum limit")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if len(value.strip()) < 10:
            raise ValueError("Description can not be less than 10 characters")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        # Keep backward compatibility for clients/tests that don't send delivery_date.
        if self.delivery_date is None:
            self.delivery_date = self.pickup_date + timedelta(days=1)
        if self.pickup_date >= self.delivery_date:
            raise ValueError("pickup_date must be before delivery_date")
        return self
    
class UpdateShipmentStatus(BaseModel):
    status:ShipmentStatus


class ShipmentResponse(BaseModel):
    id: uuid.UUID
    tracking_number: str
    status: str
    origin: str
    destination: str
    recipient_name: str
    recipient_phone: str
    weight: float
    delivery_address: str
    description: str
    pickup_date: datetime
    delivery_date: datetime = Field(
        validation_alias=AliasChoices("delivery_date", "expected_delivery_date")
    )
    category: str
    confidence: float

    model_config = ConfigDict(from_attributes=True)


class SimilarShipmentResponse(BaseModel):
    shipment: ShipmentResponse
    similarity: float