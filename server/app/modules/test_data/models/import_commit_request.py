from uuid import UUID

from pydantic import Field

from app.modules.test_data.models.import_commit_item_request import ImportCommitItemRequest
from app.modules.test_data.typing.constants import MAX_IMPORT_ITEMS
from app.shared.common import WireModel


class ImportCommitRequest(WireModel):
    file_id: UUID
    environment_id: UUID | None = None
    items: list[ImportCommitItemRequest] = Field(min_length=1, max_length=MAX_IMPORT_ITEMS)
