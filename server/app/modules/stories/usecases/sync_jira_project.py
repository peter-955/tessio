from datetime import datetime
from uuid import UUID, uuid7

from app.modules.jira import (
    JiraClient,
    JiraCredentials,
    JiraIssue,
    JiraSprint,
    JiraSprintState,
    LoadJiraCredentialsUseCase,
    RefreshJiraWriteAccessUseCase,
)
from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.domains.fetched_story.entity import FetchedStory
from app.modules.stories.domains.project_sync_state.repository import ProjectSyncStateRepository
from app.modules.stories.domains.sprint.entity import Sprint
from app.modules.stories.domains.sprint.repository import SprintRepository
from app.modules.stories.domains.story.entity import Story
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.sync_target.entity import SyncTarget
from app.modules.stories.ports.criteria_changed_handler import CriteriaChangedHandler
from app.modules.stories.ports.jira_issue_status_refresher import JiraIssueStatusRefresher
from app.modules.stories.ports.sync_target_reader import SyncTargetReader
from app.modules.stories.typing.constants import JIRA_BROWSE_URL_TEMPLATE
from app.modules.stories.typing.enums import ProjectSyncStatus, SprintState, TestStatus
from app.modules.stories.utils.acceptance_criteria_parser import parse_acceptance_criteria
from app.modules.stories.utils.criteria_merge import merge_acceptance_criteria
from app.modules.stories.utils.sprint_issues_jql import build_sprint_issues_jql
from app.modules.stories.utils.sprint_scope import assign_stories_to_sprints, is_sprint_in_scope
from app.shared.common import TessioError, Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.logging import get_logger
from app.shared.typing.enums import ErrorCode

log = get_logger(__name__)


