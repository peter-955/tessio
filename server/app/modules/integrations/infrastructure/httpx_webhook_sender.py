import asyncio
import ipaddress
import socket
from collections.abc import Mapping
from urllib.parse import urlsplit

import httpx

from app.modules.integrations.domains.webhook_send_result.entity import WebhookSendResult
from app.modules.integrations.ports.webhook_sender import WebhookSender
from app.modules.integrations.typing.constants.webhook import MAX_WEBHOOK_ERROR_LENGTH, WEBHOOK_REQUEST_TIMEOUT_SECONDS
from app.modules.integrations.utils.webhook_url import is_public_address

TIMEOUT_ERROR = "The receiver did not answer within 10 seconds."
UNREACHABLE_ERROR = "The receiver could not be reached."
PRIVATE_ADDRESS_ERROR = "The webhook host resolves to a private, loopback or link-local address."
UNRESOLVED_ERROR = "The webhook host name could not be resolved."
REFUSED_ERROR = "The receiver answered HTTP {status_code}."


class HttpxWebhookSender(WebhookSender):
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def send(self, url: str, body: bytes, headers: Mapping[str, str]) -> WebhookSendResult:
        address_error = await self._check_addresses(url)
        if address_error is not None:
            return WebhookSendResult(is_success=False, response_status=None, error=address_error)
        try:
            response = await self._http_client.post(
                url,
                content=body,
                headers=dict(headers),
                timeout=WEBHOOK_REQUEST_TIMEOUT_SECONDS,
                follow_redirects=False,
            )
        except httpx.TimeoutException:
            return WebhookSendResult(is_success=False, response_status=None, error=TIMEOUT_ERROR)
        except httpx.HTTPError:
            return WebhookSendResult(is_success=False, response_status=None, error=UNREACHABLE_ERROR)
        if response.is_success:
            return WebhookSendResult(is_success=True, response_status=response.status_code, error=None)
        excerpt = response.text[:MAX_WEBHOOK_ERROR_LENGTH].strip()
        error = REFUSED_ERROR.format(status_code=response.status_code)
        return WebhookSendResult(
            is_success=False,
            response_status=response.status_code,
            error=f"{error} {excerpt}"[:MAX_WEBHOOK_ERROR_LENGTH] if excerpt else error,
        )

    @staticmethod
    async def _check_addresses(url: str) -> str | None:
        parts = urlsplit(url)
        host = parts.hostname or ""
        try:
            addresses = await asyncio.get_running_loop().getaddrinfo(host, parts.port or 443, type=socket.SOCK_STREAM)
        except OSError:
            return UNRESOLVED_ERROR
        for address_info in addresses:
            address = ipaddress.ip_address(str(address_info[4][0]).split("%", 1)[0])
            if not is_public_address(address):
                return PRIVATE_ADDRESS_ERROR
        return None
