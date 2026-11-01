from pydantic import Field

from app.modules.files.typing.enums import UploadKind
from app.shared.common import WireModel


class CreateUploadRequest(WireModel):
    kind: UploadKind
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int = Field(ge=1)
