"""Notification schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NotificationChannelEnum(str, Enum):
    """Notification channel types."""

    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationEventEnum(str, Enum):
    """Notification event types."""

    TICKET_CREATED = "ticket_created"
    STATUS_CHANGED = "status_changed"
    READY = "ready"
    DELIVERED = "delivered"
    MANUAL = "manual"


class NotificationStatusEnum(str, Enum):
    """Notification status types."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SIMULATED = "simulated"


# ==================== Template Schemas ====================


class NotificationTemplateCreate(BaseModel):
    """Schema for creating a notification template."""

    channel: NotificationChannelEnum
    event: NotificationEventEnum
    title: str = Field(..., min_length=1, max_length=100)
    message_template: str = Field(..., min_length=1, max_length=1000)
    is_active: bool = True


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating a notification template."""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    message_template: str | None = Field(default=None, min_length=1, max_length=1000)
    is_active: bool | None = None


class NotificationTemplateOut(BaseModel):
    """Schema for notification template response."""

    id: str
    organization_id: str
    channel: str
    event: str
    title: str
    message_template: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationTemplateListResponse(BaseModel):
    """Response schema for template list."""

    items: list[NotificationTemplateOut]
    total: int


# ==================== Log Schemas ====================


class NotificationLogOut(BaseModel):
    """Schema for notification log response."""

    id: str
    organization_id: str
    ticket_id: str | None
    template_id: str | None
    channel: str
    provider: str
    event: str
    status: str
    recipient: str
    message: str
    error_message: str | None
    created_at: datetime
    sent_at: datetime | None

    model_config = {"from_attributes": True}


class NotificationLogListResponse(BaseModel):
    """Response schema for log list."""

    items: list[NotificationLogOut]
    total: int


# ==================== Send Schemas ====================


class SendNotificationRequest(BaseModel):
    """Schema for sending a notification."""

    ticket_id: str
    channel: NotificationChannelEnum
    template_id: str
    dry_run: bool = False


class SendNotificationResponse(BaseModel):
    """Response after sending a notification."""

    success: bool
    log_id: str
    status: str
    message: str | None = None
    error: str | None = None


class PreviewNotificationRequest(BaseModel):
    """Schema for previewing a notification."""

    ticket_id: str
    template_id: str


class PreviewNotificationResponse(BaseModel):
    """Response for notification preview."""

    recipient: str
    message: str
    channel: str
    event: str


# ==================== Template Variables ====================


class TemplateVariable(BaseModel):
    """Information about a template variable."""

    name: str
    description: str
    example: str


class TemplateVariablesResponse(BaseModel):
    """Response with available template variables."""

    variables: list[TemplateVariable]


# ==================== Provider Config Schemas ====================


class NotificationProviderEnum(str, Enum):
    """Notification provider types."""

    MOCK = "mock"
    TWILIO = "twilio"
    WHATSAPP_CLOUD = "whatsapp_cloud"


class ProviderConfigOut(BaseModel):
    """Schema for provider configuration response."""

    id: str
    organization_id: str
    channel: str
    provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProviderConfigUpdate(BaseModel):
    """Schema for updating provider configuration."""

    provider: NotificationProviderEnum
    is_active: bool = True
