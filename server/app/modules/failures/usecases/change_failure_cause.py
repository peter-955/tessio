from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.errors import FailureClosedError, FailureNotFoundError
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.failures.utils.failure_event import build_failure_changed_event
from app.modules.runs import SuspectedCause
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ChangeFailureCauseUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        failure_repository: FailureRepository,
        failure_event_repository: FailureEventRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._failure_repository = failure_repository
        self._failure_event_repository = failure_event_repository
        self._live_event_publisher = live_event_publisher

    async def execute(
        self, actor: Actor, project_key: str, failure_id: UUID, cause: SuspectedCause, reason: str | None
    ) -> FailureView:
        now = datetime.now(UTC)
        cleaned_reason = reason.strip() if reason is not None and reason.strip() else None
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FAILURE_ASSIGN)
            failure = await self._failure_repository.find_for_update(access.project_id, failure_id)
            if failure is None:
                raise FailureNotFoundError
            if failure.status is FailureStatus.VERIFIED:
                raise FailureClosedError
            await self._failure_repository.save(
                failure.model_copy(
                    update={
                        "cause": cause,
                        "cause_reason": cleaned_reason,
                        "cause_changed_at": now,
                        "cause_changed_by": actor.user_id,
                    }
                )
            )
            await self._failure_event_repository.add(
                FailureEvent(
                    id=uuid7(),
                    failure_id=failure.id,
                    kind=FailureEventKind.CAUSE_CHANGED,
                    from_status=None,
                    to_status=None,
                    from_cause=failure.cause,
                    to_cause=cause,
                    case_result_id=None,
                    assignee_id=None,
                    actor_id=actor.user_id,
                    created_at=now,
                )
            )
            view = await self._failure_repository.find_view(access.project_id, failure.id)
            if view is None:
                raise FailureNotFoundError
        await self._live_event_publisher.publish(build_failure_changed_event(view.failure))
        return view
