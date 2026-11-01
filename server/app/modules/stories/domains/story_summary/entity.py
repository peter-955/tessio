from app.modules.stories.domains.story.entity import Story
from app.shared.common import Entity


class StorySummary(Entity):
    story: Story
    sprint_name: str | None
    criterion_count: int
