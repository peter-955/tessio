from app.modules.runs import SkippedRunCase
from app.modules.story_context import ContextEnvironment, DataEntry
from app.modules.suites.domains.suite_context_story.entity import SuiteContextStory
from app.modules.suites.domains.test_suite.entity import TestSuite
from app.shared.common import Entity


class SuiteContext(Entity):
    suite: TestSuite
    stories: list[SuiteContextStory]
    skipped_cases: list[SkippedRunCase]
    data_entries: list[DataEntry]
    environments: list[ContextEnvironment]
