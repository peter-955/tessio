from datetime import datetime
from uuid import UUID

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.utils.failure_event import build_failure_changed_event
from app.modules.jira import JiraClient, JiraCredentials, JiraIssueStatus
from app.modules.stories import JiraIssueStatusRefresher
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher


class RefreshFailureJiraIssuesUseCase(JiraIssueStatusRefresher):
    def __init__(
        self,
        transaction: Transaction,
        failure_repository: FailureRepository,
        jira_client: JiraClient,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._failure_repository = failure_repository
        self._jira_client = jira_client
        self._live_event_publisher = live_event_publisher

    async def refresh(self, project_id: UUID, credentials: JiraCredentials, now: datetime) -> None:
        async with self._transaction.begin():
            failures = await self._failure_repository.list_active_with_jira_issue(project_id)
        issue_keys = [failure.jira_issue_key for failure in failures if failure.jira_issue_key is not None]
        if not issue_keys:
            return
        statuses = {
            status.key: status for status in await self._jira_client.list_issue_statuses(credentials, issue_keys)
        }
        changed: list[Failure] = []
        async with self._transaction.begin():
            for failure in failures:
                status = None if failure.jira_issue_key is None else statuses.get(failure.jira_issue_key)
                if status is None or not self._is_changed(failure, status):
                    continue
                locked = await self._failure_repository.find_for_update(project_id, failure.id)
                if locked is None or locked.jira_issue_key != failure.jira_issue_key:
                    continue
                refreshed = locked.model_copy(
                    update={
                        "jira_issue_status": status.status_name,
                        "jira_issue_done_at": (locked.jira_issue_done_at or now) if status.is_done else None,
                    }
                )
                await self._failure_repository.save(refreshed)
                changed.append(refreshed)
        for failure in changed:
            await self._live_event_publisher.publish(build_failure_changed_event(failure))

    @staticmethod
    def _is_changed(failure: Failure, status: JiraIssueStatus) -> bool:
        return failure.jira_issue_status != status.status_name or failure.is_done_in_jira != status.is_done
