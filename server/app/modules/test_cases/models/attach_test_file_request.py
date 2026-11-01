from uuid import UUID

from pydantic import Field

from app.modules.test_cases.typing.constants import FILE_KEY_PATTERN
from app.shared.common import WireModel


class AttachTestFileRequest(WireModel):
    key: str = Field(pattern=FILE_KEY_PATTERN)
    file_id: UUID
    base_version_number: int = Field(ge=1)
