import ipaddress
from urllib.parse import urlsplit

from app.modules.integrations.typing.constants.webhook import (
    BLOCKED_WEBHOOK_HOST_NAMES,
    BLOCKED_WEBHOOK_HOST_SUFFIXES,
    WEBHOOK_URL_SCHEME,
)


def is_allowed_webhook_url(url: str) -> bool:
    if any(character.isspace() for character in url):
        return False
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return False
    host = (parts.hostname or "").rstrip(".").lower()
    if parts.scheme != WEBHOOK_URL_SCHEME or not host or parts.username or parts.password or port == 0:
        return False
    return is_public_webhook_host(host)


def is_public_webhook_host(host: str) -> bool:
    try:
        address = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return (
            "." in host and host not in BLOCKED_WEBHOOK_HOST_NAMES and not host.endswith(BLOCKED_WEBHOOK_HOST_SUFFIXES)
        )
    return is_public_address(address)


def is_public_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return is_public_address(address.ipv4_mapped)
    return address.is_global and not address.is_multicast
