from datetime import UTC, datetime
from uuid import UUID

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.errors import (
    FailureNotFoundError,
    FailureProjectWithoutJiraError,
    JiraIssueAlreadyLinkedError,
)
from app.modules.failures.ports.jira_bug_source_reader import JiraBugSourceReader
from app.modules.failures.typing.constants import JIRA_CREATE_ISSUE_JOB_ID_TEMPLATE
from app.modules.failures.utils.failure_event import build_failure_changed_event
from app.modules.failures.utils.jira_issue_state import is_jira_issue_request_blocked
from app.modules.jira import FindJiraWriteAccessUseCase, JiraNotConfiguredError, JiraWriteNotAllowedError
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName


class RequestJiraIssueUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        failure_repository: FailureRepository,
        jira_bug_source_reader: JiraBugSourceReader,
        find_jira_write_access: FindJiraWriteAccessUseCase,
        job_queue: JobQueue,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._failure_repository = failure_repository
        self._jira_bug_source_reader = jira_bug_source_reader
        self._find_jira_write_access = find_jira_write_access
        self._job_queue = job_queue
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, failure_id: UUID) -> FailureView:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FAILURE_CREATE_JIRA_ISSUE)
            failure = await self._failure_repository.find_for_update(access.project_id, failure_id)
            if failure is None:
                raise FailureNotFoundError
            if await self._jira_bug_source_reader.find_jira_project_key(access.project_id) is None:
                raise FailureProjectWithoutJiraError
            write_access = await self._find_jira_write_access.execute()
            if write_access is None:
                raise JiraNotConfiguredError
            if write_access.is_create_refused:
                raise JiraWriteNotAllowedError
            if is_jira_issue_request_blocked(failure, now):
                raise JiraIssueAlreadyLinkedError
            requested = failure.model_copy(update={"jira_issue_requested_at": now, "jira_issue_error_code": None})
            await self._failure_repository.save(requested)
            await self._job_queue.add(
                QueueName.JIRA,
                JobName.JIRA_CREATE_ISSUE,
                {"projectId": str(access.project_id), "failureId": str(failure.id), "requestedBy": str(actor.user_id)},
                job_id=JIRA_CREATE_ISSUE_JOB_ID_TEMPLATE.format(failure_id=failure.id),
            )
            view = await self._failure_repository.find_view(access.project_id, failure.id)
            if view is None:
                raise FailureNotFoundError
        await self._live_event_publisher.publish(build_failure_changed_event(view.failure))
        return view
