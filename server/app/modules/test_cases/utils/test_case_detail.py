from app.modules.labels import TestCaseLabelRepository
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.errors import StoryNotFoundError
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.utils.readiness import find_unknown_references
from app.modules.test_cases.utils.test_case_lookup import require_current_version


async def load_test_case_detail(
    test_case: TestCase,
    test_case_version_repository: TestCaseVersionRepository,
    test_file_repository: TestFileRepository,
    story_reader: StoryReader,
    criterion_reader: CriterionReader,
    data_key_reader: DataKeyReader,
    test_case_label_repository: TestCaseLabelRepository,
) -> TestCaseDetail:
    story = await story_reader.find_by_id(test_case.project_id, test_case.story_id)
    if story is None:
        raise StoryNotFoundError
    version = await require_current_version(test_case_version_repository, test_case)
    criteria = await criterion_reader.list_by_ids(version.criterion_ids) if version.criterion_ids else []
    files = await test_file_repository.list_for_case(test_case.id)
    data_keys = await data_key_reader.list_keys(test_case.project_id)
    file_keys = frozenset(file.test_file.key for file in files)
    labels = await test_case_label_repository.list_for_case(test_case.id)
    return TestCaseDetail(
        test_case=test_case,
        story=story,
        version=version,
        criteria=sorted(criteria, key=lambda criterion: criterion.position),
        files=files,
        unknown_references=find_unknown_references(version, data_keys, file_keys),
        labels=labels,
    )
