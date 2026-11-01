from app.modules.story_context.domains.context_case.entity import ContextCase
from app.modules.story_context.domains.context_criterion.entity import ContextCriterion
from app.modules.story_context.domains.context_environment.entity import ContextEnvironment
from app.modules.story_context.domains.context_story.entity import ContextStory
from app.modules.story_context.domains.data_entry.entity import DataEntry
from app.shared.common import Entity


class StoryContext(Entity):
    story: ContextStory
    criteria: list[ContextCriterion]
    cases: list[ContextCase]
    other_case_count: int
    data_entries: list[DataEntry]
    environments: list[ContextEnvironment]
