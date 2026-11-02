from uuid import UUID

from app.modules.stories.domains.story.entity import Story
from app.shared.events import LiveEvent, LiveEventType


def build_story_changed_event(project_id: UUID, story: Story) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.STORY_CHANGED,
        project_id=project_id,
        ids={"storyId": str(story.id), "jiraKey": story.jira_key},
    )
