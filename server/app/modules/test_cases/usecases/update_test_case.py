from datetime import UTC, datetime

from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_changes.entity import TestCaseChanges
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.errors import TestCaseDeprecatedError, TestCaseVersionConflictError
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.typing.enums import TestCaseStatus
from app.modules.test_cases.utils.available_references import load_available_references
from app.modules.test_cases.utils.criterion_links import require_linkable
from app.modules.test_cases.utils.readiness import require_ready
from app.modules.test_cases.utils.test_case_changes import build_version_content, merge_changes
from app.modules.test_cases.utils.test_case_detail import load_test_case_detail
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_current_version, require_locked_test_case
from app.modules.test_cases.utils.test_case_version import build_test_case_version
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateTestCaseUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_case_version_repository: TestCaseVersionRepository,
        test_file_repository: TestFileRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        data_key_reader: DataKeyReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_version_repository = test_case_version_repository
        self._test_file_repository = test_file_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._data_key_reader = data_key_reader
        self._live_event_publisher = live_event_publisher

    async def execute(
        self, actor: Actor, project_key: str, case_code: str, base_version_number: int, changes: TestCaseChanges
    ) -> TestCaseDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            test_case = await require_locked_test_case(self._test_case_repository, access.project_id, case_code)
            if test_case.is_deprecated:
                raise TestCaseDeprecatedError
            current_version = await require_current_version(self._test_case_version_repository, test_case)
            if base_version_number != current_version.number:
                raise TestCaseVersionConflictError
            current_content = build_version_content(current_version)
            merged_content = merge_changes(current_content, changes)
            criterion_ids = require_linkable(
                merged_content.criterion_ids,
                await self._criterion_reader.list_for_story(test_case.story_id),
                frozenset(current_version.criterion_ids),
            )
            content = merged_content.model_copy(update={"criterion_ids": criterion_ids})
            is_changing = content != current_content
            if is_changing:
                version = build_test_case_version(
                    test_case.id,
                    current_version.number + 1,
                    content,
                    current_version.file_version_ids,
                    actor.user_id,
                    now,
                )
                if test_case.status is TestCaseStatus.READY:
                    available = await load_available_references(
                        self._data_key_reader, self._test_file_repository, access.project_id, test_case.id
                    )
                    require_ready(version, available.data_keys, available.file_keys)
                test_case = test_case.model_copy(
                    update={"title": version.title, "priority": version.priority, "current_version_id": version.id}
                )
                await self._test_case_repository.add_version(test_case, version)
            detail = await load_test_case_detail(
                test_case,
                self._test_case_version_repository,
                self._test_file_repository,
                self._story_reader,
                self._criterion_reader,
                self._data_key_reader,
            )
        if is_changing:
            await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return detail
