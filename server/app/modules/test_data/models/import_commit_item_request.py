from pydantic import Field

from app.modules.test_data.typing.constants import DATA_ITEM_KEY_PATTERN
from app.modules.test_data.typing.enums import DataItemKind
from app.shared.common import WireModel


class ImportCommitItemRequest(WireModel):
    key: str = Field(pattern=DATA_ITEM_KEY_PATTERN)
    kind: DataItemKind
