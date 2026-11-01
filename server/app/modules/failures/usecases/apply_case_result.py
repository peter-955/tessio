from uuid import uuid7

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.runs import CaseResultRecordedHandler, RecordedCaseResult, ResultStatus
from app.shared.common import Transaction


class ApplyCaseResultUseCase(CaseResultRecordedHandler):
    def __init__(
        self,
        transaction: Transaction,
        failure_repository: FailureRepository,
        failure_event_repository: FailureEventRepository,
    ) -> None:
        self._transaction = transaction
        self._failure_repository = failure_repository
        self._failure_event_repository = failure_event_repository

    async def handle(self, recorded: RecordedCaseResult) -> None:
        if recorded.status is not ResultStatus.FAILED:
            return
        async with self._transaction.begin():
            await self._failure_repository.lock_test_case(recorded.test_case_id)
            active = await self._failure_repository.find_active_for_update(recorded.test_case_id)
            if active is None:
                await self._open(recorded)
            elif active.status is FailureStatus.FIXED:
                await self._reopen(active, recorded)
            else:
                await self._fail_again(active, recorded)

    async def _open(self, recorded: RecordedCaseResult) -> None:
        failure = Failure(
            id=uuid7(),
            project_id=recorded.project_id,
            story_id=recorded.story_id,
            test_case_id=recorded.test_case_id,
            opened_by_case_result_id=recorded.case_result_id,
            latest_case_result_id=recorded.case_result_id,
            assignee_id=None,
            status=FailureStatus.OPEN,
            status_changed_at=None,
            status_changed_by=None,
            created_at=recorded.recorded_at,
        )
        await self._failure_repository.add(failure)
        await self._add_event(failure, recorded, FailureEventKind.OPENED, None, FailureStatus.OPEN)

    async def _reopen(self, failure: Failure, recorded: RecordedCaseResult) -> None:
        reopened = failure.model_copy(
            update={
                "status": FailureStatus.REOPENED,
                "latest_case_result_id": recorded.case_result_id,
                "status_changed_at": recorded.recorded_at,
                "status_changed_by": None,
            }
        )
        await self._failure_repository.save(reopened)
        await self._add_event(
            reopened, recorded, FailureEventKind.STATUS_CHANGED, FailureStatus.FIXED, FailureStatus.REOPENED
        )

    async def _fail_again(self, failure: Failure, recorded: RecordedCaseResult) -> None:
        updated = failure.model_copy(update={"latest_case_result_id": recorded.case_result_id})
        await self._failure_repository.save(updated)
        await self._add_event(updated, recorded, FailureEventKind.FAILED_AGAIN, None, None)

    async def _add_event(
        self,
        failure: Failure,
        recorded: RecordedCaseResult,
        kind: FailureEventKind,
        from_status: FailureStatus | None,
        to_status: FailureStatus | None,
    ) -> None:
        await self._failure_event_repository.add(
            FailureEvent(
                id=uuid7(),
                failure_id=failure.id,
                kind=kind,
                from_status=from_status,
                to_status=to_status,
                case_result_id=recorded.case_result_id,
                assignee_id=None,
                actor_id=None,
                created_at=recorded.recorded_at,
            )
        )
