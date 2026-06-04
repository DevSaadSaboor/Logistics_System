"""Tenant bootstrap auth: POST /tenants/ without bearer only when no tenants exist."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.parametrize(
    "tenant_count,expected_status",
    [
        (0, 200),
        (1, 401),
    ],
)
def test_create_tenant_bootstrap_auth(app_client, tenant_count, expected_status):
    with (
        patch(
            "app.modules.tenants.repository.TenantRepository.count_active",
            new_callable=AsyncMock,
            return_value=tenant_count,
        ),
        patch(
            "app.modules.tenants.service.TenantService.create_tenant",
            new_callable=AsyncMock,
        ) as mock_create,
    ):
        from uuid import uuid4
        from types import SimpleNamespace

        mock_create.return_value = SimpleNamespace(
            id=uuid4(), name="acme", slug="acme"
        )
        r = app_client.post("/tenants/", json={"name": "Acme"})

    assert r.status_code == expected_status
    if expected_status == 401:
        assert "Bearer token required" in r.json()["error"]


def test_list_tenants_no_auth_required(app_client):
    """GET /tenants/ is public (slug needed for register); no bearer token."""
    with patch(
        "app.modules.tenants.service.TenantService.list_tenants",
        new_callable=AsyncMock,
        return_value=[],
    ):
        r = app_client.get("/tenants/")

    assert r.status_code == 200
