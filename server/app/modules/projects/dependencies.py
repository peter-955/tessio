from typing import Annotated

from fastapi import Depends, Request

from app.modules.auth import AuthenticatedSession, get_signed_in_session
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
from app.modules.users import build_actor
from app.shared.permissions import Actor


def get_list_projects(request: Request) -> ListProjectsUseCase:
    use_case: ListProjectsUseCase = request.app.state.container.list_projects
    return use_case


def get_create_project(request: Request) -> CreateProjectUseCase:
    use_case: CreateProjectUseCase = request.app.state.container.create_project
    return use_case


def get_get_project(request: Request) -> GetProjectUseCase:
    use_case: GetProjectUseCase = request.app.state.container.get_project
    return use_case


def get_update_project(request: Request) -> UpdateProjectUseCase:
    use_case: UpdateProjectUseCase = request.app.state.container.update_project
    return use_case


def get_archive_project(request: Request) -> ArchiveProjectUseCase:
    use_case: ArchiveProjectUseCase = request.app.state.container.archive_project
    return use_case


def get_unarchive_project(request: Request) -> UnarchiveProjectUseCase:
    use_case: UnarchiveProjectUseCase = request.app.state.container.unarchive_project
    return use_case


def get_list_project_members(request: Request) -> ListProjectMembersUseCase:
    use_case: ListProjectMembersUseCase = request.app.state.container.list_project_members
    return use_case


def get_set_project_member(request: Request) -> SetProjectMemberUseCase:
    use_case: SetProjectMemberUseCase = request.app.state.container.set_project_member
    return use_case


def get_remove_project_member(request: Request) -> RemoveProjectMemberUseCase:
    use_case: RemoveProjectMemberUseCase = request.app.state.container.remove_project_member
    return use_case


def get_list_member_candidates(request: Request) -> ListMemberCandidatesUseCase:
    use_case: ListMemberCandidatesUseCase = request.app.state.container.list_member_candidates
    return use_case


def get_get_user_access(request: Request) -> GetUserAccessUseCase:
    use_case: GetUserAccessUseCase = request.app.state.container.get_user_access
    return use_case


async def get_signed_in_actor(
    authenticated: Annotated[AuthenticatedSession, Depends(get_signed_in_session)],
) -> Actor:
    return build_actor(authenticated.user)
