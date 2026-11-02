from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import SecretStr

from app.modules.jira.dependencies import (
    get_get_jira_connection,
    get_get_project_jira_write_access,
    get_list_jira_boards,
    get_list_jira_projects,
    get_save_jira_connection,
)
from app.modules.jira.models.jira_board_response import JiraBoardResponse
from app.modules.jira.models.jira_connection_response import JiraConnectionResponse
from app.modules.jira.models.jira_project_response import JiraProjectResponse
from app.modules.jira.models.project_jira_write_access_response import ProjectJiraWriteAccessResponse
from app.modules.jira.models.save_jira_connection_request import SaveJiraConnectionRequest
from app.modules.jira.usecases.get_jira_connection import GetJiraConnectionUseCase
from app.modules.jira.usecases.get_project_jira_write_access import GetProjectJiraWriteAccessUseCase
from app.modules.jira.usecases.list_jira_boards import ListJiraBoardsUseCase
from app.modules.jira.usecases.list_jira_projects import ListJiraProjectsUseCase
from app.modules.jira.usecases.save_jira_connection import SaveJiraConnectionUseCase
from app.modules.jira.utils.jira_responses import (
    build_jira_board_response,
    build_jira_connection_response,
    build_jira_project_response,
    build_project_jira_write_access_response,
)
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

jira_router = APIRouter(prefix="/api", tags=["jira"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@jira_router.get("/workspace/jira")
async def get_jira_connection(
    actor: SignedInActor,
    use_case: Annotated[GetJiraConnectionUseCase, Depends(get_get_jira_connection)],
) -> JiraConnectionResponse:
    return build_jira_connection_response(await use_case.execute(actor))


@jira_router.put("/workspace/jira")
async def save_jira_connection(
    body: SaveJiraConnectionRequest,
    actor: SignedInActor,
    use_case: Annotated[SaveJiraConnectionUseCase, Depends(get_save_jira_connection)],
) -> JiraConnectionResponse:
    api_token = None if body.api_token is None else SecretStr(body.api_token)
    connection = await use_case.execute(actor, body.site_url, str(body.account_email), api_token)
    return build_jira_connection_response(connection)


@jira_router.get("/workspace/jira/projects")
async def list_jira_projects(
    actor: SignedInActor,
    use_case: Annotated[ListJiraProjectsUseCase, Depends(get_list_jira_projects)],
) -> list[JiraProjectResponse]:
    jira_projects = await use_case.execute(actor)
    return [build_jira_project_response(jira_project) for jira_project in jira_projects]


@jira_router.get("/workspace/jira/boards")
async def list_jira_boards(
    actor: SignedInActor,
    use_case: Annotated[ListJiraBoardsUseCase, Depends(get_list_jira_boards)],
    jira_project_key: Annotated[str, Query(alias="jiraProjectKey", min_length=1, max_length=20)],
) -> list[JiraBoardResponse]:
    jira_boards = await use_case.execute(actor, jira_project_key)
    return [build_jira_board_response(jira_board) for jira_board in jira_boards]


@jira_router.get("/projects/{project_key}/jira-write-access")
async def get_project_jira_write_access(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetProjectJiraWriteAccessUseCase, Depends(get_get_project_jira_write_access)],
) -> ProjectJiraWriteAccessResponse:
    return build_project_jira_write_access_response(await use_case.execute(actor, project_key))
