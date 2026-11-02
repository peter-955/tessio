from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.projects.dependencies import (
    get_archive_project,
    get_create_project,
    get_get_project,
    get_get_user_access,
    get_list_member_candidates,
    get_list_project_members,
    get_list_projects,
    get_remove_project_member,
    get_set_project_member,
    get_signed_in_actor,
    get_unarchive_project,
    get_update_project,
)
from app.modules.projects.domains.project_changes.entity import ProjectChanges
from app.modules.projects.models.create_project_request import CreateProjectRequest
from app.modules.projects.models.member_candidate_response import MemberCandidateResponse
from app.modules.projects.models.project_member_response import ProjectMemberResponse
from app.modules.projects.models.project_response import ProjectResponse
from app.modules.projects.models.set_project_member_request import SetProjectMemberRequest
from app.modules.projects.models.update_project_request import UpdateProjectRequest
from app.modules.projects.models.user_project_access_response import UserProjectAccessResponse
from app.modules.projects.usecases.archive_project import ArchiveProjectUseCase
from app.modules.projects.usecases.create_project import CreateProjectUseCase
from app.modules.projects.usecases.get_project import GetProjectUseCase
from app.modules.projects.usecases.get_user_access import GetUserAccessUseCase
from app.modules.projects.usecases.list_member_candidates import ListMemberCandidatesUseCase
from app.modules.projects.usecases.list_project_members import ListProjectMembersUseCase
from app.modules.projects.usecases.list_projects import ListProjectsUseCase
from app.modules.projects.usecases.remove_project_member import RemoveProjectMemberUseCase
from app.modules.projects.usecases.set_project_member import SetProjectMemberUseCase
from app.modules.projects.usecases.unarchive_project import UnarchiveProjectUseCase
from app.modules.projects.usecases.update_project import UpdateProjectUseCase
from app.modules.projects.utils.project_member_response import build_project_member_response
from app.modules.projects.utils.project_response import build_project_response
from app.shared.permissions import Actor

projects_router = APIRouter(prefix="/api", tags=["projects"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@projects_router.get("/projects")
async def list_projects(
    actor: SignedInActor,
    use_case: Annotated[ListProjectsUseCase, Depends(get_list_projects)],
    include_archived: Annotated[bool, Query(alias="includeArchived")] = False,
) -> list[ProjectResponse]:
    overviews = await use_case.execute(actor, include_archived)
    return [build_project_response(overview) for overview in overviews]


@projects_router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    body: CreateProjectRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateProjectUseCase, Depends(get_create_project)],
) -> ProjectResponse:
    overview = await use_case.execute(
        actor, body.key, body.name, body.description, body.jira_project_key, body.jira_board_id
    )
    return build_project_response(overview)


@projects_router.get("/projects/{project_key}")
async def get_project(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetProjectUseCase, Depends(get_get_project)],
) -> ProjectResponse:
    return build_project_response(await use_case.execute(actor, project_key))


@projects_router.patch("/projects/{project_key}")
async def update_project(
    project_key: str,
    body: UpdateProjectRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateProjectUseCase, Depends(get_update_project)],
) -> ProjectResponse:
    changes = ProjectChanges(
        name=body.name,
        description=body.description,
        jira_board_id=body.jira_board_id,
        allowed_file_types=body.allowed_file_types,
        default_environment_id=body.default_environment_id,
        is_default_environment_cleared="default_environment_id" in body.model_fields_set
        and body.default_environment_id is None,
        require_separate_reviewer=body.require_separate_reviewer,
        jira_bug_issue_type=body.jira_bug_issue_type,
        jira_post_results=body.jira_post_results,
    )
    return build_project_response(await use_case.execute(actor, project_key, changes))


@projects_router.post("/projects/{project_key}/archive")
async def archive_project(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ArchiveProjectUseCase, Depends(get_archive_project)],
) -> ProjectResponse:
    return build_project_response(await use_case.execute(actor, project_key))


@projects_router.post("/projects/{project_key}/unarchive")
async def unarchive_project(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[UnarchiveProjectUseCase, Depends(get_unarchive_project)],
) -> ProjectResponse:
    return build_project_response(await use_case.execute(actor, project_key))


@projects_router.get("/projects/{project_key}/members")
async def list_project_members(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListProjectMembersUseCase, Depends(get_list_project_members)],
) -> list[ProjectMemberResponse]:
    member_profiles = await use_case.execute(actor, project_key)
    return [build_project_member_response(member_profile) for member_profile in member_profiles]


@projects_router.get("/projects/{project_key}/members/candidates")
async def list_member_candidates(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListMemberCandidatesUseCase, Depends(get_list_member_candidates)],
    query: Annotated[str | None, Query(max_length=200)] = None,
) -> list[MemberCandidateResponse]:
    candidates = await use_case.execute(actor, project_key, query)
    return [
        MemberCandidateResponse(
            user_id=candidate.user_id, name=candidate.name, email=candidate.email, user_status=candidate.user_status
        )
        for candidate in candidates
    ]


@projects_router.put("/projects/{project_key}/members/{user_id}")
async def set_project_member(
    project_key: str,
    user_id: UUID,
    body: SetProjectMemberRequest,
    actor: SignedInActor,
    use_case: Annotated[SetProjectMemberUseCase, Depends(get_set_project_member)],
) -> ProjectMemberResponse:
    return build_project_member_response(await use_case.execute(actor, project_key, user_id, body.role))


@projects_router.delete("/projects/{project_key}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_key: str,
    user_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[RemoveProjectMemberUseCase, Depends(get_remove_project_member)],
) -> None:
    await use_case.execute(actor, project_key, user_id)


@projects_router.get("/users/{user_id}/access")
async def get_user_access(
    user_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[GetUserAccessUseCase, Depends(get_get_user_access)],
) -> list[UserProjectAccessResponse]:
    accesses = await use_case.execute(actor, user_id)
    return [
        UserProjectAccessResponse(
            project_id=access.project_id,
            project_key=access.project_key,
            project_name=access.project_name,
            role=access.role,
            is_archived=access.is_archived,
        )
        for access in accesses
    ]
