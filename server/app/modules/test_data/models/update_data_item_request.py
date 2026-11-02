from pydantic import Field

from app.modules.test_data.typing.constants import (
    DATA_ITEM_KEY_PATTERN,
    MAX_DATA_ITEM_DESCRIPTION_LENGTH,
    MAX_DATA_ITEM_VALUE_LENGTH,
)
from app.modules.test_data.typing.enums import DataItemKind
from app.shared.common import WireModel


class UpdateDataItemRequest(WireModel):
    key: str = Field(pattern=DATA_ITEM_KEY_PATTERN)
    kind: DataItemKind
    value: str | None = Field(default=None, min_length=1, max_length=MAX_DATA_ITEM_VALUE_LENGTH)
    description: str | None = Field(default=None, max_length=MAX_DATA_ITEM_DESCRIPTION_LENGTH)
