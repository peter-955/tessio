from app.modules.jira.domains.jira_board.entity import JiraBoard
from app.modules.jira.domains.jira_connection.entity import JiraConnection
from app.modules.jira.domains.jira_project.entity import JiraProject
from app.modules.jira.models.jira_board_response import JiraBoardResponse
from app.modules.jira.models.jira_connection_response import JiraConnectionResponse
from app.modules.jira.models.jira_project_response import JiraProjectResponse


def build_jira_connection_response(connection: JiraConnection | None) -> JiraConnectionResponse:
    if connection is None:
        return JiraConnectionResponse(
            is_configured=False, site_url=None, account_email=None, account_display_name=None, configured_at=None
        )
    return JiraConnectionResponse(
        is_configured=True,
        site_url=connection.site_url,
        account_email=connection.account_email,
        account_display_name=connection.account_display_name,
        configured_at=connection.configured_at,
    )


def build_jira_project_response(jira_project: JiraProject) -> JiraProjectResponse:
    return JiraProjectResponse(id=jira_project.id, key=jira_project.key, name=jira_project.name)


def build_jira_board_response(jira_board: JiraBoard) -> JiraBoardResponse:
    return JiraBoardResponse(id=jira_board.id, name=jira_board.name, type=jira_board.type)
