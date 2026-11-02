from uuid import UUID

from app.modules.plans.typing.enums import PlanItemKind
from app.shared.common import Entity


class PlanItem(Entity):
    test_suite_id: UUID | None
    story_id: UUID | None

    @property
    def kind(self) -> PlanItemKind:
        return PlanItemKind.SUITE if self.test_suite_id is not None else PlanItemKind.STORY
