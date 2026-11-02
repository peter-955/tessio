from dataclasses import dataclass

from app.modules.jira import (
    JiraAccount,
    JiraAttachment,
    JiraBoard,
    JiraClient,
    JiraCreatedIssue,
    JiraCredentials,
    JiraDocumentBlock,
    JiraInvalidCredentialsError,
    JiraIssue,
    JiraIssueStatus,
    JiraNewIssue,
    JiraPermission,
    JiraProject,
    JiraSprint,
    JiraSprintState,
    JiraUnreachableError,
    JiraWriteNotAllowedError,
)
from app.modules.jira.errors import JiraProjectNotFoundError
from app.shared.common import TessioError


@dataclass(frozen=True)
class RecordedComment:
    issue_key: str
    body: list[JiraDocumentBlock]


@dataclass(frozen=True)
class RecordedLink:
    inward_issue_key: str
    outward_issue_key: str


@dataclass(frozen=True)
class RecordedAttachment:
    issue_key: str
    attachment: JiraAttachment


class FakeJiraClient(JiraClient):
    def __init__(self) -> None:
        self.valid_api_token = "jira-api-token"
        self.account = JiraAccount(account_id="acc-1", display_name="Jira Bot", email_address=None)
        self.projects: list[JiraProject] = []
        self.boards_by_project_key: dict[str, list[JiraBoard]] = {}
        self.sprints_by_board_id: dict[int, list[JiraSprint]] = {}
        self.issues_by_jql: dict[str, list[JiraIssue]] = {}
        self.is_unreachable = False
        self.requested_site_urls: list[str] = []
        self.missing_permissions_by_project_key: dict[str | None, frozenset[JiraPermission]] = {}
        self.permission_checks: list[str | None] = []
        self.created_issues: list[JiraNewIssue] = []
        self.attachments: list[RecordedAttachment] = []
        self.comments: list[RecordedComment] = []
        self.links: list[RecordedLink] = []
        self.statuses_by_key: dict[str, JiraIssueStatus] = {}
        self.status_requests: list[list[str]] = []
        self.write_errors: list[TessioError] = []
        self.comment_errors: list[TessioError] = []
        self.next_issue_number = 100

    async def get_myself(self, credentials: JiraCredentials) -> JiraAccount:
        self._check(credentials)
        return self.account

    async def list_projects(self, credentials: JiraCredentials) -> list[JiraProject]:
        self._check(credentials)
        return list(self.projects)

    async def list_boards(self, credentials: JiraCredentials, jira_project_key: str) -> list[JiraBoard]:
        self._check(credentials)
        if jira_project_key not in self.boards_by_project_key:
            raise JiraProjectNotFoundError
        return list(self.boards_by_project_key[jira_project_key])

    async def list_sprints(
        self, credentials: JiraCredentials, board_id: int, states: frozenset[JiraSprintState]
    ) -> list[JiraSprint]:
        self._check(credentials)
        return [sprint for sprint in self.sprints_by_board_id.get(board_id, []) if not states or sprint.state in states]

    async def search_issues(self, credentials: JiraCredentials, jql: str) -> list[JiraIssue]:
        self._check(credentials)
        return list(self.issues_by_jql.get(jql, []))

    async def list_missing_permissions(
        self, credentials: JiraCredentials, jira_project_key: str | None
    ) -> frozenset[JiraPermission]:
        self._check_quietly(credentials)
        self.permission_checks.append(jira_project_key)
        return self.missing_permissions_by_project_key.get(jira_project_key, frozenset())

    async def create_issue(self, credentials: JiraCredentials, new_issue: JiraNewIssue) -> JiraCreatedIssue:
        self._check_quietly(credentials)
        if self.write_errors:
            raise self.write_errors.pop(0)
        if JiraPermission.CREATE_ISSUES in self.missing_permissions_by_project_key.get(
            new_issue.jira_project_key, frozenset()
        ):
            raise JiraWriteNotAllowedError
        self.created_issues.append(new_issue)
        self.next_issue_number += 1
        key = f"{new_issue.jira_project_key}-{self.next_issue_number}"
        self.statuses_by_key.setdefault(key, JiraIssueStatus(key=key, status_name="To Do", is_done=False))
        return JiraCreatedIssue(id=str(self.next_issue_number), key=key, url=f"{credentials.site_url}/browse/{key}")

    async def add_attachment(self, credentials: JiraCredentials, issue_key: str, attachment: JiraAttachment) -> None:
        self._check_quietly(credentials)
        self.attachments.append(RecordedAttachment(issue_key=issue_key, attachment=attachment))

    async def add_comment(self, credentials: JiraCredentials, issue_key: str, body: list[JiraDocumentBlock]) -> None:
        self._check_quietly(credentials)
        if self.comment_errors:
            raise self.comment_errors.pop(0)
        self.comments.append(RecordedComment(issue_key=issue_key, body=body))

    async def link_issues(self, credentials: JiraCredentials, inward_issue_key: str, outward_issue_key: str) -> None:
        self._check_quietly(credentials)
        self.links.append(RecordedLink(inward_issue_key=inward_issue_key, outward_issue_key=outward_issue_key))

    async def list_issue_statuses(self, credentials: JiraCredentials, issue_keys: list[str]) -> list[JiraIssueStatus]:
        self._check_quietly(credentials)
        self.status_requests.append(sorted(issue_keys))
        return [self.statuses_by_key[key] for key in sorted(set(issue_keys)) if key in self.statuses_by_key]

    def _check_quietly(self, credentials: JiraCredentials) -> None:
        if self.is_unreachable:
            raise JiraUnreachableError
        if credentials.api_token.get_secret_value() != self.valid_api_token:
            raise JiraInvalidCredentialsError

    def _check(self, credentials: JiraCredentials) -> None:
        self.requested_site_urls.append(credentials.site_url)
        if self.is_unreachable:
            raise JiraUnreachableError
        if credentials.api_token.get_secret_value() != self.valid_api_token:
            raise JiraInvalidCredentialsError
