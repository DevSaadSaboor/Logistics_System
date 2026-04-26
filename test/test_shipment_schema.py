import pytest
from pydantic import ValidationError
from datetime import datetime
from app.modules.shipments.schema import ShipmentCreate

def test_valid_shipment_create():
    now = datetime.now()
    valid_data = {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "recipient_name": "Jane Doe",
        "recipient_phone": "1234567890",
        "weight": 10.5,
        "delivery_address": "123 Main St",
        "description": "Fragile electronics equipment",
        "pickup_date": now
    }
    shipment = ShipmentCreate(**valid_data)
    assert shipment.weight == 10.5
    assert shipment.recipient_phone == "1234567890"

def test_invalid_weight():
    now = datetime.now()
    invalid_data = {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "recipient_name": "Jane Doe",
        "recipient_phone": "1234567890",
        "weight": -5.0,  # Invalid
        "delivery_address": "123 Main St",
        "description": "Fragile electronics equipment",
        "pickup_date": now
    }
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**invalid_data)
    assert "Weight must be positive" in str(exc.value)

    invalid_data["weight"] = 15000.0  # Exceeds limit
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**invalid_data)
    assert "Weight exceeds maximum limit" in str(exc.value)

    invalid_data["weight"] = 0.0  # Boundary: zero is also invalid
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**invalid_data)
    assert "Weight must be positive" in str(exc.value)

def test_invalid_phone():
    now = datetime.now()
    base = {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "recipient_name": "Jane Doe",
        "weight": 10.5,
        "delivery_address": "123 Main St",
        "description": "Fragile electronics equipment",
        "pickup_date": now
    }

    # Too short
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**{**base, "recipient_phone": "123"})
    assert "Phone number length must contain at least 8 digits" in str(exc.value)

    # Contains non-digits
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**{**base, "recipient_phone": "notadigit"})
    assert "Phone numbers must contain digits only" in str(exc.value)

    # Exceeds max length (21 chars)
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**{**base, "recipient_phone": "1" * 21})
    assert "Phone number exceeds maximum limit" in str(exc.value)

def test_invalid_description():
    now = datetime.now()
    invalid_data = {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "recipient_name": "Jane Doe",
        "recipient_phone": "1234567890",
        "weight": 10.5,
        "delivery_address": "123 Main St",
        "description": "Short",  # Target: < 10 chars
        "pickup_date": now
    }
    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**invalid_data)
    assert "Description can not be less than 10 characters" in str(exc.value)

