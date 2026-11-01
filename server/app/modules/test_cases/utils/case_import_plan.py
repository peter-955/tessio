from uuid import UUID

from app.modules.test_cases.domains.case_import_plan.entity import CaseImportPlan
from app.modules.test_cases.domains.parsed_case_import.entity import ParsedCaseImport
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.utils.case_import_preview import build_preview_items


async def load_case_import_plan(
    parsed_import: ParsedCaseImport,
    project_id: UUID,
    test_case_repository: TestCaseRepository,
    story_reader: StoryReader,
    criterion_reader: CriterionReader,
) -> CaseImportPlan:
    story_keys = frozenset(case.story_key for case in parsed_import.cases if case.story_key is not None)
    stories = await story_reader.list_by_jira_keys(project_id, story_keys) if story_keys else []
    stories_by_key = {story.jira_key.upper(): story for story in stories}
    criteria_by_story_id = {story.id: await criterion_reader.list_for_story(story.id) for story in stories}
    story_ids = frozenset(story.id for story in stories)
    existing_titles = await test_case_repository.list_titles_for_stories(project_id, story_ids) if story_ids else set()
    return CaseImportPlan(
        items=build_preview_items(parsed_import.cases, stories_by_key, criteria_by_story_id, existing_titles),
        stories_by_key=stories_by_key,
        criteria_by_story_id=criteria_by_story_id,
    )
