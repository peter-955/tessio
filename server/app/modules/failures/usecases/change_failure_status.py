from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.errors import FailureNotFoundError, InvalidFailureTransitionError
from app.modules.failures.typing.constants import MANUAL_STATUS_TRANSITIONS
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.failures.utils.failure_event import (
    build_failure_changed_event,
    build_failure_status_changed_event,
)
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ChangeFailureStatusUseCase:
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

    async def execute(self, actor: Actor, project_key: str, failure_id: UUID, status: FailureStatus) -> FailureView:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(
                access, Capability.FAILURE_MARK_FIXED if status is FailureStatus.FIXED else Capability.FAILURE_VERIFY
            )
            failure = await self._failure_repository.find_for_update(access.project_id, failure_id)
            if failure is None:
                raise FailureNotFoundError
            if status not in MANUAL_STATUS_TRANSITIONS[failure.status]:
                raise InvalidFailureTransitionError
            changed = failure.model_copy(
                update={"status": status, "status_changed_at": now, "status_changed_by": actor.user_id}
            )
            await self._failure_repository.save(changed)
            await self._failure_event_repository.add(
                FailureEvent(
                    id=uuid7(),
                    failure_id=failure.id,
                    kind=FailureEventKind.STATUS_CHANGED,
                    from_status=failure.status,
                    to_status=status,
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
        await self._live_event_publisher.publish(build_failure_status_changed_event(view.failure))
        return view
