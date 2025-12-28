"""Tests for dashboard endpoints."""

import pytest
from httpx import AsyncClient

from washflow_api.models import Location, Service, Status


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
async def test_dashboard_summary_empty(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard summary with no tickets."""
    response = await client.get(
        "/api/v1/dashboard/summary",
        headers=owner_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_tickets"] == 0
    assert data["in_progress"] == 0
    assert data["completed"] == 0
    assert data["avg_total_minutes"] is None
    assert data["avg_sample_size"] == 0
    assert data["throughput_per_hour"] is None
    assert data["range"] == "hoy"


@pytest.mark.asyncio
async def test_dashboard_summary_with_tickets(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard summary with tickets in progress."""
    # Create a ticket
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={"plate": "TEST-001"},
    )
    assert create_response.status_code == 201

    # Get summary
    response = await client.get(
        "/api/v1/dashboard/summary",
        headers=owner_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_tickets"] == 1
    assert data["in_progress"] == 1
    assert data["completed"] == 0


@pytest.mark.asyncio
async def test_dashboard_summary_with_completed_tickets(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard summary with completed tickets."""
    # Create a ticket
    create_response = await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={"plate": "TEST-002"},
    )
    ticket_id = create_response.json()["id"]

    # Move to terminal status
    terminal_status = next(s for s in test_statuses if s.is_terminal)
    await client.post(
        f"/api/v1/tickets/{ticket_id}/move",
        headers=owner_headers,
        json={"to_status_id": terminal_status.id},
    )

    # Get summary
    response = await client.get(
        "/api/v1/dashboard/summary",
        headers=owner_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_tickets"] == 1
    assert data["in_progress"] == 0
    assert data["completed"] == 1
    # avg_sample_size should be 1 since we have one completed ticket
    assert data["avg_sample_size"] == 1
    # avg_total_minutes should be set since we have completed tickets
    assert data["avg_total_minutes"] is not None or data["avg_total_minutes"] == 0


@pytest.mark.asyncio
async def test_dashboard_flow_returns_all_statuses(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard flow returns all statuses in sort order."""
    response = await client.get(
        "/api/v1/dashboard/flow",
        headers=owner_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["statuses"]) == len(test_statuses)

    # Verify sort order
    sort_orders = [s["sort_order"] for s in data["statuses"]]
    assert sort_orders == sorted(sort_orders)


@pytest.mark.asyncio
async def test_dashboard_flow_counts_tickets_per_status(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard flow counts tickets per status correctly."""
    # Create two tickets (they start in first status)
    await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={"plate": "TEST-A"},
    )
    await client.post(
        f"/api/v1/locations/{test_location.id}/tickets",
        headers=owner_headers,
        json={"plate": "TEST-B"},
    )

    # Get flow
    response = await client.get(
        "/api/v1/dashboard/flow",
        headers=owner_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
    data = response.json()

    # First status should have 2 tickets
    first_status = data["statuses"][0]
    assert first_status["count"] == 2


@pytest.mark.asyncio
async def test_dashboard_timeline_hourly_buckets(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard timeline returns hourly buckets for today."""
    response = await client.get(
        "/api/v1/dashboard/timeline",
        headers=owner_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["bucket"] == "hour"
    # Should have points for each hour up to current hour
    assert len(data["points"]) > 0
    # All points should have label in HH:00 format
    for point in data["points"]:
        assert ":" in point["label"]
        assert point["count"] >= 0


@pytest.mark.asyncio
async def test_dashboard_timeline_yesterday_full_day(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard timeline returns 24 hourly buckets for yesterday."""
    response = await client.get(
        "/api/v1/dashboard/timeline",
        headers=owner_headers,
        params={"range": "ayer"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["bucket"] == "hour"
    # Yesterday should have all 24 hours
    assert len(data["points"]) == 24


@pytest.mark.asyncio
async def test_dashboard_timeline_weekly_daily_buckets(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard timeline returns daily buckets for week view."""
    response = await client.get(
        "/api/v1/dashboard/timeline",
        headers=owner_headers,
        params={"range": "ultimos_7_dias"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["bucket"] == "day"
    # Should have 7 days
    assert len(data["points"]) == 7


@pytest.mark.asyncio
async def test_dashboard_summary_different_ranges(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test dashboard summary works with all range options."""
    for range_option in ["hoy", "ayer", "ultimos_7_dias"]:
        response = await client.get(
            "/api/v1/dashboard/summary",
            headers=owner_headers,
            params={"range": range_option},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["range"] == range_option


@pytest.mark.asyncio
async def test_dashboard_requires_authentication(
    client: AsyncClient,
    test_location: Location,
) -> None:
    """Test dashboard endpoints require authentication."""
    response = await client.get(
        "/api/v1/dashboard/summary",
        params={"range": "hoy"},
    )
    assert response.status_code in (401, 403)  # Unauthorized or Forbidden without token


@pytest.mark.asyncio
async def test_dashboard_staff_can_access(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that staff users can access dashboard."""
    response = await client.get(
        "/api/v1/dashboard/summary",
        headers=staff_headers,
        params={"range": "hoy"},
    )
    assert response.status_code == 200
