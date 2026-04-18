"""
Advanced / edge-case tests for the Shipments module.

Covers areas NOT tested in test_shipment_schema.py / test_shipment_service.py:
  - Boundary-pass values (min/max valid inputs)
  - ShipmentResponse ORM serialization
  - run_ai_categorization (AI success + AI failure fallback)
  - Phone masking edge cases
  - Multiple history entries in get_by_tracking_number
  - Tracking number format validation
  - create_shipment with explicit user_id
"""

import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from pydantic import ValidationError
import uuid

from app.modules.shipments.schema import ShipmentCreate, ShipmentResponse
from app.modules.shipments.service import ShipmentsService
from app.modules.shipments.enum import ShipmentStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_create_data(now=None):
    now = now or datetime.now()
    return {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "recipient_name": "Jane Doe",
        "recipient_phone": "1234567890",
        "weight": 10.5,
        "delivery_address": "123 Main St",
        "description": "Fragile electronics equipment",
        "pickup_date": now,
    }


# ===========================================================================
# Section 1: Boundary PASS values (valid edge cases)
# ===========================================================================

def test_weight_boundary_pass():
    """Weight = 0.001 (just above 0) and 10000.0 (exactly at limit) should pass."""
    now = datetime.now()
    base = _base_create_data(now)

    # Minimum positive weight
    s = ShipmentCreate(**{**base, "weight": 0.001})
    assert s.weight == 0.001

    # Maximum allowed weight
    s = ShipmentCreate(**{**base, "weight": 10000.0})
    assert s.weight == 10000.0


def test_phone_boundary_pass():
    """Phone with exactly 8 digits (min) and 20 digits (max) should pass."""
    now = datetime.now()
    base = _base_create_data(now)

    s = ShipmentCreate(**{**base, "recipient_phone": "12345678"})       # exactly 8
    assert len(s.recipient_phone) == 8

    s = ShipmentCreate(**{**base, "recipient_phone": "1" * 20})         # exactly 20
    assert len(s.recipient_phone) == 20


def test_description_boundary_pass():
    """Description with exactly 10 characters (after strip) should pass."""
    now = datetime.now()
    base = _base_create_data(now)

    s = ShipmentCreate(**{**base, "description": "1234567890"})  # exactly 10 chars
    assert s.description == "1234567890"


def test_description_whitespace_boundary():
    """Description that is 10 chars but all whitespace should fail."""
    now = datetime.now()
    base = _base_create_data(now)

    with pytest.raises(ValidationError) as exc:
        ShipmentCreate(**{**base, "description": "          "})  # 10 spaces
    assert "Description can not be less than 10 characters" in str(exc.value)


# ===========================================================================
# Section 2: ShipmentResponse serialization (ORM mode)
# ===========================================================================

def test_shipment_response_from_orm_dict():
    """ShipmentResponse should correctly parse from a dict (simulating ORM object)."""
    now = datetime.now()
    data = {
        "id": uuid.uuid4(),
        "tracking_number": "TRK-ABCD1234",
        "status": "CREATED",
        "origin": "NY",
        "destination": "LA",
        "recipient_name": "John Doe",
        "recipient_phone": "9876543210",
        "weight": 5.0,
        "delivery_address": "456 Oak Ave",
        "description": "Standard package delivery",
        "pickup_date": now,
        "expected_delivery_date": now + timedelta(days=3),
        "category": "electronics",
        "confidence": 0.95,
    }
    response = ShipmentResponse(**data)
    assert response.tracking_number == "TRK-ABCD1234"
    assert response.status == "CREATED"
    assert response.confidence == 0.95
    assert isinstance(response.id, uuid.UUID)


def test_shipment_response_from_orm_object():
    """ShipmentResponse.from_orm should work with a MagicMock simulating an ORM model."""
    now = datetime.now()
    orm_obj = MagicMock()
    orm_obj.id = uuid.uuid4()
    orm_obj.tracking_number = "TRK-XYZ12345"
    orm_obj.status = "IN_TRANSIT"
    orm_obj.origin = "Chicago"
    orm_obj.destination = "Miami"
    orm_obj.recipient_name = "Alice"
    orm_obj.recipient_phone = "5559876543"
    orm_obj.weight = 22.5
    orm_obj.delivery_address = "789 Elm St"
    orm_obj.description = "Electronics shipment goods"
    orm_obj.pickup_date = now
    orm_obj.expected_delivery_date = now + timedelta(days=2)
    orm_obj.category = "electronics"
    orm_obj.confidence = 0.87

    response = ShipmentResponse.model_validate(orm_obj)
    assert response.tracking_number == "TRK-XYZ12345"
    assert response.status == "IN_TRANSIT"


