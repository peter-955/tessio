from datetime import UTC, datetime
from uuid import uuid7

from app.modules.labels import TestCaseLabelRepository
from app.modules.test_cases.domains.quarantine_event.entity import QuarantineEvent
from app.modules.test_cases.domains.quarantine_event.repository import QuarantineEventRepository
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_quality.repository import TestCaseQualityRepository
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.typing.enums import QuarantineEventKind
from app.modules.test_cases.utils.test_case_detail import load_test_case_detail
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_locked_test_case
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class QuarantineTestCaseUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_case_quality_repository: TestCaseQualityRepository,
        quarantine_event_repository: QuarantineEventRepository,
        test_case_version_repository: TestCaseVersionRepository,
        test_file_repository: TestFileRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        data_key_reader: DataKeyReader,
        test_case_label_repository: TestCaseLabelRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_quality_repository = test_case_quality_repository
        self._quarantine_event_repository = quarantine_event_repository
        self._test_case_version_repository = test_case_version_repository
        self._test_file_repository = test_file_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._data_key_reader = data_key_reader
        self._test_case_label_repository = test_case_label_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, case_code: str, reason: str | None) -> TestCaseDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_QUARANTINE)
            test_case = await require_locked_test_case(self._test_case_repository, access.project_id, case_code)
            is_changing = not test_case.is_quarantined
            if is_changing:
                test_case = test_case.model_copy(
                    update={"quarantined_at": now, "quarantined_by": actor.user_id, "quarantine_reason": reason}
                )
                await self._test_case_quality_repository.save(test_case)
                await self._quarantine_event_repository.add(
                    QuarantineEvent(
                        id=uuid7(),
                        test_case_id=test_case.id,
                        kind=QuarantineEventKind.QUARANTINED,
                        actor_id=actor.user_id,
                        reason=reason,
                        created_at=now,
                    )
                )
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
