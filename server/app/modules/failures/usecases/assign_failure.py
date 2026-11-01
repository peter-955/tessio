from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.errors import AssigneeNotActiveMemberError, FailureClosedError, FailureNotFoundError
from app.modules.failures.ports.failure_assignee_directory import FailureAssigneeDirectory
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.failures.utils.failure_event import build_failure_changed_event
from app.modules.notifications import FailureAssignedPayload, SendNotificationUseCase
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class AssignFailureUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        failure_repository: FailureRepository,
        failure_event_repository: FailureEventRepository,
        failure_assignee_directory: FailureAssigneeDirectory,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._failure_repository = failure_repository
        self._failure_event_repository = failure_event_repository
        self._failure_assignee_directory = failure_assignee_directory
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, failure_id: UUID, assignee_id: UUID | None) -> FailureView:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FAILURE_ASSIGN)
            failure = await self._failure_repository.find_for_update(access.project_id, failure_id)
            if failure is None:
                raise FailureNotFoundError
            if failure.status is FailureStatus.VERIFIED:
                raise FailureClosedError
            if assignee_id is not None and not await self._failure_assignee_directory.is_active_member(
                access.project_id, assignee_id
            ):
                raise AssigneeNotActiveMemberError
            is_changing = assignee_id != failure.assignee_id
            if is_changing:
                await self._failure_repository.save(failure.model_copy(update={"assignee_id": assignee_id}))
                await self._failure_event_repository.add(
                    FailureEvent(
                        id=uuid7(),
                        failure_id=failure.id,
                        kind=FailureEventKind.UNASSIGNED if assignee_id is None else FailureEventKind.ASSIGNED,
                        from_status=None,
                        to_status=None,
                        case_result_id=None,
                        assignee_id=failure.assignee_id if assignee_id is None else assignee_id,
                        actor_id=actor.user_id,
                        created_at=now,
                    )
                )
            view = await self._failure_repository.find_view(access.project_id, failure.id)
            if view is None:
                raise FailureNotFoundError
        if not is_changing:
            return view
        if assignee_id is not None:
            await self._send_notification.execute(
                view.failure.project_id,
                FailureAssignedPayload(
                    failure_id=view.failure.id,
                    test_case_id=view.failure.test_case_id,
                    test_case_code=view.test_case_code,
                    test_case_title=view.test_case_title,
                    story_jira_key=view.story_jira_key,
                ),
                actor_id=actor.user_id,
                recipient_ids={assignee_id},
            )
        await self._live_event_publisher.publish(build_failure_changed_event(view.failure))
        return view
