import httpx
from pydantic import JsonValue

from app.modules.integrations.errors import ChatWebhookRejectedError
from app.modules.integrations.ports.chat_webhook_sender import ChatWebhookSender

TOO_MANY_REQUESTS = 429
FIRST_SERVER_ERROR = 500
TIMEOUT_REASON = "Slack or Teams did not answer in time."
UNREACHABLE_REASON = "Slack or Teams could not be reached."
REFUSED_REASON = "Slack or Teams answered HTTP {status_code}."


class HttpxChatWebhookSender(ChatWebhookSender):
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def send(self, webhook_url: str, payload: dict[str, JsonValue]) -> None:
        try:
            response = await self._http_client.post(webhook_url, json=payload, follow_redirects=False)
        except httpx.TimeoutException:
            raise ChatWebhookRejectedError(TIMEOUT_REASON, is_retryable=True) from None
        except httpx.HTTPError:
            raise ChatWebhookRejectedError(UNREACHABLE_REASON, is_retryable=True) from None
        if response.is_success:
            return
        status_code = response.status_code
        raise ChatWebhookRejectedError(
            REFUSED_REASON.format(status_code=status_code),
            is_retryable=status_code == TOO_MANY_REQUESTS or status_code >= FIRST_SERVER_ERROR,
        )
