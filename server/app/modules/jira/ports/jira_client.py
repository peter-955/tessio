from abc import ABC, abstractmethod

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
from app.modules.jira.typing.enums import JiraPermission, JiraSprintState


class JiraClient(ABC):
    @abstractmethod
    async def get_myself(self, credentials: JiraCredentials) -> JiraAccount: ...

    @abstractmethod
    async def list_projects(self, credentials: JiraCredentials) -> list[JiraProject]: ...

    @abstractmethod
    async def list_boards(self, credentials: JiraCredentials, jira_project_key: str) -> list[JiraBoard]: ...

    @abstractmethod
    async def list_sprints(
        self, credentials: JiraCredentials, board_id: int, states: frozenset[JiraSprintState]
    ) -> list[JiraSprint]: ...

    @abstractmethod
    async def search_issues(self, credentials: JiraCredentials, jql: str) -> list[JiraIssue]: ...

    @abstractmethod
    async def list_missing_permissions(
        self, credentials: JiraCredentials, jira_project_key: str | None
    ) -> frozenset[JiraPermission]: ...

    @abstractmethod
    async def create_issue(self, credentials: JiraCredentials, new_issue: JiraNewIssue) -> JiraCreatedIssue: ...

    @abstractmethod
    async def add_attachment(
        self, credentials: JiraCredentials, issue_key: str, attachment: JiraAttachment
    ) -> None: ...

    @abstractmethod
    async def add_comment(
        self, credentials: JiraCredentials, issue_key: str, body: list[JiraDocumentBlock]
    ) -> None: ...

    @abstractmethod
    async def link_issues(
        self, credentials: JiraCredentials, inward_issue_key: str, outward_issue_key: str
    ) -> None: ...

    @abstractmethod
    async def list_issue_statuses(
        self, credentials: JiraCredentials, issue_keys: list[str]
    ) -> list[JiraIssueStatus]: ...
