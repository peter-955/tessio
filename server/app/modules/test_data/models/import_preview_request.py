from uuid import UUID

from app.shared.common import WireModel


class ImportPreviewRequest(WireModel):
    file_id: UUID
    environment_id: UUID | None = None
