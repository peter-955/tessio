from datetime import UTC, datetime

from app.modules.labels import TestCaseLabelRepository
from app.modules.test_cases.domains.review_comment.repository import ReviewCommentRepository
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.errors import InvalidTestCaseStatusTransitionError
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.review_policy_reader import ReviewPolicyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.typing.constants import TEST_CASE_STATUS_TRANSITIONS
from app.modules.test_cases.typing.enums import TestCaseStatus
from app.modules.test_cases.utils.available_references import load_available_references
from app.modules.test_cases.utils.readiness import require_ready
from app.modules.test_cases.utils.review_rules import require_no_open_review_comments, require_separate_reviewer
from app.modules.test_cases.utils.test_case_detail import load_test_case_detail
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_current_version, require_locked_test_case
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ChangeTestCaseStatusUseCase:
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
        live_event_publisher: LiveEventPublisher,
        review_comment_repository: ReviewCommentRepository,
        review_policy_reader: ReviewPolicyReader,
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
        self._live_event_publisher = live_event_publisher
        self._review_comment_repository = review_comment_repository
        self._review_policy_reader = review_policy_reader

    async def execute(self, actor: Actor, project_key: str, case_code: str, status: TestCaseStatus) -> TestCaseDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            test_case = await require_locked_test_case(self._test_case_repository, access.project_id, case_code)
            is_changing = status is not test_case.status
            if is_changing:
                if status not in TEST_CASE_STATUS_TRANSITIONS[test_case.status]:
                    raise InvalidTestCaseStatusTransitionError
                updates: dict[str, object] = {
                    "status": status,
                    "status_changed_at": now,
                    "status_changed_by": actor.user_id,
                }
                if status is TestCaseStatus.READY:
                    version = await require_current_version(self._test_case_version_repository, test_case)
                    await require_separate_reviewer(self._review_policy_reader, test_case, version, actor)
                    await require_no_open_review_comments(self._review_comment_repository, test_case)
                    available = await load_available_references(
                        self._data_key_reader, self._test_file_repository, access.project_id, test_case.id
                    )
                    require_ready(version, available.data_keys, available.file_keys)
                    updates |= {
                        "needs_review_at": None,
                        "needs_review_criterion_ids": [],
                        "reviewed_at": now,
                        "reviewed_by": actor.user_id,
                    }
                test_case = test_case.model_copy(update=updates)
                await self._test_case_repository.save(test_case)
            detail = await load_test_case_detail(
                test_case,
                self._test_case_version_repository,
                self._test_file_repository,
                self._story_reader,
                self._criterion_reader,
                self._data_key_reader,
                self._test_case_label_repository,
            )
        if is_changing:
            await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return detail
