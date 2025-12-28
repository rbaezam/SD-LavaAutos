"""Twilio notification provider stub.

This is a stub implementation. To use Twilio in production:
1. Install twilio package: pip install twilio
2. Set environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
3. Implement the send() method with actual Twilio API calls
"""

import re

from washflow_api.notifications.providers.base import NotificationProviderBase, ProviderResponse


class TwilioProvider(NotificationProviderBase):
    """
    Twilio SMS provider.

    TODO: Implement with actual Twilio SDK when ready for production.
    """

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_number: str | None = None,
    ) -> None:
        """
        Initialize Twilio provider.

        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Twilio phone number to send from
        """
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number

    @property
    def name(self) -> str:
        return "twilio"

    async def send(self, to: str, message: str) -> ProviderResponse:
        """
        Send SMS via Twilio.

        TODO: Implement with actual Twilio SDK.
        """
        # Validate configuration
        if not all([self._account_sid, self._auth_token, self._from_number]):
            return ProviderResponse.fail(
                error="Twilio provider not configured. Missing credentials.",
                raw_response={"configured": False},
            )

        # TODO: Implement actual Twilio integration
        # Example implementation:
        # from twilio.rest import Client
        # client = Client(self._account_sid, self._auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_=self._from_number,
        #     to=to
        # )
        # return ProviderResponse.ok(
        #     message_id=message.sid,
        #     raw_response={"status": message.status}
        # )

        raise NotImplementedError(
            "Twilio provider is not yet implemented. "
            "Use MockProvider for development or implement Twilio integration."
        )

    async def validate_recipient(self, phone: str) -> bool:
        """Validate phone number format for Twilio."""
        if not phone:
            return False

        # Twilio prefers E.164 format
        # Example: +14155552671
        pattern = r"^\+?[1-9]\d{9,14}$"
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        return bool(re.match(pattern, cleaned))
