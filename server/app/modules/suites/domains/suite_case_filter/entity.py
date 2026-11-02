from uuid import UUID

from app.modules.test_cases import TestCasePriority
from app.shared.common import Entity


class SuiteCaseFilter(Entity):
    label_names: list[str]
    priorities: list[TestCasePriority]
    story_id: UUID | None
    sprint_id: UUID | None

    @property
    def is_empty(self) -> bool:
        return not self.label_names and not self.priorities and self.story_id is None and self.sprint_id is None
