from fastapi import Request

from app.modules.jira.usecases.get_jira_connection import GetJiraConnectionUseCase
from app.modules.jira.usecases.get_project_jira_write_access import GetProjectJiraWriteAccessUseCase
from app.modules.jira.usecases.list_jira_boards import ListJiraBoardsUseCase
from app.modules.jira.usecases.list_jira_projects import ListJiraProjectsUseCase
from app.modules.jira.usecases.save_jira_connection import SaveJiraConnectionUseCase


def get_get_jira_connection(request: Request) -> GetJiraConnectionUseCase:
    use_case: GetJiraConnectionUseCase = request.app.state.container.get_jira_connection
    return use_case


def get_save_jira_connection(request: Request) -> SaveJiraConnectionUseCase:
    use_case: SaveJiraConnectionUseCase = request.app.state.container.save_jira_connection
    return use_case


def get_list_jira_projects(request: Request) -> ListJiraProjectsUseCase:
    use_case: ListJiraProjectsUseCase = request.app.state.container.list_jira_projects
    return use_case


def get_list_jira_boards(request: Request) -> ListJiraBoardsUseCase:
    use_case: ListJiraBoardsUseCase = request.app.state.container.list_jira_boards
    return use_case


def get_get_project_jira_write_access(request: Request) -> GetProjectJiraWriteAccessUseCase:
    use_case: GetProjectJiraWriteAccessUseCase = request.app.state.container.get_project_jira_write_access
    return use_case
