import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

# We need to import the service and related models.
# To avoid actual DB queries, we will mock the dependencies.
from app.modules.shipments.service import ShipmentsService
from app.modules.shipments.enum import ShipmentStatus
from fastapi import HTTPException

class TestShipmentsService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Mock the db session
        self.mock_db = AsyncMock()
        
        # Create the instance of the service
        # Service initializes its own repositories, we'll want to patch them or replace them after init
        self.service = ShipmentsService(self.mock_db)
        
        # Replace the initialized repositories with AsyncMocks
        self.service.repo = AsyncMock()
        self.service.status_log = AsyncMock()

    async def test_create_shipment(self):
        # Setup mock behavior
        mock_shipment = MagicMock()
        mock_shipment.id = 1
        mock_shipment.tracking_number = "TRK-12345678"
        self.service.repo.create_shipment.return_value = mock_shipment
        
        # Data
        tenant_id = 99
        origin = "NY"
        destination = "LA"
        weight = 10.5
        recipient_name = "Jane Doe"
        recipient_phone = "1234567890"
        delivery_address = "123 Street"
        pickup_date = datetime(2025, 1, 1)
        delivery_date = datetime(2025, 1, 5)
        description = "Test Package"
        
        # Execution
        result = await self.service.create_shipment(
            tenant_id, origin, destination, weight, recipient_name,
            recipient_phone, delivery_address, pickup_date, delivery_date, description
        )
        
        # Assertions
        self.assertEqual(result, mock_shipment)
        self.service.repo.create_shipment.assert_called_once()
        
        args = self.service.repo.create_shipment.call_args[0]
        self.assertEqual(args[0], tenant_id)
        self.assertTrue(args[1].startswith("TRK-"))  # tracking_number
        self.assertEqual(args[2], ShipmentStatus.CREATED)  # status
        self.assertEqual(args[3], origin)
        self.assertEqual(args[4], destination)
        self.assertEqual(args[5], weight)
        self.assertEqual(args[6], recipient_name)
        self.assertEqual(args[7], recipient_phone)
        self.assertEqual(args[8], delivery_address)
        self.assertEqual(args[9], pickup_date)
        self.assertEqual(args[10], delivery_date)
        self.assertEqual(args[11], description)
        self.assertEqual(args[12], "other")  # category
        self.assertEqual(args[13], 0.0)      # confidence
        self.assertIsNone(args[14])          # assign_driver_id
        
        self.mock_db.flush.assert_called_once()
        self.service.status_log.create_status_log.assert_called_once_with(
            mock_shipment.id, ShipmentStatus.CREATED, origin, None
        )
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(mock_shipment)

    async def test_update_shipment(self):
        # Setup mock behavior
        mock_shipment = MagicMock()
        mock_shipment.id = 1
        mock_shipment.origin = "NY"
        mock_shipment.assign_driver_id = 42
        self.service.repo.get_by_id.return_value = mock_shipment
        
        # Execution
        result = await self.service.update_shipment(1, ShipmentStatus.IN_TRANSIT)
        
        # Assertions
        self.assertEqual(result, mock_shipment)
        self.service.repo.get_by_id.assert_called_once_with(1)
        self.service.repo.update_status.assert_called_once_with(1, ShipmentStatus.IN_TRANSIT)
        self.service.status_log.create_status_log.assert_called_once_with(
            1, ShipmentStatus.IN_TRANSIT, "NY", 42
        )
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(mock_shipment)

    async def test_assing_driver(self):
        # Setup mock behavior
        mock_shipment = MagicMock()
        mock_shipment.id = 1
        mock_shipment.origin = "NY"
        self.service.repo.get_by_id.return_value = mock_shipment
        
        driver_id = 42
        user_id = 100
        
        # Execution
        result = await self.service.assing_driver(1, ShipmentStatus.ASSIGNED, driver_id, user_id)
        
        # Assertions
        self.assertEqual(result, mock_shipment)
        self.service.repo.get_by_id.assert_called_once_with(1)
        self.service.repo.assign_driver.assert_called_once_with(1, driver_id)
        self.service.repo.update_status.assert_called_once_with(1, ShipmentStatus.ASSIGNED.value)
        self.service.status_log.create_status_log.assert_called_once_with(
            1, ShipmentStatus.ASSIGNED.value, "NY", user_id
        )
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(mock_shipment)

    async def test_get_by_tracking_number_success(self):
        # Setup mock behavior
        mock_shipment = MagicMock()
        mock_shipment.id = 1
        mock_shipment.tracking_number = "TRK-123"
        mock_shipment.status = ShipmentStatus.CREATED
        mock_shipment.origin = "NY"
        mock_shipment.destination = "LA"
        mock_shipment.recipient_name = "John Done"
        mock_shipment.recipient_phone = "1234567890"

        self.service.repo.get_by_tracking_number.return_value = mock_shipment
        
        mock_log = MagicMock()
        mock_log.status = ShipmentStatus.CREATED
        mock_log.location = "NY"
        mock_log.timestamp = datetime.now()
        self.service.status_log.get_logs_by_shipment_id.return_value = [mock_log]
        
        # Execution
        result = await self.service.get_by_tracking_number("TRK-123")
        
        # Assertions
        self.assertEqual(result["tracking_number"], "TRK-123")
        self.assertEqual(result["recipient_phone"], "****7890")
        self.assertEqual(len(result["history"]), 1)
        self.assertEqual(result["history"][0]["location"], "NY")
        
    async def test_get_by_tracking_number_not_found(self):
        # Setup mock behavior
        self.service.repo.get_by_tracking_number.return_value = None
        
        # Execution and Assertion
        with self.assertRaises(HTTPException) as context:
            await self.service.get_by_tracking_number("TRK-UNKNOWN")
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "shipment not found")

if __name__ == "__main__":
    unittest.main()
