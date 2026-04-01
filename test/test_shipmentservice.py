import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.modules.shipments.service import ShipmentsService 


@pytest.mark.asyncio
async def test_create_shipment_with_ai_success():

    mock_db = AsyncMock()

    service = ShipmentsService(mock_db)

    # Mock repo + status log
    service.repo = AsyncMock()
    service.status_log = AsyncMock()

    # Mock categorizer
    with patch("app.modules.shipments.service.ShipmentCategorizer") as MockCategorizer:
        mock_instance = MockCategorizer.return_value
        mock_instance.categorize.return_value = MagicMock(
            category="electronics",
            confidence=0.95
        )

        service.repo.create_shipment.return_value = MagicMock(id=1)

        result = await service.create_shipment(
            tenant_id=1,
            origin="A",
            destination="B",
            weight=10,
            recipient_name="John",
            recipient_phone="12345678",
            delivery_address="Address",
            pickup_date="2025-01-01",
            delivery_date="2025-01-02",
            description="iPhone shipment"
        )

        assert result is not None
        service.repo.create_shipment.assert_called_once()

@pytest.mark.asyncio
async def test_create_shipment_ai_failure():

    mock_db = AsyncMock()
    service = ShipmentsService(mock_db)

    service.repo = AsyncMock()
    service.status_log = AsyncMock()

    with patch("app.modules.shipments.service.ShipmentCategorizer") as MockCategorizer:
        mock_instance = MockCategorizer.return_value
        mock_instance.categorize.side_effect = Exception("AI failed")

        service.repo.create_shipment.return_value = MagicMock(id=1)

        result = await service.create_shipment(
            tenant_id=1,
            origin="A",
            destination="B",
            weight=10,
            recipient_name="John",
            recipient_phone="12345678",
            delivery_address="Address",
            pickup_date="2025-01-01",
            delivery_date="2025-01-02",
            description="random item"
        )

        assert result is not None

@pytest.mark.asyncio
async def test_category_passed_to_repo():

    mock_db = AsyncMock()
    service = ShipmentsService(mock_db)

    service.repo = AsyncMock()
    service.status_log = AsyncMock()

    with patch("app.modules.shipments.service.ShipmentCategorizer") as MockCategorizer:
        mock_instance = MockCategorizer.return_value
        mock_instance.categorize.return_value = MagicMock(
            category="furniture",
            confidence=0.8
        )

        service.repo.create_shipment.return_value = MagicMock(id=1)

        await service.create_shipment(
            tenant_id=1,
            origin="A",
            destination="B",
            weight=10,
            recipient_name="John",
            recipient_phone="12345678",
            delivery_address="Address",
            pickup_date="2025-01-01",
            delivery_date="2025-01-02",
            description="wooden table"
        )

        args = service.repo.create_shipment.call_args[0]

        # category index depends on your repo signature
        assert "furniture" in args