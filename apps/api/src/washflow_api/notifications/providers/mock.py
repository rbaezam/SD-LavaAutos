"""Mock notification provider for testing and development."""

import asyncio
import re
from datetime import UTC, datetime
from uuid import uuid4

import structlog

from washflow_api.notifications.providers.base import NotificationProviderBase, ProviderResponse

logger = structlog.get_logger()


class MockProvider(NotificationProviderBase):
    """
    Mock notification provider that simulates sending messages.

    This provider is used for development and testing purposes.
    It logs messages instead of actually sending them.
    """

    def __init__(self, delay_seconds: float = 0.5, fail_rate: float = 0.0) -> None:
        """
        Initialize the mock provider.

        Args:
            delay_seconds: Artificial delay to simulate network latency
            fail_rate: Probability of simulated failure (0.0 to 1.0)
        """
        self._delay = delay_seconds
        self._fail_rate = fail_rate
        self._sent_messages: list[dict] = []

    @property
    def name(self) -> str:
        return "mock"

    async def send(self, to: str, message: str) -> ProviderResponse:
        """
        Simulate sending a notification.

        Args:
            to: Recipient phone number
            message: Message content

        Returns:
            ProviderResponse with simulated success
        """
        # Simulate network delay
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        # Generate a mock message ID
        message_id = f"mock_{uuid4().hex[:12]}"
        timestamp = datetime.now(UTC).isoformat()

        # Store for debugging/testing
        sent_record = {
            "id": message_id,
            "to": to,
            "message": message,
            "timestamp": timestamp,
            "provider": self.name,
        }
        self._sent_messages.append(sent_record)

        # Log the simulated send
        logger.info(
            "Mock notification sent",
            message_id=message_id,
            to=to,
            message_preview=message[:50] + "..." if len(message) > 50 else message,
        )

        return ProviderResponse.ok(
            message_id=message_id,
            raw_response={
                "simulated": True,
                "timestamp": timestamp,
                "recipient": to,
                "message_length": len(message),
            },
        )

    async def validate_recipient(self, phone: str) -> bool:
        """
        Validate phone number format.

        Accepts various formats but prefers E.164.
        """
        if not phone:
            return False

        # Remove common formatting
        cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)

        # Check if it's a valid number (10-15 digits)
        if not cleaned.isdigit():
            return False

        if len(cleaned) < 10 or len(cleaned) > 15:
            return False

        return True

    def get_sent_messages(self) -> list[dict]:
        """Get all messages sent through this provider (for testing)."""
        return self._sent_messages.copy()

    def clear_sent_messages(self) -> None:
        """Clear the sent messages history (for testing)."""
        self._sent_messages.clear()
