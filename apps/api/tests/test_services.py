"""Tests for service endpoints."""

import pytest
from httpx import AsyncClient

from washflow_api.models import Location, Service


@pytest.fixture
async def test_service(db_session, test_org, test_location) -> Service:
    """Create a test service."""
    service = Service(
        organization_id=test_org.id,
        location_id=test_location.id,
        name="Test Service",
        duration_minutes=30,
        price_mxn=150,
        sort_order=0,
        active=True,
    )
    db_session.add(service)
    await db_session.flush()
    await db_session.refresh(service)
    return service


@pytest.mark.asyncio
async def test_list_services_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_service: Service,
) -> None:
    """Test that owner can list services."""
    response = await client.get(
        f"/api/v1/locations/{test_location.id}/services",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(svc["id"] == test_service.id for svc in data["items"])


@pytest.mark.asyncio
async def test_list_services_staff(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
    test_service: Service,
) -> None:
    """Test that staff can list services."""
    response = await client.get(
        f"/api/v1/locations/{test_location.id}/services",
        headers=staff_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_create_service_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that owner can create a service."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/services",
        headers=owner_headers,
        json={
            "name": "Lavado Completo",
            "duration_minutes": 45,
            "price_mxn": 200,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lavado Completo"
    assert data["duration_minutes"] == 45
    assert data["price_mxn"] == 200
    assert data["active"] is True


@pytest.mark.asyncio
async def test_create_service_staff_forbidden(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that staff cannot create a service."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/services",
        headers=staff_headers,
        json={
            "name": "Staff Service",
            "duration_minutes": 30,
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_service_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_service: Service,
) -> None:
    """Test that owner can update a service."""
    response = await client.patch(
        f"/api/v1/services/{test_service.id}",
        headers=owner_headers,
        json={"name": "Updated Service", "price_mxn": 250},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Service"
    assert data["price_mxn"] == 250


@pytest.mark.asyncio
async def test_deactivate_service_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_service: Service,
) -> None:
    """Test that owner can deactivate a service."""
    response = await client.post(
        f"/api/v1/services/{test_service.id}/deactivate",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is False


@pytest.mark.asyncio
async def test_activate_service_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_service: Service,
) -> None:
    """Test that owner can activate a service."""
    # First deactivate
    await client.post(
        f"/api/v1/services/{test_service.id}/deactivate",
        headers=owner_headers,
    )

    # Then activate
    response = await client.post(
        f"/api/v1/services/{test_service.id}/activate",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is True


@pytest.mark.asyncio
async def test_duplicate_service_name_active(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_service: Service,
) -> None:
    """Test that duplicate active service names are rejected."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/services",
        headers=owner_headers,
        json={
            "name": test_service.name,  # Same name as existing active service
            "duration_minutes": 20,
        },
    )
    assert response.status_code == 400
