from abc import ABC, abstractmethod

from app.modules.jira.domains.jira_account.entity import JiraAccount
from app.modules.jira.domains.jira_board.entity import JiraBoard
from app.modules.jira.domains.jira_credentials.entity import JiraCredentials
from app.modules.jira.domains.jira_issue.entity import JiraIssue
from app.modules.jira.domains.jira_project.entity import JiraProject
from app.modules.jira.domains.jira_sprint.entity import JiraSprint
from app.modules.jira.typing.enums import JiraSprintState


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
