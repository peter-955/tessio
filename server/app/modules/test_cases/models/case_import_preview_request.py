from uuid import UUID

from app.shared.common import WireModel


class CaseImportPreviewRequest(WireModel):
    file_id: UUID
