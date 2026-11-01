from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion
from app.modules.stories.domains.sprint.entity import Sprint
from app.modules.stories.domains.story.entity import Story
from app.modules.stories.typing.enums import TestStatus
from app.shared.common import Entity


class StoryDetail(Entity):
    story: Story
    sprint: Sprint | None
    criteria: list[AcceptanceCriterion]
    available_test_statuses: frozenset[TestStatus]
