from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion
from app.modules.stories.domains.sprint.entity import Sprint
from app.modules.stories.domains.story.entity import Story
from app.modules.stories.domains.story_detail.entity import StoryDetail
from app.modules.stories.utils.test_status_transition import list_available_test_statuses
from app.shared.permissions import ProjectAccess


def build_story_detail(
    access: ProjectAccess, story: Story, sprint: Sprint | None, criteria: list[AcceptanceCriterion]
) -> StoryDetail:
    return StoryDetail(
        story=story,
        sprint=sprint,
        criteria=sorted(criteria, key=lambda criterion: criterion.position),
        available_test_statuses=list_available_test_statuses(access, story.test_status),
    )
