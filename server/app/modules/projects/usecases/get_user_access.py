from uuid import UUID

from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.modules.projects.domains.user_project_access.entity import UserProjectAccess
from app.modules.projects.errors import UserNotFoundError
from app.modules.users import UserRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class GetUserAccessUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._project_repository = project_repository
        self._project_member_repository = project_member_repository

    async def execute(self, actor: Actor, user_id: UUID) -> list[UserProjectAccess]:
        require_workspace(actor, WorkspaceCapability.USER_ACCESS_VIEW)
        async with self._transaction.begin():
            if await self._user_repository.find_by_id(user_id) is None:
                raise UserNotFoundError
            memberships = await self._project_member_repository.list_for_user(user_id)
            role_by_project_id = {membership.project_id: membership.role for membership in memberships}
            projects = await self._project_repository.list(frozenset(role_by_project_id), is_including_archived=True)
        return [
            UserProjectAccess(
                project_id=project.id,
                project_key=project.key,
                project_name=project.name,
                role=role_by_project_id[project.id],
                is_archived=project.is_archived,
            )
            for project in projects
        ]
