from datetime import UTC, datetime

from app.modules.jira import JiraNotConfiguredError
from app.modules.projects import JiraConnectionChecker
from app.modules.stories.domains.project_sync_state.entity import ProjectSyncState
from app.modules.stories.domains.project_sync_state.repository import ProjectSyncStateRepository
from app.modules.stories.typing.constants import JIRA_SYNC_JOB_ID_TEMPLATE, SYNC_STALE_AFTER
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName


class RequestJiraSyncUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_sync_state_repository: ProjectSyncStateRepository,
        jira_connection_checker: JiraConnectionChecker,
        job_queue: JobQueue,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_sync_state_repository = project_sync_state_repository
        self._jira_connection_checker = jira_connection_checker
        self._job_queue = job_queue
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str) -> ProjectSyncState:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.JIRA_SYNC)
            if not await self._jira_connection_checker.is_configured():
                raise JiraNotConfiguredError
            state = await self._project_sync_state_repository.lock(access.project_id, now)
            progress_at = state.started_at or state.queued_at
            if state.is_in_progress and progress_at is not None and progress_at > now - SYNC_STALE_AFTER:
                return state
            queued_state = state.model_copy(
                update={
                    "status": ProjectSyncStatus.QUEUED,
                    "queued_at": now,
                    "requested_by": actor.user_id,
                    "started_at": None,
                    "finished_at": None,
                    "error_code": None,
                }
            )
            await self._project_sync_state_repository.save(queued_state)
            await self._job_queue.add(
                QueueName.JIRA,
                JobName.JIRA_SYNC_PROJECT,
                {"projectId": str(access.project_id)},
                job_id=JIRA_SYNC_JOB_ID_TEMPLATE.format(project_id=access.project_id),
            )
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.JIRA_SYNC_STARTED,
                project_id=access.project_id,
                ids={"projectKey": access.project_key},
            )
        )
        return queued_state
