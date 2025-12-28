"""Base notification provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResponse:
    """Response from a notification provider."""

    success: bool
    message_id: str | None = None
    error: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, message_id: str, raw_response: dict[str, Any] | None = None) -> "ProviderResponse":
        """Create a successful response."""
        return cls(
            success=True,
            message_id=message_id,
            raw_response=raw_response or {},
        )

    @classmethod
    def fail(cls, error: str, raw_response: dict[str, Any] | None = None) -> "ProviderResponse":
        """Create a failed response."""
        return cls(
            success=False,
            error=error,
            raw_response=raw_response or {},
        )


class NotificationProviderBase(ABC):
    """Abstract base class for notification providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        ...

    @abstractmethod
    async def send(self, to: str, message: str) -> ProviderResponse:
        """
        Send a notification message.

        Args:
            to: Recipient phone number (E.164 format preferred)
            message: Message content to send

        Returns:
            ProviderResponse with success status and details
        """
        ...

    @abstractmethod
    async def validate_recipient(self, phone: str) -> bool:
        """
        Validate if a phone number is valid for this provider.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        ...
