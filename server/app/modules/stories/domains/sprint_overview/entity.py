from app.modules.stories.domains.sprint.entity import Sprint
from app.shared.common import Entity


class SprintOverview(Entity):
    sprint: Sprint
    story_count: int
