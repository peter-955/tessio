import hashlib

import httpx

from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.shared.logging import get_logger

PWNED_PASSWORDS_RANGE_URL = "https://api.pwnedpasswords.com/range/"
HASH_PREFIX_LENGTH = 5

log = get_logger(__name__)


class PwnedPasswordsChecker(BreachedPasswordChecker):
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def is_breached(self, password: str) -> bool:
        password_hash = hashlib.sha1(password.encode(), usedforsecurity=False).hexdigest().upper()
        prefix, suffix = password_hash[:HASH_PREFIX_LENGTH], password_hash[HASH_PREFIX_LENGTH:]
        try:
            response = await self._http_client.get(
                f"{PWNED_PASSWORDS_RANGE_URL}{prefix}", headers={"Add-Padding": "true"}
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            log.warning("breached_password_check.skipped", extra={"reason": type(error).__name__})
            return False
        return any(self._is_breached_line(line, suffix) for line in response.text.splitlines())

    def _is_breached_line(self, line: str, suffix: str) -> bool:
        line_suffix, _, count = line.strip().partition(":")
        return line_suffix == suffix and count.strip() not in {"", "0"}
