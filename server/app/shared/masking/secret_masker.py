import re
from collections.abc import Collection

from app.shared.masking.masked_value import MASKED_VALUE


class SecretMasker:
    def __init__(self, secret_values: Collection[str]) -> None:
        values = sorted({value for value in secret_values if value}, key=len, reverse=True)
        self._pattern = re.compile("|".join(re.escape(value) for value in values)) if values else None

    def mask(self, text: str) -> str:
        if self._pattern is None:
            return text
        return self._pattern.sub(MASKED_VALUE, text)

    def mask_optional(self, text: str | None) -> str | None:
        return None if text is None else self.mask(text)
