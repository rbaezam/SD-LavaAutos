"""Tests for notification endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.models import Location, Status, Ticket, Organization, User
from washflow_api.models.notification import (
    NotificationTemplate,
    NotificationChannel,
    NotificationEvent,
)


@pytest.fixture
async def test_ticket(
    db_session: AsyncSession,
    test_org: Organization,
    test_location: Location,
    test_statuses: list[Status],
) -> Ticket:
    """Create a test ticket."""
    ticket = Ticket(
        organization_id=test_org.id,
        location_id=test_location.id,
        current_status_id=test_statuses[0].id,
        public_code="WF-TEST",
        plate="TEST-123",
        customer_name="Juan Pérez",
        customer_whatsapp="5215551234567",
    )
    db_session.add(ticket)
    await db_session.flush()
    await db_session.refresh(ticket)
    return ticket


@pytest.fixture
async def test_template(
    db_session: AsyncSession,
    test_org: Organization,
) -> NotificationTemplate:
    """Create a test notification template."""
    template = NotificationTemplate(
        organization_id=test_org.id,
        channel=NotificationChannel.WHATSAPP,
        event=NotificationEvent.TICKET_CREATED,
        title="Bienvenida",
        message_template="Hola {{customer_name}}, tu vehículo {{vehicle_label}} está siendo atendido.",
        is_active=True,
    )
    db_session.add(template)
    await db_session.flush()
    await db_session.refresh(template)
    return template


@pytest.mark.asyncio
async def test_list_templates_empty(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test listing templates when none exist."""
    response = await client.get(
        "/api/v1/notifications/templates",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_template(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test creating a notification template."""
    response = await client.post(
        "/api/v1/notifications/templates",
        headers=owner_headers,
        json={
            "channel": "whatsapp",
            "event": "ticket_created",
            "title": "Bienvenida",
            "message_template": "Hola {{customer_name}}!",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Bienvenida"
    assert data["channel"] == "whatsapp"
    assert data["event"] == "ticket_created"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_templates_with_data(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_location: Location,
) -> None:
    """Test listing templates with existing data."""
    response = await client.get(
        "/api/v1/notifications/templates",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Bienvenida"
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_update_template(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_location: Location,
) -> None:
    """Test updating a notification template."""
    response = await client.patch(
        f"/api/v1/notifications/templates/{test_template.id}",
        headers=owner_headers,
        json={
            "title": "Nuevo Título",
            "is_active": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Nuevo Título"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_template(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_location: Location,
) -> None:
    """Test deleting a notification template."""
    response = await client.delete(
        f"/api/v1/notifications/templates/{test_template.id}",
        headers=owner_headers,
    )
    assert response.status_code == 204

    # Verify it's deleted
    response = await client.get(
        "/api/v1/notifications/templates",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_template_variables(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test getting available template variables."""
    response = await client.get(
        "/api/v1/notifications/templates/variables",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "variables" in data
    assert len(data["variables"]) > 0

    # Check some expected variables
    variable_names = [v["name"] for v in data["variables"]]
    assert "customer_name" in variable_names
    assert "vehicle_label" in variable_names
    assert "public_code" in variable_names


@pytest.mark.asyncio
async def test_preview_notification(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_ticket: Ticket,
    test_location: Location,
) -> None:
    """Test previewing a notification message."""
    response = await client.post(
        "/api/v1/notifications/preview",
        headers=owner_headers,
        json={
            "ticket_id": str(test_ticket.id),
            "template_id": str(test_template.id),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "recipient" in data
    # Check that variables are replaced
    assert "Juan Pérez" in data["message"]  # customer_name
    assert "TEST-123" in data["message"]  # vehicle_label (plate)


@pytest.mark.asyncio
async def test_send_notification_dry_run(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_ticket: Ticket,
    test_location: Location,
) -> None:
    """Test sending a notification in dry run mode (simulated)."""
    response = await client.post(
        "/api/v1/notifications/send",
        headers=owner_headers,
        json={
            "ticket_id": str(test_ticket.id),
            "channel": "whatsapp",
            "template_id": str(test_template.id),
            "dry_run": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "simulated"


@pytest.mark.asyncio
async def test_send_notification_without_recipient(
    client: AsyncClient,
    owner_headers: dict[str, str],
    db_session: AsyncSession,
    test_org: Organization,
    test_location: Location,
    test_statuses: list[Status],
    test_template: NotificationTemplate,
) -> None:
    """Test sending notification to ticket without phone number."""
    # Create ticket without customer_whatsapp
    ticket = Ticket(
        organization_id=test_org.id,
        location_id=test_location.id,
        current_status_id=test_statuses[0].id,
        public_code="WF-NOPH",
        plate="NO-PHONE",
    )
    db_session.add(ticket)
    await db_session.flush()
    await db_session.refresh(ticket)

    response = await client.post(
        "/api/v1/notifications/send",
        headers=owner_headers,
        json={
            "ticket_id": str(ticket.id),
            "channel": "whatsapp",
            "template_id": str(test_template.id),
        },
    )
    assert response.status_code == 400
    assert "no tiene número" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_logs_empty(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_location: Location,
) -> None:
    """Test listing notification logs when none exist."""
    response = await client.get(
        "/api/v1/notifications/logs",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_logs_after_send(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_ticket: Ticket,
    test_location: Location,
) -> None:
    """Test that sending a notification creates a log entry."""
    # Send a notification
    await client.post(
        "/api/v1/notifications/send",
        headers=owner_headers,
        json={
            "ticket_id": str(test_ticket.id),
            "channel": "whatsapp",
            "template_id": str(test_template.id),
            "dry_run": True,
        },
    )

    # Check logs
    response = await client.get(
        "/api/v1/notifications/logs",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["ticket_id"] == str(test_ticket.id)
    assert data["items"][0]["status"] == "simulated"


@pytest.mark.asyncio
async def test_list_logs_by_ticket(
    client: AsyncClient,
    owner_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_ticket: Ticket,
    test_location: Location,
) -> None:
    """Test filtering logs by ticket_id."""
    # Send a notification
    await client.post(
        "/api/v1/notifications/send",
        headers=owner_headers,
        json={
            "ticket_id": str(test_ticket.id),
            "channel": "whatsapp",
            "template_id": str(test_template.id),
            "dry_run": True,
        },
    )

    # Filter by ticket
    response = await client.get(
        "/api/v1/notifications/logs",
        headers=owner_headers,
        params={"ticket_id": str(test_ticket.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_staff_cannot_manage_templates(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that staff users cannot create templates."""
    response = await client.post(
        "/api/v1/notifications/templates",
        headers=staff_headers,
        json={
            "channel": "sms",
            "event": "ticket_created",
            "title": "Test",
            "message_template": "Test message",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_staff_can_send_notification(
    client: AsyncClient,
    staff_headers: dict[str, str],
    test_template: NotificationTemplate,
    test_ticket: Ticket,
    test_location: Location,
    test_statuses: list[Status],
) -> None:
    """Test that staff users can send notifications."""
    response = await client.post(
        "/api/v1/notifications/send",
        headers=staff_headers,
        json={
            "ticket_id": str(test_ticket.id),
            "channel": "whatsapp",
            "template_id": str(test_template.id),
            "dry_run": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_filter_templates_by_channel(
    client: AsyncClient,
    owner_headers: dict[str, str],
    db_session: AsyncSession,
    test_org: Organization,
    test_location: Location,
) -> None:
    """Test filtering templates by channel."""
    # Create templates for different channels
    whatsapp_template = NotificationTemplate(
        organization_id=test_org.id,
        channel=NotificationChannel.WHATSAPP,
        event=NotificationEvent.TICKET_CREATED,
        title="WhatsApp Template",
        message_template="WA message",
        is_active=True,
    )
    sms_template = NotificationTemplate(
        organization_id=test_org.id,
        channel=NotificationChannel.SMS,
        event=NotificationEvent.TICKET_CREATED,
        title="SMS Template",
        message_template="SMS message",
        is_active=True,
    )
    db_session.add_all([whatsapp_template, sms_template])
    await db_session.flush()

    # Filter by WhatsApp
    response = await client.get(
        "/api/v1/notifications/templates",
        headers=owner_headers,
        params={"channel": "whatsapp"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["channel"] == "whatsapp"

    # Filter by SMS
    response = await client.get(
        "/api/v1/notifications/templates",
        headers=owner_headers,
        params={"channel": "sms"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["channel"] == "sms"
