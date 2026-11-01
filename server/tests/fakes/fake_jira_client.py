from app.modules.jira import (
    JiraAccount,
    JiraBoard,
    JiraClient,
    JiraCredentials,
    JiraInvalidCredentialsError,
    JiraIssue,
    JiraProject,
    JiraSprint,
    JiraSprintState,
    JiraUnreachableError,
)
from app.modules.jira.errors import JiraProjectNotFoundError


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

    def _check(self, credentials: JiraCredentials) -> None:
        self.requested_site_urls.append(credentials.site_url)
        if self.is_unreachable:
            raise JiraUnreachableError
        if credentials.api_token.get_secret_value() != self.valid_api_token:
            raise JiraInvalidCredentialsError
