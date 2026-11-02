from datetime import datetime
from uuid import UUID

from app.modules.plans.typing.enums import PlanItemKind
from app.shared.common import WireModel


class PlanItemResponse(WireModel):
    position: int
    kind: PlanItemKind
    suite_id: UUID | None
    story_id: UUID | None
    name: str
    story_jira_key: str | None
    archived_at: datetime | None
    case_count: int
