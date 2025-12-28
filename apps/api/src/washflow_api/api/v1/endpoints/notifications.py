"""Notification API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db.session import get_db
from washflow_api.models.notification import (
    NotificationChannel,
    NotificationEvent,
)
from washflow_api.models.ticket import Ticket
from washflow_api.schemas.notification import (
    NotificationChannelEnum,
    NotificationEventEnum,
    NotificationLogListResponse,
    NotificationLogOut,
    NotificationTemplateCreate,
    NotificationTemplateListResponse,
    NotificationTemplateOut,
    NotificationTemplateUpdate,
    PreviewNotificationRequest,
    PreviewNotificationResponse,
    SendNotificationRequest,
    SendNotificationResponse,
    TemplateVariable,
    TemplateVariablesResponse,
)
from washflow_api.services.notification import NotificationService

router = APIRouter()


# ==================== Template Endpoints ====================


@router.get("/templates/variables", response_model=TemplateVariablesResponse)
async def get_template_variables(
    current_user: CurrentUser,
) -> TemplateVariablesResponse:
    """Get available template variables."""
    variables = [
        TemplateVariable(
            name="customer_name",
            description="Nombre del cliente",
            example="Juan Pérez",
        ),
        TemplateVariable(
            name="vehicle_label",
            description="Placa o descripción del vehículo",
            example="ABC-123",
        ),
        TemplateVariable(
            name="plate",
            description="Placa del vehículo",
            example="ABC-123",
        ),
        TemplateVariable(
            name="status",
            description="Estado actual del ticket",
            example="En lavado",
        ),
        TemplateVariable(
            name="location_name",
            description="Nombre de la sucursal",
            example="Sucursal Centro",
        ),
        TemplateVariable(
            name="public_code",
            description="Código público del ticket",
            example="WF-A1B2",
        ),
        TemplateVariable(
            name="eta",
            description="Hora estimada de entrega",
            example="14:30",
        ),
        TemplateVariable(
            name="tracking_url",
            description="URL de seguimiento",
            example="https://app.washflow.com/t/WF-A1B2",
        ),
    ]

    return TemplateVariablesResponse(variables=variables)


@router.get("/templates", response_model=NotificationTemplateListResponse)
async def list_templates(
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    channel: NotificationChannelEnum | None = None,
    event: NotificationEventEnum | None = None,
) -> NotificationTemplateListResponse:
    """List notification templates for the organization."""
    service = NotificationService(db)

    channel_enum = NotificationChannel(channel.value) if channel else None
    event_enum = NotificationEvent(event.value) if event else None

    templates = await service.list_templates(
        organization_id=current_user.organization_id,
        channel=channel_enum,
        event=event_enum,
    )

    return NotificationTemplateListResponse(
        items=[NotificationTemplateOut.model_validate(t) for t in templates],
        total=len(templates),
    )


@router.post("/templates", response_model=NotificationTemplateOut, status_code=201)
async def create_template(
    data: NotificationTemplateCreate,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationTemplateOut:
    """Create a new notification template."""
    service = NotificationService(db)

    template = await service.create_template(
        organization_id=current_user.organization_id,
        channel=NotificationChannel(data.channel.value),
        event=NotificationEvent(data.event.value),
        title=data.title,
        message_template=data.message_template,
        is_active=data.is_active,
    )

    return NotificationTemplateOut.model_validate(template)


@router.get("/templates/{template_id}", response_model=NotificationTemplateOut)
async def get_template(
    template_id: str,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationTemplateOut:
    """Get a specific notification template."""
    service = NotificationService(db)

    template = await service.get_template(template_id, current_user.organization_id)
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    return NotificationTemplateOut.model_validate(template)


@router.patch("/templates/{template_id}", response_model=NotificationTemplateOut)
async def update_template(
    template_id: str,
    data: NotificationTemplateUpdate,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationTemplateOut:
    """Update a notification template."""
    service = NotificationService(db)

    try:
        template = await service.update_template(
            template_id=template_id,
            organization_id=current_user.organization_id,
            title=data.title,
            message_template=data.message_template,
            is_active=data.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return NotificationTemplateOut.model_validate(template)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a notification template."""
    service = NotificationService(db)

    deleted = await service.delete_template(template_id, current_user.organization_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")


# ==================== Send Endpoints ====================


@router.post("/send", response_model=SendNotificationResponse)
async def send_notification(
    data: SendNotificationRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SendNotificationResponse:
    """Send a notification for a ticket."""
    # Load ticket with relationships
    result = await db.execute(
        select(Ticket)
        .where(
            Ticket.id == data.ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
        .options(
            selectinload(Ticket.current_status),
            selectinload(Ticket.location),
        )
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Check rate limit (max 5 per hour per ticket)
    service = NotificationService(db)
    count = await service.get_ticket_notification_count(ticket.id, hours=1)
    if count >= 5:
        raise HTTPException(
            status_code=429,
            detail="Límite de notificaciones alcanzado (máximo 5 por hora)",
        )

    # Get template to determine event
    template = await service.get_template(data.template_id, current_user.organization_id)
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    try:
        log = await service.send_notification(
            ticket=ticket,
            channel=NotificationChannel(data.channel.value),
            event=NotificationEvent(template.event),
            organization_id=current_user.organization_id,
            dry_run=data.dry_run,
        )

        success = log.status in ("sent", "simulated")
        return SendNotificationResponse(
            success=success,
            log_id=log.id,
            status=log.status,
            message="Notificación enviada correctamente" if success else None,
            error=log.error_message if not success else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preview", response_model=PreviewNotificationResponse)
async def preview_notification(
    data: PreviewNotificationRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PreviewNotificationResponse:
    """Preview a notification message without sending."""
    # Load ticket with relationships
    result = await db.execute(
        select(Ticket)
        .where(
            Ticket.id == data.ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
        .options(
            selectinload(Ticket.current_status),
            selectinload(Ticket.location),
        )
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    service = NotificationService(db)

    try:
        preview = await service.preview_message(
            ticket=ticket,
            template_id=data.template_id,
            organization_id=current_user.organization_id,
        )

        return PreviewNotificationResponse(
            recipient=preview["recipient"],
            message=preview["message"],
            channel=preview["channel"],
            event=preview["event"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Log Endpoints ====================


@router.get("/logs", response_model=NotificationLogListResponse)
async def list_logs(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    ticket_id: str | None = Query(default=None, description="Filter by ticket ID"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> NotificationLogListResponse:
    """List notification logs."""
    service = NotificationService(db)

    logs, total = await service.list_logs(
        organization_id=current_user.organization_id,
        ticket_id=ticket_id,
        limit=limit,
        offset=offset,
    )

    return NotificationLogListResponse(
        items=[NotificationLogOut.model_validate(log) for log in logs],
        total=total,
    )
