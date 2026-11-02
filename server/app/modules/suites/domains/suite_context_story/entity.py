from app.modules.story_context import ContextCase, ContextCriterion, ContextStory
from app.shared.common import Entity


class SuiteContextStory(Entity):
    story: ContextStory
    criteria: list[ContextCriterion]
    cases: list[ContextCase]
