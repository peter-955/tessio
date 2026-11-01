import re

from app.modules.test_data.typing.constants import DATA_ITEM_KEY_PATTERN


def is_valid_data_item_key(key: str) -> bool:
    return re.fullmatch(DATA_ITEM_KEY_PATTERN, key) is not None
