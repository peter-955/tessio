import re

from app.modules.test_data.typing.constants import SENSITIVE_KEY_PATTERN
from app.modules.test_data.typing.enums import DataItemKind


def suggest_kind(key: str) -> DataItemKind:
    if re.search(SENSITIVE_KEY_PATTERN, key) is not None:
        return DataItemKind.SECRET
    return DataItemKind.VARIABLE
