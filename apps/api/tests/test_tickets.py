"""Tests for ticket endpoints."""

import pytest
from httpx import AsyncClient

from washflow_api.models import Location, Service, Status, User


@pytest.fixture
async def test_service(db_session, test_org, test_location) -> Service:
    """Create a test service."""
    service = Service(
        organization_id=test_org.id,
        location_id=test_location.id,
        name="Lavado Completo",
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
async def test_create_ticket_assigns_first_status(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
    test_service: Service,
) -> None:
    """Test that creating a ticket assigns the first status by sort_order."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={
            "plate": "ABC-123",
            "service_ids": [test_service.id],
        },
    )
    assert response.status_code == 201
    data = response.json()

    # Should have a public_code
    assert data["public_code"].startswith("WF-")

    # Should be assigned to first status (sort_order=0)
    first_status = min(test_statuses, key=lambda s: s.sort_order)
    assert data["current_status_id"] == first_status.id


@pytest.mark.asyncio
async def test_create_ticket_snapshots_service(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
    test_service: Service,
) -> None:
    """Test that creating a ticket snapshots service data."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={
            "service_ids": [test_service.id],
        },
    )
    assert response.status_code == 201
    data = response.json()

    # Check services are snapshotted
    assert len(data["services"]) == 1
    service_snapshot = data["services"][0]
    assert service_snapshot["captured_name"] == test_service.name
    assert service_snapshot["captured_price_mxn"] == test_service.price_mxn
    assert service_snapshot["captured_duration_minutes"] == test_service.duration_minutes


@pytest.mark.asyncio
async def test_create_ticket_computes_eta(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
    test_service: Service,
) -> None:
    """Test that ETA is computed based on service duration."""
    response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={
            "service_ids": [test_service.id],
        },
    )
    assert response.status_code == 201
    data = response.json()

    # ETA should be set when services are selected
    assert data["eta_at"] is not None
    assert data["total_duration_minutes"] == test_service.duration_minutes


@pytest.mark.asyncio
async def test_create_ticket_creates_event(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that creating a ticket creates a 'created' event."""
    # Create ticket
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={},
    )
    assert create_response.status_code == 201
    ticket_id = create_response.json()["id"]

    # Get events
    events_response = await client.get(
        f"/api/v1/tickets/{ticket_id}/events",
        headers=owner_headers,
    )
    assert events_response.status_code == 200
    events = events_response.json()["items"]

    assert len(events) == 1
    assert events[0]["event_type"] == "created"


@pytest.mark.asyncio
async def test_move_ticket_creates_event(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that moving a ticket creates a 'moved' event."""
    # Create ticket
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={},
    )
    ticket_id = create_response.json()["id"]

    # Move to another status
    second_status = sorted(test_statuses, key=lambda s: s.sort_order)[1]
    move_response = await client.post(
        f"/api/v1/tickets/{ticket_id}/move",
        headers=owner_headers,
        json={"to_status_id": second_status.id},
    )
    assert move_response.status_code == 200

    # Get events
    events_response = await client.get(
        f"/api/v1/tickets/{ticket_id}/events",
        headers=owner_headers,
    )
    events = events_response.json()["items"]

    assert len(events) == 2
    assert events[1]["event_type"] == "moved"
    assert events[1]["to_status_id"] == second_status.id


@pytest.mark.asyncio
async def test_staff_cannot_update_eta(
    client: AsyncClient,
    staff_headers: dict[str, str],
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that staff cannot manually update ETA."""
    # Create ticket as owner
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={},
    )
    ticket_id = create_response.json()["id"]

    # Try to update ETA as staff
    eta_response = await client.patch(
        f"/api/v1/tickets/{ticket_id}/eta",
        headers=staff_headers,
        json={"eta_at": "2024-01-15T14:00:00Z"},
    )
    assert eta_response.status_code == 403


@pytest.mark.asyncio
async def test_owner_can_update_eta(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that owner can manually update ETA."""
    # Create ticket
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={},
    )
    ticket_id = create_response.json()["id"]

    # Update ETA
    eta_response = await client.patch(
        f"/api/v1/tickets/{ticket_id}/eta",
        headers=owner_headers,
        json={"eta_at": "2024-01-15T14:00:00Z"},
    )
    assert eta_response.status_code == 200
    assert "2024-01-15" in eta_response.json()["eta_at"]


@pytest.mark.asyncio
async def test_list_tickets_filters_by_status(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that ticket list can be filtered by status."""
    # Create a ticket
    await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={},
    )

    first_status = min(test_statuses, key=lambda s: s.sort_order)

    # Filter by the first status
    response = await client.get(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        params={"status_id": first_status.id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert all(t["current_status_id"] == first_status.id for t in data["items"])


@pytest.mark.asyncio
async def test_list_tickets_search(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that ticket list can be searched."""
    # Create a ticket with specific plate
    await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={"plate": "XYZ-999"},
    )

    # Search by plate
    response = await client.get(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        params={"q": "XYZ"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(t["plate"] == "XYZ-999" for t in data["items"])


@pytest.mark.asyncio
async def test_create_ticket_fails_without_statuses(
    client: AsyncClient,
    owner_headers: dict[str, str],
    db_session,
    test_org,
) -> None:
    """Test that creating a ticket fails if location has no statuses."""
    from washflow_api.models import Location

    # Create a location without statuses
    location = Location(
        organization_id=test_org.id,
        name="Empty Location",
    )
    db_session.add(location)
    await db_session.flush()
    await db_session.refresh(location)

    response = await client.post(
        f"/api/v1/locations/{location.id}/tickets",
        headers=owner_headers,
        json={},
    )
    assert response.status_code == 400
    assert "estados" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_move_to_terminal_sets_completed_at(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that moving to terminal status sets completed_at."""
    # Create ticket
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={},
    )
    ticket_id = create_response.json()["id"]
    assert create_response.json()["completed_at"] is None

    # Find terminal status
    terminal_status = next(s for s in test_statuses if s.is_terminal)

    # Move to terminal status
    move_response = await client.post(
        f"/api/v1/tickets/{ticket_id}/move",
        headers=owner_headers,
        json={"to_status_id": terminal_status.id},
    )
    assert move_response.status_code == 200
    assert move_response.json()["completed_at"] is not None
