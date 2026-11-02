from datetime import UTC, datetime
from uuid import UUID

from app.modules.labels import Label, LabelRepository, TestCaseLabelRepository, require_project_labels
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_locked_test_case
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class SetTestCaseLabelsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        label_repository: LabelRepository,
        test_case_label_repository: TestCaseLabelRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._label_repository = label_repository
        self._test_case_label_repository = test_case_label_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, case_code: str, label_ids: list[UUID]) -> list[Label]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            test_case = await require_locked_test_case(self._test_case_repository, access.project_id, case_code)
            labels = await require_project_labels(self._label_repository, access.project_id, label_ids)
            current_labels = await self._test_case_label_repository.list_for_case(test_case.id)
            is_changing = {label.id for label in labels} != {label.id for label in current_labels}
            if is_changing:
                await self._test_case_label_repository.replace_for_case(
                    test_case.id, [label.id for label in labels], datetime.now(UTC)
                )
        if is_changing:
            await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return labels
