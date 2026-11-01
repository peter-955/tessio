from uuid import UUID

from app.shared.common import WireModel


class SignedUploadResponse(WireModel):
    file_id: UUID
    url: str
    fields: dict[str, str]
    object_key: str
