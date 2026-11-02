from datetime import UTC, datetime
from uuid import uuid7

from app.modules.labels import TestCaseLabelRepository
from app.modules.shared_steps import SharedStepRepository
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_counter.repository import TestCaseCounterRepository
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.errors import StoryNotFoundError
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.typing.enums import TestCaseStatus
from app.modules.test_cases.utils.case_content_check import check_case_content
from app.modules.test_cases.utils.criterion_links import require_linkable
from app.modules.test_cases.utils.test_case_detail import load_test_case_detail
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_version import build_test_case_version
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateTestCaseUseCase:
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
        test_case_label_repository: TestCaseLabelRepository,
        test_case_counter_repository: TestCaseCounterRepository,
        live_event_publisher: LiveEventPublisher,
        shared_step_repository: SharedStepRepository,
        secret_value_reader: SecretValueReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_version_repository = test_case_version_repository
        self._test_file_repository = test_file_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._data_key_reader = data_key_reader
        self._test_case_label_repository = test_case_label_repository
        self._test_case_counter_repository = test_case_counter_repository
        self._live_event_publisher = live_event_publisher
        self._shared_step_repository = shared_step_repository
        self._secret_value_reader = secret_value_reader

    async def execute(self, actor: Actor, project_key: str, story_key: str, content: TestCaseContent) -> TestCaseDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            story = await self._story_reader.find_by_jira_key(access.project_id, story_key.strip().upper())
            if story is None:
                raise StoryNotFoundError
            criterion_ids = require_linkable(
                content.criterion_ids, await self._criterion_reader.list_for_story(story.id), frozenset()
            )
            shared_data_keys = await check_case_content(
                self._shared_step_repository, self._secret_value_reader, access.project_id, content, None
            )
            number = await self._test_case_counter_repository.allocate_number(access.project_id, now)
            test_case_id = uuid7()
            version = build_test_case_version(
                test_case_id,
                1,
                content.model_copy(update={"criterion_ids": criterion_ids}),
                [],
                actor.user_id,
                now,
                shared_data_keys,
            )
            test_case = TestCase(
                id=test_case_id,
                project_id=access.project_id,
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
                created_by=actor.user_id,
                created_at=now,
            )
            await self._test_case_repository.create(test_case, version)
            detail = await load_test_case_detail(
                test_case,
                self._test_case_version_repository,
                self._test_file_repository,
                self._story_reader,
                self._criterion_reader,
                self._data_key_reader,
                self._test_case_label_repository,
            )
        await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return detail
