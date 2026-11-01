from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.modules.projects.domains.project_overview.entity import ProjectOverview
from app.modules.projects.utils.effective_role import resolve_effective_role
from app.modules.projects.utils.project_access import build_project_access
from app.modules.projects.utils.visible_projects import select_visible_project_ids
from app.shared.common import Transaction
from app.shared.permissions import Actor


class ListProjectsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
    ) -> None:
        self._transaction = transaction
        self._project_repository = project_repository
        self._project_member_repository = project_member_repository

    async def execute(self, actor: Actor, is_including_archived: bool) -> list[ProjectOverview]:
        async with self._transaction.begin():
            memberships = await self._project_member_repository.list_for_user(actor.user_id)
            role_by_project_id = {membership.project_id: membership.role for membership in memberships}
            visible_project_ids = select_visible_project_ids(actor, frozenset(role_by_project_id))
            projects = await self._project_repository.list(visible_project_ids, is_including_archived)
        return [
            ProjectOverview(
                project=project,
                access=build_project_access(project, resolve_effective_role(actor, role_by_project_id.get(project.id))),
            )
            for project in projects
        ]
