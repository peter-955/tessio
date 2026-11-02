from uuid import uuid7

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.failures.utils.failure_event import build_failure_opened_event, build_failure_status_changed_event
from app.modules.runs import CaseResultRecordedHandler, RecordedCaseResult, ResultStatus
from app.shared.common import Transaction
from app.shared.events import LiveEvent


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

    async def handle(self, recorded: RecordedCaseResult) -> list[LiveEvent]:
        if recorded.status is not ResultStatus.FAILED:
            return []
        async with self._transaction.begin():
            await self._failure_repository.lock_test_case(recorded.test_case_id)
            active = await self._failure_repository.find_active_for_update(recorded.test_case_id)
            if active is None:
                opened = await self._open(recorded)
                return [build_failure_opened_event(opened, str(recorded.run_id))]
            if active.status is FailureStatus.FIXED:
                reopened = await self._reopen(active, recorded)
                return [build_failure_status_changed_event(reopened)]
            await self._fail_again(active, recorded)
        return []

    async def _open(self, recorded: RecordedCaseResult) -> Failure:
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
            cause=recorded.suspected_cause,
            cause_reason=recorded.cause_reason,
            cause_changed_at=None,
            cause_changed_by=None,
            created_at=recorded.recorded_at,
        )
        await self._failure_repository.add(failure)
        await self._add_event(failure, recorded, FailureEventKind.OPENED, None, FailureStatus.OPEN)
        return failure

    async def _reopen(self, failure: Failure, recorded: RecordedCaseResult) -> Failure:
        reopened = failure.model_copy(
            update={
                "status": FailureStatus.REOPENED,
                "latest_case_result_id": recorded.case_result_id,
                "status_changed_at": recorded.recorded_at,
                "status_changed_by": None,
                **self._recorded_cause(failure, recorded),
            }
        )
        await self._failure_repository.save(reopened)
        await self._add_event(
            reopened, recorded, FailureEventKind.STATUS_CHANGED, FailureStatus.FIXED, FailureStatus.REOPENED
        )
        return reopened

    async def _fail_again(self, failure: Failure, recorded: RecordedCaseResult) -> None:
        updated = failure.model_copy(
            update={"latest_case_result_id": recorded.case_result_id, **self._recorded_cause(failure, recorded)}
        )
        await self._failure_repository.save(updated)
        await self._add_event(updated, recorded, FailureEventKind.FAILED_AGAIN, None, None)

    @staticmethod
    def _recorded_cause(failure: Failure, recorded: RecordedCaseResult) -> dict[str, object]:
        if failure.cause_changed_by is not None or recorded.suspected_cause is None:
            return {}
        return {"cause": recorded.suspected_cause, "cause_reason": recorded.cause_reason}

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
