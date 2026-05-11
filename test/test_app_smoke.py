"""
Application-level smoke checks: app wiring, startup (with DB stubbed), OpenAPI.

These do not substitute integration tests against a real PostgreSQL instance.
"""

from __future__ import annotations


def test_root_ok(app_client):
    r = app_client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Backend is running"}


def test_openapi_schema_loads(app_client):
    r = app_client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec.get("openapi").startswith("3.")
    paths = spec.get("paths", {})
    assert "/" in paths
    assert "/shipments" in paths or any("/shipments" in p for p in paths)