# ===========================================================================
# Section 3: Tracking number format
# ===========================================================================

class TestTrackingNumberFormat(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_db = AsyncMock()
        self.service = ShipmentsService(self.mock_db)
        self.service.repo = AsyncMock()
        self.service.status_log = AsyncMock()

    async def test_tracking_number_format(self):
        """Generated tracking_number must be TRK-XXXXXXXX (8 uppercase hex chars)."""
        mock_shipment = MagicMock(id=1)
        self.service.repo.create_shipment.return_value = mock_shipment

        await self.service.create_shipment(
            1, "NY", "LA", 5.0, "John", "12345678",
            "123 St", datetime(2025, 1, 1), "Test description here"
        )

        tracking_number = self.service.repo.create_shipment.call_args[0][1]
        assert tracking_number.startswith("TRK-")
        suffix = tracking_number[4:]
        assert len(suffix) == 8
        assert suffix == suffix.upper()
        assert all(c in "0123456789ABCDEF" for c in suffix)

    async def test_tracking_number_unique_per_call(self):
        """Each create_shipment call should generate a different tracking number."""
        mock_shipment = MagicMock(id=1)
        self.service.repo.create_shipment.return_value = mock_shipment

        kwargs = dict(
            tenant_id=1, origin="NY", destination="LA", weight=5.0,
            recipient_name="John", recipient_phone="12345678",
            delivery_address="123 St", pickup_date=datetime(2025, 1, 1),
            description="Test description here"
        )

        await self.service.create_shipment(**kwargs)
        tn1 = self.service.repo.create_shipment.call_args[0][1]

        self.service.repo.reset_mock()

        await self.service.create_shipment(**kwargs)
        tn2 = self.service.repo.create_shipment.call_args[0][1]

        assert tn1 != tn2


# ===========================================================================
# Section 4: AI categorization
# ===========================================================================

class TestAiCategorization(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_db = AsyncMock()
        self.service = ShipmentsService(self.mock_db)
        self.service.repo = AsyncMock()

    async def test_run_ai_categorization_success(self):
        """When AI returns a result, repo.update_ai_fields is called with correct values."""
        with patch("app.modules.shipments.service.ShipmentCategorizer") as MockCat:
            mock_result = MagicMock()
            mock_result.category = "electronics"
            mock_result.confidence = 0.92
            MockCat.return_value.categorize.return_value = mock_result

            await self.service.run_ai_categorization(shipment_id=5, tenant_id=1, description="MacBook Pro laptop")

        self.service.repo.update_ai_fields.assert_called_once_with(5, "electronics", 0.92)
        self.mock_db.commit.assert_called_once()

    async def test_run_ai_categorization_fallback_on_error(self):
        """When AI raises an exception, fallback to category='other', confidence=0.0."""
        with patch("app.modules.shipments.service.ShipmentCategorizer") as MockCat:
            MockCat.return_value.categorize.side_effect = RuntimeError("AI service down")

            await self.service.run_ai_categorization(shipment_id=7, tenant_id=1, description="Unknown item")

        self.service.repo.update_ai_fields.assert_called_once_with(7, "other", 0.0)
        self.mock_db.commit.assert_called_once()


# ===========================================================================
# Section 5: Phone masking edge cases
# ===========================================================================

class TestPhoneMasking(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_db = AsyncMock()
        self.service = ShipmentsService(self.mock_db)
        self.service.repo = AsyncMock()
        self.service.status_log = AsyncMock()

    async def _tracking_result(self, phone):
        mock_shipment = MagicMock()
        mock_shipment.tracking_number = "TRK-TEST0001"
        mock_shipment.status = ShipmentStatus.CREATED
        mock_shipment.origin = "NY"
        mock_shipment.destination = "LA"
        mock_shipment.recipient_name = "Test User"
        mock_shipment.recipient_phone = phone
        self.service.repo.get_by_tracking_number.return_value = mock_shipment
        self.service.status_log.get_logs_by_shipment_id.return_value = []
        return await self.service.get_by_tracking_number("TRK-TEST0001")

    async def test_phone_masked_correctly(self):
        """Last 4 digits shown, rest masked with ****."""
        result = await self._tracking_result("9876543210")
        assert result["recipient_phone"] == "****3210"

    async def test_phone_exactly_4_digits(self):
        """Phone with exactly 4 digits → ****XXXX."""
        result = await self._tracking_result("1234")
        assert result["recipient_phone"] == "****1234"

    async def test_phone_none_returns_none(self):
        """None phone should return None (not crash)."""
        result = await self._tracking_result(None)
        assert result["recipient_phone"] is None


# ===========================================================================
# Section 6: Multiple history entries
# ===========================================================================

class TestTrackingHistory(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_db = AsyncMock()
        self.service = ShipmentsService(self.mock_db)
        self.service.repo = AsyncMock()
        self.service.status_log = AsyncMock()

    async def test_multiple_status_logs_in_history(self):
        """All status log entries should appear in history in correct order."""
        mock_shipment = MagicMock()
        mock_shipment.tracking_number = "TRK-MULTI001"
        mock_shipment.status = ShipmentStatus.IN_TRANSIT
        mock_shipment.origin = "NY"
        mock_shipment.destination = "LA"
        mock_shipment.recipient_name = "Bob"
        mock_shipment.recipient_phone = "1112223333"
        self.service.repo.get_by_tracking_number.return_value = mock_shipment

        log1 = MagicMock(status=ShipmentStatus.CREATED,   location="NY", timestamp=datetime(2025, 1, 1))
        log2 = MagicMock(status=ShipmentStatus.ASSIGNED,  location="NY", timestamp=datetime(2025, 1, 2))
        log3 = MagicMock(status=ShipmentStatus.IN_TRANSIT, location="Chicago", timestamp=datetime(2025, 1, 3))
        self.service.status_log.get_logs_by_shipment_id.return_value = [log1, log2, log3]

        result = await self.service.get_by_tracking_number("TRK-MULTI001")

        assert len(result["history"]) == 3
        assert result["history"][0]["location"] == "NY"
        assert result["history"][1]["status"] == ShipmentStatus.ASSIGNED
        assert result["history"][2]["location"] == "Chicago"

    async def test_empty_history(self):
        """If no logs exist, history should be an empty list."""
        mock_shipment = MagicMock()
        mock_shipment.tracking_number = "TRK-EMPTY001"
        mock_shipment.status = ShipmentStatus.CREATED
        mock_shipment.origin = "NY"
        mock_shipment.destination = "LA"
        mock_shipment.recipient_name = "Alice"
        mock_shipment.recipient_phone = "9998887777"
        self.service.repo.get_by_tracking_number.return_value = mock_shipment
        self.service.status_log.get_logs_by_shipment_id.return_value = []

        result = await self.service.get_by_tracking_number("TRK-EMPTY001")

        assert result["history"] == []


# ===========================================================================
# Section 7: create_shipment with explicit user_id
# ===========================================================================

class TestCreateShipmentWithUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_db = AsyncMock()
        self.service = ShipmentsService(self.mock_db)
        self.service.repo = AsyncMock()
        self.service.status_log = AsyncMock()

    async def test_create_shipment_passes_user_id_to_status_log(self):
        """user_id should be forwarded to status_log.create_status_log."""
        mock_shipment = MagicMock(id=42)
        self.service.repo.create_shipment.return_value = mock_shipment

        await self.service.create_shipment(
            tenant_id=1, origin="NY", destination="LA", weight=5.0,
            recipient_name="John", recipient_phone="12345678",
            delivery_address="123 St", pickup_date=datetime(2025, 1, 1),
            description="Test description here",
            user_id=999
        )

        self.service.status_log.create_status_log.assert_called_once_with(
            42, ShipmentStatus.CREATED, "NY", 999
        )


if __name__ == "__main__":
    unittest.main()
