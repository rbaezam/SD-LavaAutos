"""Notification service for sending and managing notifications."""

import re
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from washflow_api.core.config import settings
from washflow_api.models.notification import (
    NotificationChannel,
    NotificationEvent,
    NotificationLog,
    NotificationProviderConfig,
    NotificationProviderType,
    NotificationStatus,
    NotificationTemplate,
)
from washflow_api.models.ticket import Ticket
from washflow_api.notifications.providers.base import NotificationProviderBase
from washflow_api.notifications.providers.mock import MockProvider

logger = structlog.get_logger()


class NotificationService:
    """Service for managing and sending notifications."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._providers: dict[str, NotificationProviderBase] = {
            NotificationProviderType.MOCK.value: MockProvider(),
        }

    def _get_provider(self, provider_type: str) -> NotificationProviderBase:
        """Get a notification provider instance."""
        provider = self._providers.get(provider_type)
        if not provider:
            # Default to mock provider
            logger.warning(
                "Unknown provider type, falling back to mock",
                provider_type=provider_type,
            )
            return self._providers[NotificationProviderType.MOCK.value]
        return provider

    # ==================== Template Management ====================

    async def list_templates(
        self,
        organization_id: str,
        channel: NotificationChannel | None = None,
        event: NotificationEvent | None = None,
        active_only: bool = False,
    ) -> list[NotificationTemplate]:
        """List notification templates for an organization."""
        query = select(NotificationTemplate).where(
            NotificationTemplate.organization_id == organization_id
        )

        if channel:
            query = query.where(NotificationTemplate.channel == channel.value)

        if event:
            query = query.where(NotificationTemplate.event == event.value)

        if active_only:
            query = query.where(NotificationTemplate.is_active.is_(True))

        query = query.order_by(NotificationTemplate.channel, NotificationTemplate.event)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_template(
        self,
        template_id: str,
        organization_id: str,
    ) -> NotificationTemplate | None:
        """Get a specific template by ID."""
        result = await self.db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.id == template_id,
                NotificationTemplate.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_template(
        self,
        organization_id: str,
        channel: NotificationChannel,
        event: NotificationEvent,
    ) -> NotificationTemplate | None:
        """Get the active template for a specific channel and event."""
        result = await self.db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.organization_id == organization_id,
                NotificationTemplate.channel == channel.value,
                NotificationTemplate.event == event.value,
                NotificationTemplate.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def create_template(
        self,
        organization_id: str,
        channel: NotificationChannel,
        event: NotificationEvent,
        title: str,
        message_template: str,
        is_active: bool = True,
    ) -> NotificationTemplate:
        """Create a new notification template."""
        template = NotificationTemplate(
            organization_id=organization_id,
            channel=channel.value,
            event=event.value,
            title=title,
            message_template=message_template,
            is_active=is_active,
        )
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def update_template(
        self,
        template_id: str,
        organization_id: str,
        title: str | None = None,
        message_template: str | None = None,
        is_active: bool | None = None,
    ) -> NotificationTemplate:
        """Update an existing template."""
        template = await self.get_template(template_id, organization_id)
        if not template:
            raise ValueError("Plantilla no encontrada")

        if title is not None:
            template.title = title
        if message_template is not None:
            template.message_template = message_template
        if is_active is not None:
            template.is_active = is_active

        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def delete_template(
        self,
        template_id: str,
        organization_id: str,
    ) -> bool:
        """Delete a template."""
        template = await self.get_template(template_id, organization_id)
        if not template:
            return False

        await self.db.delete(template)
        await self.db.flush()
        return True

    # ==================== Provider Config Management ====================

    async def get_provider_config(
        self,
        organization_id: str,
        channel: NotificationChannel,
    ) -> NotificationProviderConfig | None:
        """Get provider configuration for a channel."""
        result = await self.db.execute(
            select(NotificationProviderConfig).where(
                NotificationProviderConfig.organization_id == organization_id,
                NotificationProviderConfig.channel == channel.value,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_provider_config(
        self,
        organization_id: str,
        channel: NotificationChannel,
        provider: NotificationProviderType,
        is_active: bool = True,
        config_json: dict[str, Any] | None = None,
    ) -> NotificationProviderConfig:
        """Create or update provider configuration."""
        existing = await self.get_provider_config(organization_id, channel)

        if existing:
            existing.provider = provider.value
            existing.is_active = is_active
            existing.config_json = config_json
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            config = NotificationProviderConfig(
                organization_id=organization_id,
                channel=channel.value,
                provider=provider.value,
                is_active=is_active,
                config_json=config_json,
            )
            self.db.add(config)
            await self.db.flush()
            await self.db.refresh(config)
            return config

    # ==================== Template Rendering ====================

    def render_template(self, template: str, context: dict[str, Any]) -> str:
        """
        Render a template string with context variables.

        Variables use {{variable_name}} syntax.
        """
        result = template

        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            # Sanitize value to prevent injection
            safe_value = str(value) if value is not None else ""
            result = result.replace(placeholder, safe_value)

        return result

    def build_context_from_ticket(self, ticket: Ticket) -> dict[str, Any]:
        """Build template context from a ticket."""
        # Build vehicle label
        vehicle_label = ticket.plate or ticket.vehicle_desc or "Vehículo"

        # Format ETA
        eta_formatted = ""
        if ticket.eta_at:
            eta_formatted = ticket.eta_at.strftime("%H:%M")

        # Build tracking URL
        tracking_url = f"{settings.frontend_url}/t/{ticket.public_code}"

        return {
            "customer_name": ticket.customer_name or "Cliente",
            "vehicle_label": vehicle_label,
            "plate": ticket.plate or "",
            "status": ticket.current_status.name if ticket.current_status else "",
            "location_name": ticket.location.name if ticket.location else "",
            "public_code": ticket.public_code,
            "eta": eta_formatted,
            "tracking_url": tracking_url,
        }

    # ==================== Sending Notifications ====================

    async def send_notification(
        self,
        ticket: Ticket,
        channel: NotificationChannel,
        event: NotificationEvent,
        organization_id: str,
        dry_run: bool = False,
    ) -> NotificationLog:
        """
        Send a notification for a ticket.

        Args:
            ticket: The ticket to notify about
            channel: SMS or WhatsApp
            event: The event type triggering the notification
            organization_id: Organization ID
            dry_run: If True, simulate without actually sending

        Returns:
            NotificationLog with the result
        """
        # Get recipient
        recipient = ticket.customer_whatsapp
        if not recipient:
            raise ValueError("El ticket no tiene número de WhatsApp del cliente")

        # Get active template
        template = await self.get_active_template(organization_id, channel, event)
        if not template:
            raise ValueError(f"No hay plantilla activa para {channel.value}/{event.value}")

        # Build context and render message
        context = self.build_context_from_ticket(ticket)
        message = self.render_template(template.message_template, context)

        # Get provider configuration
        provider_config = await self.get_provider_config(organization_id, channel)
        provider_type = (
            provider_config.provider
            if provider_config and provider_config.is_active
            else NotificationProviderType.MOCK.value
        )

        # Create log entry
        log = NotificationLog(
            organization_id=organization_id,
            ticket_id=ticket.id,
            template_id=template.id,
            channel=channel.value,
            provider=provider_type,
            event=event.value,
            status=NotificationStatus.PENDING.value,
            recipient=recipient,
            message=message,
            payload_json={
                "context": context,
                "template_id": template.id,
                "dry_run": dry_run,
            },
        )
        self.db.add(log)
        await self.db.flush()

        # Send or simulate
        if dry_run:
            log.status = NotificationStatus.SIMULATED.value
            log.sent_at = datetime.now(UTC)
            log.response_json = {"simulated": True}
            logger.info(
                "Notification simulated (dry run)",
                log_id=log.id,
                recipient=recipient,
            )
        else:
            provider = self._get_provider(provider_type)
            try:
                response = await provider.send(recipient, message)
                if response.success:
                    log.status = NotificationStatus.SENT.value
                    log.sent_at = datetime.now(UTC)
                    log.response_json = response.raw_response
                    logger.info(
                        "Notification sent successfully",
                        log_id=log.id,
                        message_id=response.message_id,
                    )
                else:
                    log.status = NotificationStatus.FAILED.value
                    log.error_message = response.error
                    log.response_json = response.raw_response
                    logger.error(
                        "Notification failed",
                        log_id=log.id,
                        error=response.error,
                    )
            except Exception as e:
                log.status = NotificationStatus.FAILED.value
                log.error_message = str(e)
                logger.exception(
                    "Exception sending notification",
                    log_id=log.id,
                )

        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def send_auto_notification(
        self,
        ticket: Ticket,
        event: NotificationEvent,
    ) -> NotificationLog | None:
        """
        Attempt to send automatic notification if template exists.

        This is called by TicketService after events.
        Returns None if no template or no recipient.
        """
        # Check if ticket has recipient
        if not ticket.customer_whatsapp:
            return None

        # Try WhatsApp first, then SMS
        for channel in [NotificationChannel.WHATSAPP, NotificationChannel.SMS]:
            template = await self.get_active_template(
                ticket.organization_id, channel, event
            )
            if template:
                try:
                    return await self.send_notification(
                        ticket=ticket,
                        channel=channel,
                        event=event,
                        organization_id=ticket.organization_id,
                        dry_run=False,
                    )
                except Exception as e:
                    logger.error(
                        "Auto notification failed",
                        ticket_id=ticket.id,
                        event=event.value,
                        error=str(e),
                    )

        return None

    async def preview_message(
        self,
        ticket: Ticket,
        template_id: str,
        organization_id: str,
    ) -> dict[str, str]:
        """
        Generate a preview of the notification message.

        Returns dict with recipient and rendered message.
        """
        template = await self.get_template(template_id, organization_id)
        if not template:
            raise ValueError("Plantilla no encontrada")

        context = self.build_context_from_ticket(ticket)
        message = self.render_template(template.message_template, context)

        return {
            "recipient": ticket.customer_whatsapp or "",
            "message": message,
            "channel": template.channel,
            "event": template.event,
        }

    # ==================== Log Management ====================

    async def list_logs(
        self,
        organization_id: str,
        ticket_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[NotificationLog], int]:
        """List notification logs with optional ticket filter."""
        query = select(NotificationLog).where(
            NotificationLog.organization_id == organization_id
        )

        if ticket_id:
            query = query.where(NotificationLog.ticket_id == ticket_id)

        # Count total
        from sqlalchemy import func

        count_query = select(func.count(NotificationLog.id)).where(
            NotificationLog.organization_id == organization_id
        )
        if ticket_id:
            count_query = count_query.where(NotificationLog.ticket_id == ticket_id)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        query = (
            query.order_by(NotificationLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_ticket_notification_count(
        self,
        ticket_id: str,
        hours: int = 1,
    ) -> int:
        """Get count of notifications sent for a ticket in the last N hours."""
        from sqlalchemy import func

        cutoff = datetime.now(UTC).replace(
            hour=datetime.now(UTC).hour - hours,
            minute=0,
            second=0,
            microsecond=0,
        )

        result = await self.db.execute(
            select(func.count(NotificationLog.id)).where(
                NotificationLog.ticket_id == ticket_id,
                NotificationLog.created_at >= cutoff,
                NotificationLog.status.in_([
                    NotificationStatus.SENT.value,
                    NotificationStatus.SIMULATED.value,
                ]),
            )
        )
        return result.scalar() or 0
