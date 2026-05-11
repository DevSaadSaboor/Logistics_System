"""
Shared test fixtures.

The FastAPI app startup runs `Base.metadata.create_all` and initializes PGVector.
CI / local runs often have no PostgreSQL; tests that need the full app use a mocked
async engine and skip vector store initialization.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_mock_async_engine() -> MagicMock:
    conn = AsyncMock()

    async def _run_sync(fn, *args, **kwargs):
        return None

    conn.run_sync = _run_sync

    begin_ctx = AsyncMock()
    begin_ctx.__aenter__ = AsyncMock(return_value=conn)
    begin_ctx.__aexit__ = AsyncMock(return_value=None)

    eng = MagicMock()
    eng.begin = MagicMock(return_value=begin_ctx)
    return eng


@pytest.fixture
def app_client():
    """HTTP client against the real FastAPI app with DB + vector init stubbed out."""
    import app.core.database as database

    mock_engine = _make_mock_async_engine()

    with patch.object(database, "engine", mock_engine):
        with patch("app.main.ensure_vector_store_initialized"):
            from app.main import app
            from fastapi.testclient import TestClient

            with TestClient(app) as client:
                yield client
