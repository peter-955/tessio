from app.modules.projects.ports.jira_connection_checker import JiraConnectionChecker


class StaticJiraConnectionChecker(JiraConnectionChecker):
    def __init__(self, is_configured: bool) -> None:
        self._is_configured = is_configured

    async def is_configured(self) -> bool:
        return self._is_configured
