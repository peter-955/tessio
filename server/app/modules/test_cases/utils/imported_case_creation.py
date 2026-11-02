from datetime import datetime
from uuid import UUID, uuid7

from app.modules.test_cases.domains.case_import_plan.entity import CaseImportPlan
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_counter.repository import TestCaseCounterRepository
from app.modules.test_cases.typing.enums import TestCaseStatus
from app.modules.test_cases.utils.test_case_version import build_test_case_version


async def create_imported_case(
    imported_case: ImportedCase,
    plan: CaseImportPlan,
    project_id: UUID,
    created_by: UUID,
    now: datetime,
    test_case_repository: TestCaseRepository,
    test_case_counter_repository: TestCaseCounterRepository,
) -> TestCase:
    story = plan.stories_by_key[imported_case.story_key or ""]
    criterion_ids_by_code = {
        criterion.code.upper(): criterion.id
        for criterion in plan.criteria_by_story_id.get(story.id, [])
        if not criterion.is_removed
    }
    criterion_ids = [
        criterion_ids_by_code[code.upper()]
        for code in imported_case.criterion_codes
        if code.upper() in criterion_ids_by_code
    ]
    content = TestCaseContent(
        title=imported_case.title,
        priority=imported_case.priority,
        business_value=imported_case.business_value,
        preconditions=imported_case.preconditions,
        steps=imported_case.steps,
        criterion_ids=list(dict.fromkeys(criterion_ids)),
    )
    number = await test_case_counter_repository.allocate_number(project_id, now)
    test_case_id = uuid7()
    version = build_test_case_version(test_case_id, 1, content, [], created_by, now)
    test_case = TestCase(
        id=test_case_id,
        project_id=project_id,
        story_id=story.id,
        number=number,
        title=version.title,
        priority=version.priority,
        status=TestCaseStatus.DRAFT,
        current_version_id=version.id,
        status_changed_at=None,
        status_changed_by=None,
        needs_review_at=None,
        needs_review_criterion_ids=[],
        reviewed_at=None,
        reviewed_by=None,
        created_by=created_by,
        created_at=now,
    )
    await test_case_repository.create(test_case, version)
    return test_case
