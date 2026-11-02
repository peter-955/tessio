import asyncio
from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime

import httpx
from pydantic import BaseModel, JsonValue, ValidationError

from app.modules.jira.domains.jira_account.entity import JiraAccount
from app.modules.jira.domains.jira_attachment.entity import JiraAttachment
from app.modules.jira.domains.jira_board.entity import JiraBoard
from app.modules.jira.domains.jira_created_issue.entity import JiraCreatedIssue
from app.modules.jira.domains.jira_credentials.entity import JiraCredentials
from app.modules.jira.domains.jira_document_block.entity import JiraDocumentBlock
from app.modules.jira.domains.jira_issue.entity import JiraIssue
from app.modules.jira.domains.jira_issue_status.entity import JiraIssueStatus
from app.modules.jira.domains.jira_new_issue.entity import JiraNewIssue
from app.modules.jira.domains.jira_project.entity import JiraProject
from app.modules.jira.domains.jira_sprint.entity import JiraSprint
from app.modules.jira.errors import (
    JiraInvalidCredentialsError,
    JiraIssueRejectedError,
    JiraProjectNotFoundError,
    JiraUnreachableError,
    JiraWriteNotAllowedError,
)
from app.modules.jira.infrastructure.jira_payloads import (
    JiraBoardPagePayload,
    JiraCreatedIssuePayload,
    JiraIssuePayload,
    JiraIssueSearchPagePayload,
    JiraIssueStatusPagePayload,
    JiraMyPermissionsPayload,
    JiraMyselfPayload,
    JiraProjectPagePayload,
    JiraSprintPagePayload,
)
from app.modules.jira.ports.jira_client import JiraClient
from app.modules.jira.typing.constants import (
    JIRA_BOARD_SPRINTS_PATH,
    JIRA_BOARDS_PATH,
    JIRA_CONNECT_TIMEOUT_SECONDS,
    JIRA_DONE_STATUS_CATEGORY_KEY,
    JIRA_INVALID_CREDENTIALS_STATUS_CODES,
    JIRA_ISSUE_ATTACHMENTS_PATH,
    JIRA_ISSUE_BROWSE_URL_TEMPLATE,
    JIRA_ISSUE_COMMENT_PATH,
    JIRA_ISSUE_FIELDS,
    JIRA_ISSUE_LINK_PATH,
    JIRA_ISSUE_PATH,
    JIRA_ISSUE_SEARCH_PATH,
    JIRA_MAX_PAGES,
    JIRA_MAX_RATE_LIMIT_RETRIES,
    JIRA_MY_PERMISSIONS_PATH,
    JIRA_MYSELF_PATH,
    JIRA_NO_CHECK_HEADERS,
    JIRA_PAGE_SIZE,
    JIRA_PERMISSION_REJECTED_STATUS_CODES,
    JIRA_PROJECT_SEARCH_PATH,
    JIRA_RELATES_LINK_TYPE_NAME,
    JIRA_REQUEST_TIMEOUT_SECONDS,
    JIRA_RETRYABLE_STATUS_CODES,
    JIRA_SEARCH_PAGE_SIZE,
    JIRA_STATUS_FIELDS,
    JIRA_STATUS_SEARCH_BATCH_SIZE,
    JIRA_WRITE_FORBIDDEN_STATUS_CODES,
    JIRA_WRITE_INVALID_CREDENTIALS_STATUS_CODES,
    JIRA_WRITE_PERMISSIONS,
    JIRA_WRITE_REJECTED_STATUS_CODES,
)
from app.modules.jira.typing.enums import JiraPermission, JiraSprintState
from app.modules.jira.utils.jira_document import build_adf_document
from app.modules.jira.utils.jira_text import build_issue_keys_jql, is_valid_issue_key
from app.modules.jira.utils.retry_delay import compute_retry_delay
from app.shared.logging import get_logger

log = get_logger(__name__)

JiraQueryParameters = Mapping[str, str | int]
JiraUploadFiles = Mapping[str, tuple[str, bytes, str]]


