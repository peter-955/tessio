from uuid import UUID

from app.shared.common import WireModel


class ManualRerunRequest(WireModel):
    environment_id: UUID | None = None
