"""Tests for status endpoints."""

import pytest
from httpx import AsyncClient

from washflow_api.models import Location, Status


@pytest.mark.asyncio
async def test_list_statuses_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that owner can list statuses."""
    response = await client.get(
        f"/api/v1/locations/{test_location.id}/statuses",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(test_statuses)
    # Verify sorted by sort_order
    for i in range(len(data["items"]) - 1):
        assert data["items"][i]["sort_order"] <= data["items"][i + 1]["sort_order"]


@pytest.mark.asyncio
async def test_list_statuses_staff(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that staff can list statuses."""
    response = await client.get(
        f"/api/v1/locations/{test_location.id}/statuses",
        headers=staff_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(test_statuses)


@pytest.mark.asyncio
async def test_create_status_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that owner can create a status."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/statuses",
        headers=owner_headers,
        json={"name": "Nuevo Estado", "is_terminal": False},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Nuevo Estado"
    assert data["is_terminal"] is False


@pytest.mark.asyncio
async def test_create_status_staff_forbidden(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test that staff cannot create a status."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/statuses",
        headers=staff_headers,
        json={"name": "Staff Status"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_status_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_statuses: list[Status],
) -> None:
    """Test that owner can update a status."""
    status = test_statuses[0]
    response = await client.patch(
        f"/api/v1/statuses/{status.id}",
        headers=owner_headers,
        json={"name": "Updated Status", "is_terminal": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Status"
    assert data["is_terminal"] is True


@pytest.mark.asyncio
async def test_reorder_statuses_owner(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that owner can reorder statuses."""
    # Reverse the order
    reversed_ids = [s.id for s in reversed(test_statuses)]

    response = await client.post(
        f"/api/v1/locations/{test_location.id}/statuses/reorder",
        headers=owner_headers,
        json={"ordered_ids": reversed_ids},
    )
    assert response.status_code == 200
    data = response.json()

    # Verify new order matches reversed ids
    result_ids = [s["id"] for s in data["items"]]
    assert result_ids == reversed_ids


@pytest.mark.asyncio
async def test_reorder_statuses_staff_forbidden(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that staff cannot reorder statuses."""
    reversed_ids = [s.id for s in reversed(test_statuses)]

    response = await client.post(
        f"/api/v1/locations/{test_location.id}/statuses/reorder",
        headers=staff_headers,
        json={"ordered_ids": reversed_ids},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_duplicate_status_name(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that duplicate status names are rejected."""
    existing_name = test_statuses[0].name

    response = await client.post(
        f"/api/v1/locations/{test_location.id}/statuses",
        headers=owner_headers,
        json={"name": existing_name},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_terminal_status_flag(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_statuses: list[Status],
) -> None:
    """Test that terminal status is correctly set."""
    terminal_status = next(s for s in test_statuses if s.is_terminal)

    response = await client.get(
        f"/api/v1/statuses/{terminal_status.id}",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_terminal"] is True