class HttpxJiraClient(JiraClient):
    def __init__(
        self, http_client: httpx.AsyncClient, sleep: Callable[[float], Awaitable[None]] = asyncio.sleep
    ) -> None:
        self._http_client = http_client
        self._sleep = sleep
        self._timeout = httpx.Timeout(JIRA_REQUEST_TIMEOUT_SECONDS, connect=JIRA_CONNECT_TIMEOUT_SECONDS)

    async def get_myself(self, credentials: JiraCredentials) -> JiraAccount:
        response = await self._send(credentials, "GET", JIRA_MYSELF_PATH)
        self._ensure_success(response, JIRA_MYSELF_PATH)
        myself = self._parse(JiraMyselfPayload, response, JIRA_MYSELF_PATH)
        return JiraAccount(
            account_id=myself.account_id, display_name=myself.display_name, email_address=myself.email_address
        )

    async def list_projects(self, credentials: JiraCredentials) -> list[JiraProject]:
        jira_projects: list[JiraProject] = []
        start_at = 0
        for _ in range(JIRA_MAX_PAGES):
            response = await self._send(
                credentials,
                "GET",
                JIRA_PROJECT_SEARCH_PATH,
                params={"startAt": start_at, "maxResults": JIRA_PAGE_SIZE, "orderBy": "name"},
            )
            self._ensure_success(response, JIRA_PROJECT_SEARCH_PATH)
            page = self._parse(JiraProjectPagePayload, response, JIRA_PROJECT_SEARCH_PATH)
            jira_projects.extend(
                JiraProject(id=project.id, key=project.key, name=project.name) for project in page.values
            )
            if page.is_last or not page.values:
                break
            start_at += len(page.values)
        return jira_projects

    async def list_boards(self, credentials: JiraCredentials, jira_project_key: str) -> list[JiraBoard]:
        jira_boards: list[JiraBoard] = []
        start_at = 0
        for _ in range(JIRA_MAX_PAGES):
            response = await self._send(
                credentials,
                "GET",
                JIRA_BOARDS_PATH,
                params={"projectKeyOrId": jira_project_key, "startAt": start_at, "maxResults": JIRA_PAGE_SIZE},
            )
            if response.status_code in {httpx.codes.BAD_REQUEST, httpx.codes.NOT_FOUND}:
                raise JiraProjectNotFoundError
            self._ensure_success(response, JIRA_BOARDS_PATH)
            page = self._parse(JiraBoardPagePayload, response, JIRA_BOARDS_PATH)
            jira_boards.extend(JiraBoard(id=board.id, name=board.name, type=board.type) for board in page.values)
            if page.is_last or not page.values:
                break
            start_at += len(page.values)
        return jira_boards

    async def list_sprints(
        self, credentials: JiraCredentials, board_id: int, states: frozenset[JiraSprintState]
    ) -> list[JiraSprint]:
        path = JIRA_BOARD_SPRINTS_PATH.format(board_id=board_id)
        state_filter = ",".join(state.value for state in JiraSprintState if state in states)
        jira_sprints: list[JiraSprint] = []
        start_at = 0
        for _ in range(JIRA_MAX_PAGES):
            params: dict[str, str | int] = {"startAt": start_at, "maxResults": JIRA_PAGE_SIZE}
            if state_filter:
                params["state"] = state_filter
            response = await self._send(credentials, "GET", path, params=params)
            if response.status_code == httpx.codes.BAD_REQUEST:
                return []
            self._ensure_success(response, path)
            page = self._parse(JiraSprintPagePayload, response, path)
            jira_sprints.extend(
                JiraSprint(
                    id=sprint.id,
                    name=sprint.name,
                    state=sprint.state,
                    start_at=sprint.start_date,
                    end_at=sprint.end_date,
                    complete_at=sprint.complete_date,
                )
                for sprint in page.values
            )
            if page.is_last or not page.values:
                break
            start_at += len(page.values)
        return jira_sprints

    async def search_issues(self, credentials: JiraCredentials, jql: str) -> list[JiraIssue]:
        jira_issues: list[JiraIssue] = []
        next_page_token: str | None = None
        for _ in range(JIRA_MAX_PAGES):
            body: dict[str, JsonValue] = {
                "jql": jql,
                "fields": list(JIRA_ISSUE_FIELDS),
                "maxResults": JIRA_SEARCH_PAGE_SIZE,
            }
            if next_page_token is not None:
                body["nextPageToken"] = next_page_token
            response = await self._send(credentials, "POST", JIRA_ISSUE_SEARCH_PATH, json_body=body)
            self._ensure_success(response, JIRA_ISSUE_SEARCH_PATH)
            page = self._parse(JiraIssueSearchPagePayload, response, JIRA_ISSUE_SEARCH_PATH)
            jira_issues.extend(self._build_issue(issue) for issue in page.issues)
            next_page_token = page.next_page_token
            if next_page_token is None or page.is_last is True:
                break
        return jira_issues

    async def list_missing_permissions(
        self, credentials: JiraCredentials, jira_project_key: str | None
    ) -> frozenset[JiraPermission]:
        params: dict[str, str | int] = {
            "permissions": ",".join(permission.value for permission in JIRA_WRITE_PERMISSIONS)
        }
        if jira_project_key is not None:
            params["projectKey"] = jira_project_key
        response = await self._send(credentials, "GET", JIRA_MY_PERMISSIONS_PATH, params=params)
        if response.status_code in JIRA_PERMISSION_REJECTED_STATUS_CODES:
            return frozenset(JIRA_WRITE_PERMISSIONS)
        self._ensure_success(response, JIRA_MY_PERMISSIONS_PATH)
        payload = self._parse(JiraMyPermissionsPayload, response, JIRA_MY_PERMISSIONS_PATH)
        return frozenset(
            permission
            for permission in JIRA_WRITE_PERMISSIONS
            if permission.value not in payload.permissions or not payload.permissions[permission.value].have_permission
        )

    async def create_issue(self, credentials: JiraCredentials, new_issue: JiraNewIssue) -> JiraCreatedIssue:
        body: dict[str, JsonValue] = {
            "fields": {
                "project": {"key": new_issue.jira_project_key},
                "issuetype": {"name": new_issue.issue_type_name},
                "summary": new_issue.summary,
                "description": build_adf_document(new_issue.description),
            }
        }
        response = await self._send(credentials, "POST", JIRA_ISSUE_PATH, json_body=body, is_write=True)
        self._ensure_written(response, JIRA_ISSUE_PATH)
        created = self._parse(JiraCreatedIssuePayload, response, JIRA_ISSUE_PATH)
        return JiraCreatedIssue(
            id=created.id,
            key=created.key,
            url=JIRA_ISSUE_BROWSE_URL_TEMPLATE.format(site_url=credentials.site_url.rstrip("/"), issue_key=created.key),
        )

    async def add_attachment(self, credentials: JiraCredentials, issue_key: str, attachment: JiraAttachment) -> None:
        path = JIRA_ISSUE_ATTACHMENTS_PATH.format(issue_key=issue_key)
        files = {"file": (attachment.file_name, attachment.content, attachment.content_type)}
        response = await self._send(credentials, "POST", path, files=files, is_write=True)
        self._ensure_written(response, path)

    async def add_comment(self, credentials: JiraCredentials, issue_key: str, body: list[JiraDocumentBlock]) -> None:
        path = JIRA_ISSUE_COMMENT_PATH.format(issue_key=issue_key)
        response = await self._send(
            credentials, "POST", path, json_body={"body": build_adf_document(body)}, is_write=True
        )
        self._ensure_written(response, path)

    async def link_issues(self, credentials: JiraCredentials, inward_issue_key: str, outward_issue_key: str) -> None:
        body: dict[str, JsonValue] = {
            "type": {"name": JIRA_RELATES_LINK_TYPE_NAME},
            "inwardIssue": {"key": inward_issue_key},
            "outwardIssue": {"key": outward_issue_key},
        }
        response = await self._send(credentials, "POST", JIRA_ISSUE_LINK_PATH, json_body=body, is_write=True)
        self._ensure_written(response, JIRA_ISSUE_LINK_PATH)

    async def list_issue_statuses(self, credentials: JiraCredentials, issue_keys: list[str]) -> list[JiraIssueStatus]:
        statuses: list[JiraIssueStatus] = []
        unique_keys = sorted({issue_key for issue_key in issue_keys if is_valid_issue_key(issue_key)})
        for start in range(0, len(unique_keys), JIRA_STATUS_SEARCH_BATCH_SIZE):
            statuses.extend(
                await self._search_statuses(credentials, unique_keys[start : start + JIRA_STATUS_SEARCH_BATCH_SIZE])
            )
        return statuses

    async def _search_statuses(self, credentials: JiraCredentials, issue_keys: list[str]) -> list[JiraIssueStatus]:
        body: dict[str, JsonValue] = {
            "jql": build_issue_keys_jql(issue_keys),
            "fields": list(JIRA_STATUS_FIELDS),
            "maxResults": JIRA_SEARCH_PAGE_SIZE,
        }
        response = await self._send(credentials, "POST", JIRA_ISSUE_SEARCH_PATH, json_body=body)
        if response.status_code == httpx.codes.BAD_REQUEST:
            log.warning("jira.issue_statuses.refused", extra={"issue_count": len(issue_keys)})
            return []
        self._ensure_success(response, JIRA_ISSUE_SEARCH_PATH)
        page = self._parse(JiraIssueStatusPagePayload, response, JIRA_ISSUE_SEARCH_PATH)
        return [
            JiraIssueStatus(
                key=issue.key,
                status_name=issue.fields.status.name,
                is_done=issue.fields.status.status_category.key == JIRA_DONE_STATUS_CATEGORY_KEY,
            )
            for issue in page.issues
        ]

    async def _send(
        self,
        credentials: JiraCredentials,
        method: str,
        path: str,
        params: JiraQueryParameters | None = None,
        json_body: JsonValue = None,
        files: JiraUploadFiles | None = None,
        is_write: bool = False,
    ) -> httpx.Response:
        auth = httpx.BasicAuth(credentials.account_email, credentials.api_token.get_secret_value())
        headers = {"Accept": "application/json"}
        if files is not None:
            headers.update(JIRA_NO_CHECK_HEADERS)
        for attempt in range(JIRA_MAX_RATE_LIMIT_RETRIES + 1):
            try:
                response = await self._http_client.request(
                    method,
                    credentials.site_url + path,
                    params=params,
                    json=json_body,
                    files=files,
                    auth=auth,
                    headers=headers,
                    timeout=self._timeout,
                )
            except httpx.HTTPError as error:
                log.warning("jira.request.failed", extra={"path": path, "reason": type(error).__name__})
                raise JiraUnreachableError from error
            self._raise_for_access(response, is_write)
            if response.status_code not in JIRA_RETRYABLE_STATUS_CODES:
                return response
            if attempt == JIRA_MAX_RATE_LIMIT_RETRIES:
                break
            delay_seconds = compute_retry_delay(response.headers.get("Retry-After"), attempt, datetime.now(UTC))
            log.warning(
                "jira.request.rate_limited",
                extra={"path": path, "attempt": attempt + 1, "delay_seconds": delay_seconds},
            )
            await self._sleep(delay_seconds)
        log.warning("jira.request.failed", extra={"path": path, "status_code": response.status_code})
        raise JiraUnreachableError

    @staticmethod
    def _raise_for_access(response: httpx.Response, is_write: bool) -> None:
        if not is_write:
            if response.status_code in JIRA_INVALID_CREDENTIALS_STATUS_CODES:
                raise JiraInvalidCredentialsError
            return
        if response.status_code in JIRA_WRITE_INVALID_CREDENTIALS_STATUS_CODES:
            raise JiraInvalidCredentialsError
        if response.status_code in JIRA_WRITE_FORBIDDEN_STATUS_CODES:
            raise JiraWriteNotAllowedError

    def _ensure_written(self, response: httpx.Response, path: str) -> None:
        if response.status_code in JIRA_WRITE_REJECTED_STATUS_CODES:
            log.warning("jira.write.rejected", extra={"path": path, "status_code": response.status_code})
            raise JiraIssueRejectedError
        self._ensure_success(response, path)

    def _ensure_success(self, response: httpx.Response, path: str) -> None:
        if response.is_success:
            return
        log.warning("jira.request.failed", extra={"path": path, "status_code": response.status_code})
        raise JiraUnreachableError

    def _parse[PayloadType: BaseModel](
        self, payload_type: type[PayloadType], response: httpx.Response, path: str
    ) -> PayloadType:
        try:
            return payload_type.model_validate_json(response.content)
        except ValidationError as error:
            log.warning("jira.request.failed", extra={"path": path, "reason": "invalid_response"})
            raise JiraUnreachableError from error

    def _build_issue(self, issue: JiraIssuePayload) -> JiraIssue:
        return JiraIssue(
            id=issue.id,
            key=issue.key,
            summary=issue.fields.summary,
            description=issue.fields.description,
            status_name=issue.fields.status.name,
            issue_type_name=issue.fields.issuetype.name,
            is_subtask=issue.fields.issuetype.subtask,
            updated_at=issue.fields.updated,
        )
