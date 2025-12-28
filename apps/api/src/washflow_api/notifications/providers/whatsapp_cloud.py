"""WhatsApp Cloud API provider stub.

This is a stub implementation. To use WhatsApp Cloud API in production:
1. Set up a Meta Business account and WhatsApp Business API
2. Set environment variables: WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN
3. Implement the send() method with actual WhatsApp Cloud API calls
"""

import re

from washflow_api.notifications.providers.base import NotificationProviderBase, ProviderResponse


class WhatsAppCloudProvider(NotificationProviderBase):
    """
    WhatsApp Cloud API provider.

    TODO: Implement with actual WhatsApp Cloud API when ready for production.
    """

    def __init__(
        self,
        phone_number_id: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """
        Initialize WhatsApp Cloud provider.

        Args:
            phone_number_id: WhatsApp Business phone number ID
            access_token: Meta Graph API access token
        """
        self._phone_number_id = phone_number_id
        self._access_token = access_token
        self._api_version = "v18.0"
        self._base_url = "https://graph.facebook.com"

    @property
    def name(self) -> str:
        return "whatsapp_cloud"

    async def send(self, to: str, message: str) -> ProviderResponse:
        """
        Send message via WhatsApp Cloud API.

        TODO: Implement with actual API calls.
        """
        # Validate configuration
        if not all([self._phone_number_id, self._access_token]):
            return ProviderResponse.fail(
                error="WhatsApp Cloud provider not configured. Missing credentials.",
                raw_response={"configured": False},
            )

        # TODO: Implement actual WhatsApp Cloud API integration
        # Example implementation:
        # import httpx
        # url = f"{self._base_url}/{self._api_version}/{self._phone_number_id}/messages"
        # headers = {"Authorization": f"Bearer {self._access_token}"}
        # payload = {
        #     "messaging_product": "whatsapp",
        #     "to": to,
        #     "type": "text",
        #     "text": {"body": message}
        # }
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(url, headers=headers, json=payload)
        #     data = response.json()
        #     if response.is_success:
        #         return ProviderResponse.ok(
        #             message_id=data["messages"][0]["id"],
        #             raw_response=data
        #         )
        #     else:
        #         return ProviderResponse.fail(
        #             error=data.get("error", {}).get("message", "Unknown error"),
        #             raw_response=data
        #         )

        raise NotImplementedError(
            "WhatsApp Cloud provider is not yet implemented. "
            "Use MockProvider for development or implement WhatsApp Cloud API integration."
        )

    async def validate_recipient(self, phone: str) -> bool:
        """Validate phone number format for WhatsApp."""
        if not phone:
            return False

        # WhatsApp requires international format without +
        # Example: 5215512345678 (Mexico mobile)
        pattern = r"^[1-9]\d{10,14}$"
        cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
        return bool(re.match(pattern, cleaned))
