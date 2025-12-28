"""Tests for location endpoints."""

import pytest
from httpx import AsyncClient

from washflow_api.models import Location, User


@pytest.mark.asyncio
async def test_list_locations_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that owner can list locations."""
    response = await client.get("/api/v1/locations", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(loc["id"] == test_location.id for loc in data["items"])


@pytest.mark.asyncio
async def test_list_locations_staff(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that staff can list locations."""
    response = await client.get("/api/v1/locations", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_create_location_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
) -> None:
    """Test that owner can create a location."""
    response = await client.post(
        "/api/v1/locations",
        headers=owner_headers,
        json={"name": "New Location", "address": "123 Main St"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Location"
    assert data["address"] == "123 Main St"


@pytest.mark.asyncio
async def test_create_location_staff_forbidden(
    client: AsyncClient,
    staff_headers: dict[str, str],
) -> None:
    """Test that staff cannot create a location."""
    response = await client.post(
        "/api/v1/locations",
        headers=staff_headers,
        json={"name": "Staff Location"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_location(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test getting a specific location."""
    response = await client.get(
        f"/api/v1/locations/{test_location.id}",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_location.id
    assert data["name"] == test_location.name


@pytest.mark.asyncio
async def test_update_location_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that owner can update a location."""
    response = await client.patch(
        f"/api/v1/locations/{test_location.id}",
        headers=owner_headers,
        json={"name": "Updated Location Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Location Name"


@pytest.mark.asyncio
async def test_update_location_staff_forbidden(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that staff cannot update a location."""
    response = await client.patch(
        f"/api/v1/locations/{test_location.id}",
        headers=staff_headers,
        json={"name": "Staff Update"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_locations_unauthenticated(client: AsyncClient) -> None:
    """Test that unauthenticated requests are rejected."""
    response = await client.get("/api/v1/locations")
    assert response.status_code == 401
