from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_changes.entity import ProjectChanges
from app.modules.projects.domains.project_overview.entity import ProjectOverview
from app.modules.projects.errors import DefaultEnvironmentNotFoundError, ProjectNotLinkedToJiraError
from app.modules.projects.ports.environment_checker import EnvironmentChecker
from app.modules.projects.utils.project_changes import apply_project_changes
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class UpdateProjectUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_repository: ProjectRepository,
        environment_checker: EnvironmentChecker,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_repository = project_repository
        self._environment_checker = environment_checker

    async def execute(self, actor: Actor, key: str, changes: ProjectChanges) -> ProjectOverview:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, key)
            require(access, Capability.PROJECT_EDIT)
            project = await self._project_repository.find_by_id(access.project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.is_linked_to_jira and (
                changes.jira_board_id is not None
                or changes.jira_bug_issue_type is not None
                or changes.jira_post_results is not None
            ):
                raise ProjectNotLinkedToJiraError
            updated_project = apply_project_changes(project, changes)
            if changes.default_environment_id is not None:
                if not await self._environment_checker.is_active_environment(
                    project.id, changes.default_environment_id
                ):
                    raise DefaultEnvironmentNotFoundError
                updated_project = updated_project.model_copy(
                    update={"default_environment_id": changes.default_environment_id}
                )
            elif changes.is_default_environment_cleared:
                updated_project = updated_project.model_copy(update={"default_environment_id": None})
            await self._project_repository.save(updated_project)
        return ProjectOverview(project=updated_project, access=access)
