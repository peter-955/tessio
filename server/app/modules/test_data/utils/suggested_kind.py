import re

from app.modules.test_data.typing.constants import ENDPOINT_VALUE_PATTERN, SENSITIVE_KEY_PATTERN
from app.modules.test_data.typing.enums import DataItemKind


def suggest_kind(key: str, value: str) -> DataItemKind:
    if re.search(SENSITIVE_KEY_PATTERN, key) is not None:
        return DataItemKind.SECRET
    if re.match(ENDPOINT_VALUE_PATTERN, value) is not None:
        return DataItemKind.ENDPOINT
    return DataItemKind.VARIABLE
