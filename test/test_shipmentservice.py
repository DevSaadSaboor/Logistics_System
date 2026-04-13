import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.modules.shipments.service import ShipmentsService 


@pytest.mark.asyncio
async def test_create_shipment_default_values():

    mock_db = AsyncMock()
    service = ShipmentsService(mock_db)

    service.repo = AsyncMock()
    service.status_log = AsyncMock()

    service.repo.create_shipment.return_value = MagicMock(id=1)

    await service.create_shipment(
        tenant_id=1,
        origin="A",
        destination="B",
        weight=10,
        recipient_name="John",
        recipient_phone="12345678",
        delivery_address="Address",
        pickup_date=datetime(2025, 1, 1),
        description="test"
    )

    args = service.repo.create_shipment.call_args[0]

    assert args[-3] == "other"
    assert args[-2] == 0.0

@pytest.mark.asyncio
async def test_run_ai_categorization():

    mock_db = AsyncMock()
    service = ShipmentsService(mock_db)

    service.repo = AsyncMock()

    with patch("app.modules.shipments.service.ShipmentCategorizer") as MockCategorizer:
        mock_instance = MockCategorizer.return_value
        mock_instance.categorize.return_value = MagicMock(
            category="electronics",
            confidence=0.9
        )

        await service.run_ai_categorization(1, 1, "iphone")

        service.repo.update_ai_fields.assert_called_once()