class SyncJiraProjectUseCase:
    def __init__(
        self,
        transaction: Transaction,
        sync_target_reader: SyncTargetReader,
        project_sync_state_repository: ProjectSyncStateRepository,
        sprint_repository: SprintRepository,
        story_repository: StoryRepository,
        acceptance_criterion_repository: AcceptanceCriterionRepository,
        load_jira_credentials: LoadJiraCredentialsUseCase,
        jira_client: JiraClient,
        criteria_changed_handler: CriteriaChangedHandler,
        live_event_publisher: LiveEventPublisher,
        refresh_jira_write_access: RefreshJiraWriteAccessUseCase,
        jira_issue_status_refresher: JiraIssueStatusRefresher,
    ) -> None:
        self._transaction = transaction
        self._sync_target_reader = sync_target_reader
        self._project_sync_state_repository = project_sync_state_repository
        self._sprint_repository = sprint_repository
        self._story_repository = story_repository
        self._acceptance_criterion_repository = acceptance_criterion_repository
        self._load_jira_credentials = load_jira_credentials
        self._jira_client = jira_client
        self._criteria_changed_handler = criteria_changed_handler
        self._live_event_publisher = live_event_publisher
        self._refresh_jira_write_access = refresh_jira_write_access
        self._jira_issue_status_refresher = jira_issue_status_refresher

    async def execute(self, project_id: UUID, now: datetime) -> None:
        target = await self._start(project_id, now)
        if target is None:
            return
        if target.is_archived:
            await self._fail(target, ErrorCode.PROJECT_ARCHIVED, now)
            return
        if target.jira_project_key is None or target.jira_board_id is None:
            await self._fail(target, ErrorCode.JIRA_NOT_CONFIGURED, now)
            return
        jira_project_key = target.jira_project_key
        jira_board_id = target.jira_board_id
        try:
            credentials = await self._load_jira_credentials.execute()
            jira_sprints = await self._jira_client.list_sprints(credentials, jira_board_id, frozenset(JiraSprintState))
            in_scope_sprints = [jira_sprint for jira_sprint in jira_sprints if is_sprint_in_scope(jira_sprint, now)]
            issues_by_sprint: dict[JiraSprint, list[JiraIssue]] = {}
            for jira_sprint in in_scope_sprints:
                issues_by_sprint[jira_sprint] = await self._jira_client.search_issues(
                    credentials, build_sprint_issues_jql(jira_project_key, jira_sprint.id)
                )
            fetched_stories = assign_stories_to_sprints(issues_by_sprint)
            await self._store(target, credentials, jira_sprints, in_scope_sprints, fetched_stories, now)
        except TessioError as error:
            await self._fail(target, error.code, now)
            return
        except Exception:
            await self._fail(target, None, now)
            raise
        await self._refresh_write_side(target.project_id, credentials, now)
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.JIRA_SYNC_FINISHED,
                project_id=target.project_id,
                ids={"projectKey": target.project_key},
            )
        )

    async def _refresh_write_side(self, project_id: UUID, credentials: JiraCredentials, now: datetime) -> None:
        await self._refresh_jira_write_access.execute(now)
        try:
            await self._jira_issue_status_refresher.refresh(project_id, credentials, now)
        except TessioError as error:
            log.warning(
                "jira_sync.issue_status_refresh_failed",
                extra={"project_id": str(project_id), "error_code": error.code.value},
            )

    async def _start(self, project_id: UUID, now: datetime) -> SyncTarget | None:
        async with self._transaction.begin():
            target = await self._sync_target_reader.find(project_id)
            if target is None:
                log.warning("jira_sync.project_missing", extra={"project_id": str(project_id)})
                return None
            if target.is_archived:
                return target
            state = await self._project_sync_state_repository.lock(project_id, now)
            await self._project_sync_state_repository.save(
                state.model_copy(
                    update={
                        "status": ProjectSyncStatus.RUNNING,
                        "started_at": now,
                        "finished_at": None,
                        "error_code": None,
                    }
                )
            )
        return target

    async def _store(
        self,
        target: SyncTarget,
        credentials: JiraCredentials,
        jira_sprints: list[JiraSprint],
        in_scope_sprints: list[JiraSprint],
        fetched_stories: dict[str, FetchedStory],
        now: datetime,
    ) -> None:
        in_scope_jira_sprint_ids = {jira_sprint.id for jira_sprint in in_scope_sprints}
        async with self._transaction.begin():
            stored_sprints = {
                sprint.jira_sprint_id: sprint
                for sprint in await self._sprint_repository.list_by_project(target.project_id)
            }
            sprint_ids_by_jira_id: dict[int, UUID] = {}
            for jira_sprint in jira_sprints:
                stored_sprint = stored_sprints.get(jira_sprint.id)
                if jira_sprint.id not in in_scope_jira_sprint_ids and stored_sprint is None:
                    continue
                sprint_id = await self._sprint_repository.save_synced(
                    self._build_sprint(target, jira_sprint, stored_sprint, now)
                )
                if jira_sprint.id in in_scope_jira_sprint_ids:
                    sprint_ids_by_jira_id[jira_sprint.id] = sprint_id
            for fetched_story in fetched_stories.values():
                await self._store_story(
                    target, credentials, fetched_story, sprint_ids_by_jira_id[fetched_story.jira_sprint_id], now
                )
            await self._story_repository.mark_missing(
                target.project_id,
                frozenset(fetched_stories),
                frozenset(sprint_ids_by_jira_id.values()),
                now,
            )
            state = await self._project_sync_state_repository.lock(target.project_id, now)
            await self._project_sync_state_repository.save(
                state.model_copy(
                    update={
                        "status": ProjectSyncStatus.SUCCEEDED,
                        "finished_at": now,
                        "last_succeeded_at": now,
                        "error_code": None,
                    }
                )
            )

    async def _store_story(
        self,
        target: SyncTarget,
        credentials: JiraCredentials,
        fetched_story: FetchedStory,
        sprint_id: UUID,
        now: datetime,
    ) -> None:
        issue = fetched_story.issue
        story_id = await self._story_repository.save_synced(
            Story(
                id=uuid7(),
                project_id=target.project_id,
                sprint_id=sprint_id,
                jira_id=issue.id,
                jira_key=issue.key,
                jira_url=JIRA_BROWSE_URL_TEMPLATE.format(site_url=credentials.site_url.rstrip("/"), jira_key=issue.key),
                title=issue.summary,
                description=issue.description,
                jira_status=issue.status_name,
                jira_issue_type=issue.issue_type_name,
                test_status=TestStatus.NOT_STARTED,
                test_status_changed_at=None,
                test_status_changed_by=None,
                jira_updated_at=issue.updated_at,
                synced_at=now,
                jira_missing_at=None,
                created_at=now,
            )
        )
        merge = merge_acceptance_criteria(
            target.project_id,
            story_id,
            await self._acceptance_criterion_repository.list_for_story(story_id),
            parse_acceptance_criteria(issue.description).texts,
            now,
        )
        for criterion in merge.criteria_to_save:
            await self._acceptance_criterion_repository.save(criterion)
        if merge.change.has_changed_or_removed:
            await self._criteria_changed_handler.handle(merge.change)

    @staticmethod
    def _build_sprint(
        target: SyncTarget, jira_sprint: JiraSprint, stored_sprint: Sprint | None, now: datetime
    ) -> Sprint:
        return Sprint(
            id=uuid7() if stored_sprint is None else stored_sprint.id,
            project_id=target.project_id,
            jira_sprint_id=jira_sprint.id,
            name=jira_sprint.name,
            state=SprintState(jira_sprint.state.value),
            start_at=jira_sprint.start_at,
            end_at=jira_sprint.end_at,
            complete_at=jira_sprint.complete_at,
            synced_at=now,
            created_at=now if stored_sprint is None else stored_sprint.created_at,
        )

    async def _fail(self, target: SyncTarget, error_code: ErrorCode | None, now: datetime) -> None:
        async with self._transaction.begin():
            state = await self._project_sync_state_repository.lock(target.project_id, now)
            await self._project_sync_state_repository.save(
                state.model_copy(
                    update={"status": ProjectSyncStatus.FAILED, "finished_at": now, "error_code": error_code}
                )
            )
        ids = {"projectKey": target.project_key}
        if error_code is not None:
            ids["errorCode"] = error_code.value
        await self._live_event_publisher.publish(
            LiveEvent(type=LiveEventType.JIRA_SYNC_FAILED, project_id=target.project_id, ids=ids)
        )
