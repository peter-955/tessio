from uuid import UUID

from pydantic import Field

from app.shared.common import WireModel
from app.shared.events.live_event_type import LiveEventType


class LiveEvent(WireModel):
    type: LiveEventType
    project_id: UUID | None = None
    user_id: UUID | None = None
    ids: dict[str, str] = Field(default_factory=dict)
