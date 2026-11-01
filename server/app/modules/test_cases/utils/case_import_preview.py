from collections.abc import Mapping, Sequence
from uuid import UUID

from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.domains.case_import_preview_item.entity import CaseImportPreviewItem
from app.modules.test_cases.domains.case_story.entity import CaseStory
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.typing.constants import MAX_STEPS, MAX_TEXT_LENGTH, MAX_TITLE_LENGTH
from app.modules.test_cases.typing.enums import CaseImportProblem


def is_text_too_long(case: ImportedCase) -> bool:
    texts = [
        case.business_value,
        case.preconditions,
        *(text for step in case.steps for text in (step.action, step.expected)),
    ]
    return len(case.title) > MAX_TITLE_LENGTH or any(text is not None and len(text) > MAX_TEXT_LENGTH for text in texts)


def find_problem(case: ImportedCase, story: CaseStory | None) -> CaseImportProblem | None:
    if case.story_key is None:
        return CaseImportProblem.STORY_KEY_MISSING
    if story is None:
        return CaseImportProblem.STORY_NOT_FOUND
    if len(case.steps) > MAX_STEPS:
        return CaseImportProblem.TOO_MANY_STEPS
    if is_text_too_long(case):
        return CaseImportProblem.TEXT_TOO_LONG
    return None


def list_current_codes(criteria: Sequence[CaseCriterion]) -> frozenset[str]:
    return frozenset(criterion.code.upper() for criterion in criteria if not criterion.is_removed)


def build_preview_items(
    cases: Sequence[ImportedCase],
    stories_by_key: Mapping[str, CaseStory],
    criteria_by_story_id: Mapping[UUID, Sequence[CaseCriterion]],
    existing_titles: set[tuple[UUID, str]],
) -> list[CaseImportPreviewItem]:
    seen_titles = set(existing_titles)
    items = []
    for index, case in enumerate(cases):
        story = None if case.story_key is None else stories_by_key.get(case.story_key)
        current_codes = frozenset() if story is None else list_current_codes(criteria_by_story_id.get(story.id, []))
        title_key = None if story is None else (story.id, case.title.lower())
        is_duplicate = title_key is not None and title_key in seen_titles
        if title_key is not None:
            seen_titles.add(title_key)
        items.append(
            CaseImportPreviewItem(
                index=index,
                location=case.location,
                story_key=case.story_key,
                title=case.title,
                priority=case.priority,
                step_count=len(case.steps),
                criterion_codes=case.criterion_codes,
                unknown_criterion_codes=[code for code in case.criterion_codes if code.upper() not in current_codes],
                is_duplicate=is_duplicate,
                problem=find_problem(case, story),
            )
        )
    return items
