from uuid import UUID

from app.modules.gaps.domains.gap_recipient.entity import GapRecipient
from app.modules.gaps.typing.enums import GapStatus
from app.shared.common import Entity


class GapFilter(Entity):
    story_id: UUID | None = None
    status: GapStatus | None = None
    assigned_to: GapRecipient | None = None
