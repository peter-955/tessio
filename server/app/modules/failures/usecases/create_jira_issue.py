from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.failures.domains.failed_step.entity import FailedStep
from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.domains.jira_bug_content.entity import JiraBugContent
from app.modules.failures.domains.jira_bug_source.entity import JiraBugSource
from app.modules.failures.ports.case_result_reader import CaseResultReader
from app.modules.failures.ports.jira_bug_source_reader import JiraBugSourceReader
from app.modules.failures.typing.enums import FailureEventKind
from app.modules.failures.utils.failure_event import build_failure_changed_event
from app.modules.failures.utils.jira_bug_content import build_jira_bug_content
from app.modules.files import StoredFileRepository
from app.modules.jira import (
    JiraAttachment,
    JiraClient,
    JiraCreatedIssue,
    JiraCredentials,
    JiraNewIssue,
    JiraUnreachableError,
    LoadJiraCredentialsUseCase,
)
from app.modules.test_data import SecretValueReader
from app.shared.common import TessioError, Transaction
from app.shared.events import LiveEventPublisher
from app.shared.logging import get_logger
from app.shared.masking import SecretMasker
from app.shared.storage import ObjectStorage
from app.shared.typing.enums import ErrorCode

log = get_logger(__name__)


class CreateJiraIssueUseCase:
    def __init__(
        self,
        transaction: Transaction,
        failure_repository: FailureRepository,
        failure_event_repository: FailureEventRepository,
        jira_bug_source_reader: JiraBugSourceReader,
        case_result_reader: CaseResultReader,
        secret_value_reader: SecretValueReader,
        load_jira_credentials: LoadJiraCredentialsUseCase,
        jira_client: JiraClient,
        stored_file_repository: StoredFileRepository,
        object_storage: ObjectStorage,
        live_event_publisher: LiveEventPublisher,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._failure_repository = failure_repository
        self._failure_event_repository = failure_event_repository
        self._jira_bug_source_reader = jira_bug_source_reader
        self._case_result_reader = case_result_reader
        self._secret_value_reader = secret_value_reader
        self._load_jira_credentials = load_jira_credentials
        self._jira_client = jira_client
        self._stored_file_repository = stored_file_repository
        self._object_storage = object_storage
        self._live_event_publisher = live_event_publisher
        self._client_url = client_url

    async def execute(self, project_id: UUID, failure_id: UUID, requested_by: UUID | None) -> None:
        async with self._transaction.begin():
            failure = await self._failure_repository.find_for_update(project_id, failure_id)
            if failure is None:
                log.warning("jira.create_issue.failure_missing", extra={"failure_id": str(failure_id)})
                return
            if failure.has_jira_issue:
                return
            source = await self._jira_bug_source_reader.find(failure)
            failed_step = await self._case_result_reader.find_failed_step(failure.latest_case_result_id)
        if source is None or source.jira_project_key is None:
            await self._record_error(failure, ErrorCode.JIRA_NOT_CONFIGURED, requested_by, is_final=True)
            return
        content = await self._build_content(failure.project_id, source, source.jira_project_key, failed_step)
        try:
            credentials = await self._load_jira_credentials.execute()
            created = await self._jira_client.create_issue(
                credentials,
                JiraNewIssue(
                    jira_project_key=content.jira_project_key,
                    issue_type_name=content.issue_type_name,
                    summary=content.summary,
                    description=content.description,
                ),
            )
        except JiraUnreachableError:
            await self._record_error(failure, ErrorCode.JIRA_UNREACHABLE, requested_by, is_final=False)
            raise
        except TessioError as error:
            await self._record_error(failure, error.code, requested_by, is_final=True)
            return
        status_name, is_done = await self._find_status(credentials, created.key)
        stored = await self._store_issue(failure, created, status_name, is_done, requested_by)
        if stored is None:
            return
        await self._live_event_publisher.publish(build_failure_changed_event(stored))
        await self._attach_screenshot(credentials, created.key, content)
        await self._link_story(credentials, created.key, content)

    async def _build_content(
        self, project_id: UUID, source: JiraBugSource, jira_project_key: str, failed_step: FailedStep | None
    ) -> JiraBugContent:
        masker = SecretMasker(await self._secret_value_reader.list_secret_values(project_id, source.environment_id))
        return build_jira_bug_content(source, jira_project_key, failed_step, self._client_url, masker)

    async def _find_status(self, credentials: JiraCredentials, issue_key: str) -> tuple[str | None, bool]:
        try:
            statuses = await self._jira_client.list_issue_statuses(credentials, [issue_key])
        except TessioError as error:
            log.warning("jira.create_issue.status_failed", extra={"error_code": error.code.value})
            return None, False
        status = next((status for status in statuses if status.key == issue_key), None)
        return (None, False) if status is None else (status.status_name, status.is_done)

    async def _store_issue(
        self,
        failure: Failure,
        created: JiraCreatedIssue,
        status_name: str | None,
        is_done: bool,
        requested_by: UUID | None,
    ) -> Failure | None:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            locked = await self._failure_repository.find_for_update(failure.project_id, failure.id)
            if locked is None:
                return None
            stored = locked.model_copy(
                update={
                    "jira_issue_key": created.key,
                    "jira_issue_url": created.url,
                    "jira_issue_status": status_name,
                    "jira_issue_done_at": now if is_done else None,
                    "jira_issue_requested_at": None,
                    "jira_issue_error_code": None,
                }
            )
            await self._failure_repository.save(stored)
            await self._failure_event_repository.add(
                self._build_event(stored, FailureEventKind.JIRA_ISSUE_CREATED, requested_by, now, created.key, None)
            )
        return stored

    async def _record_error(
        self, failure: Failure, error_code: ErrorCode, requested_by: UUID | None, is_final: bool
    ) -> None:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            locked = await self._failure_repository.find_for_update(failure.project_id, failure.id)
            if locked is None or locked.has_jira_issue:
                return
            update: dict[str, object] = {"jira_issue_error_code": error_code}
            if is_final:
                update["jira_issue_requested_at"] = None
            recorded = locked.model_copy(update=update)
            await self._failure_repository.save(recorded)
            if is_final:
                await self._failure_event_repository.add(
                    self._build_event(recorded, FailureEventKind.JIRA_ISSUE_FAILED, requested_by, now, None, error_code)
                )
        log.warning(
            "jira.create_issue.failed",
            extra={"failure_id": str(failure.id), "error_code": error_code.value, "is_final": is_final},
        )
        await self._live_event_publisher.publish(build_failure_changed_event(recorded))

    async def _attach_screenshot(self, credentials: JiraCredentials, issue_key: str, content: JiraBugContent) -> None:
        if content.screenshot_file_id is None:
            return
        async with self._transaction.begin():
            stored_file = await self._stored_file_repository.find_by_id(content.screenshot_file_id)
        if stored_file is None or not stored_file.is_uploaded:
            return
        file_content = await self._object_storage.read_object(stored_file.object_key)
        if file_content is None:
            log.warning("jira.create_issue.screenshot_missing", extra={"file_id": str(stored_file.id)})
            return
        try:
            await self._jira_client.add_attachment(
                credentials,
                issue_key,
                JiraAttachment(
                    file_name=stored_file.file_name, content_type=stored_file.content_type, content=file_content
                ),
            )
        except TessioError as error:
            log.warning("jira.create_issue.attachment_failed", extra={"error_code": error.code.value})

    async def _link_story(self, credentials: JiraCredentials, issue_key: str, content: JiraBugContent) -> None:
        if content.linked_story_jira_key is None:
            return
        try:
            await self._jira_client.link_issues(credentials, issue_key, content.linked_story_jira_key)
        except TessioError as error:
            log.warning("jira.create_issue.link_failed", extra={"error_code": error.code.value})

    @staticmethod
    def _build_event(
        failure: Failure,
        kind: FailureEventKind,
        actor_id: UUID | None,
        now: datetime,
        jira_issue_key: str | None,
        error_code: ErrorCode | None,
    ) -> FailureEvent:
        return FailureEvent(
            id=uuid7(),
            failure_id=failure.id,
            kind=kind,
            from_status=None,
            to_status=None,
            case_result_id=None,
            assignee_id=None,
            actor_id=actor_id,
            created_at=now,
            jira_issue_key=jira_issue_key,
            error_code=error_code,
        )
