from uuid import UUID

from app.shared.common import WireModel


class ReadyEvent(WireModel):
    user_id: UUID
