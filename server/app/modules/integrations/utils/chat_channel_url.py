import ipaddress
from urllib.parse import urlsplit

from app.modules.integrations.typing.constants import (
    BLOCKED_CHAT_HOST_NAMES,
    BLOCKED_CHAT_HOST_SUFFIXES,
    CHAT_WEBHOOK_URL_HINT_MIN_PATH_LENGTH,
    CHAT_WEBHOOK_URL_HINT_SUFFIX_LENGTH,
    CHAT_WEBHOOK_URL_SCHEME,
    NUMERIC_HOST_LABEL_PATTERN,
)


def is_allowed_chat_webhook_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return False
    host = (parts.hostname or "").rstrip(".")
    if parts.scheme != CHAT_WEBHOOK_URL_SCHEME or not host or parts.username or parts.password:
        return False
    if port == 0:
        return False
    if any(character.isspace() for character in url):
        return False
    return is_public_host(host)


def is_public_host(host: str) -> bool:
    try:
        ascii_host = host.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return False
    try:
        address = ipaddress.ip_address(ascii_host)
    except ValueError:
        if is_numeric_host(ascii_host):
            return False
        return (
            "." in ascii_host
            and ascii_host not in BLOCKED_CHAT_HOST_NAMES
            and not ascii_host.endswith(BLOCKED_CHAT_HOST_SUFFIXES)
        )
    return is_public_address(address)


def is_numeric_host(host: str) -> bool:
    return NUMERIC_HOST_LABEL_PATTERN.fullmatch(host.rsplit(".", 1)[-1]) is not None


def is_public_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return is_public_address(address.ipv4_mapped)
    return address.is_global and not address.is_multicast


def build_chat_webhook_url_hint(url: str) -> str:
    parts = urlsplit(url)
    tail = f"{parts.path}?{parts.query}" if parts.query else parts.path
    suffix = tail[-CHAT_WEBHOOK_URL_HINT_SUFFIX_LENGTH:] if len(tail) >= CHAT_WEBHOOK_URL_HINT_MIN_PATH_LENGTH else ""
    return f"{parts.scheme}://{parts.hostname}/…{suffix}"
